"""
User Settings Endpoints
Manages user-specific application settings (theme + tool settings + branding)
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.default_settings import get_current_defaults
from app.core.storage import StorageService
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.settings import UserSettingsData, UserSettingsResponse


router = APIRouter()


def get_or_create_user_settings(user_id: str, db: Session) -> UserSettings:
    """
    Get user settings, creating with defaults if not exists
    """
    # Ensure user_id is a string
    user_id_str = str(user_id)
    user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id_str).first()
    
    if not user_settings:
        # Get current admin-configurable defaults from database
        current_defaults = get_current_defaults(db)
        # Create new settings with defaults
        user_settings = UserSettings(
            user_id=user_id_str,
            theme=current_defaults["theme"],
            tool_settings=current_defaults["toolSettings"]
        )
        db.add(user_settings)
        db.commit()

    
    return user_settings


@router.get("/", response_model=UserSettingsData)
@router.get("", response_model=UserSettingsData)
async def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user settings.
    
    Returns the user's customized settings (theme + tool settings + branding). 
    If no settings exist yet, automatically creates and returns default settings.
    Settings are merged with current defaults to ensure all new fields are present.
    
    Returns:
        UserSettingsData: Complete user settings object with theme, toolSettings, and companyLogoUrl
    """
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Merge user settings with current defaults to ensure all fields are present
    # This handles cases where new fields are added to the schema
    current_defaults = get_current_defaults(db)
    
    # Deep merge tool settings - ensure defaults come first, then override with user values
    import copy
    merged_tool_settings = copy.deepcopy(current_defaults["toolSettings"])
    
    # Merge each tool's settings
    for tool_name, user_tool_settings in user_settings.tool_settings.items():
        if tool_name in merged_tool_settings:
            # Deep merge: start with defaults, override with user values
            default_tool_settings = merged_tool_settings[tool_name]
            
            # For nested objects like sceneDescriptions, we need to merge recursively
            for key, value in user_tool_settings.items():
                if isinstance(value, dict) and key in default_tool_settings and isinstance(default_tool_settings[key], dict):
                    # Merge nested dictionaries
                    merged_tool_settings[tool_name][key] = {**default_tool_settings[key], **value}
                else:
                    # Override with user value
                    merged_tool_settings[tool_name][key] = value
        else:
            # New tool not in defaults - just use user settings
            merged_tool_settings[tool_name] = user_tool_settings
    
    # Return settings object with merged values
    return UserSettingsData(
        theme=user_settings.theme,
        companyLogoUrl=user_settings.company_logo_url,
        toolSettings=merged_tool_settings
    )


@router.put("/", response_model=UserSettingsData)
@router.put("", response_model=UserSettingsData)
async def update_user_settings(
    settings: UserSettingsData,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user settings.
    
    Replaces the user's entire settings (theme + tool settings + branding) with the provided data.
    The frontend should send the complete settings object.
    
    Body:
        UserSettingsData: Complete settings object with theme, toolSettings, and companyLogoUrl
    
    Returns:
        UserSettingsData: The updated settings object
    """
    # Get or create user settings
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Update theme and tool settings
    user_settings.theme = settings.theme
    user_settings.tool_settings = settings.toolSettings.model_dump()
    user_settings.company_logo_url = settings.companyLogoUrl
    
    db.commit()
    db.refresh(user_settings)
    
    # Return the updated settings
    return UserSettingsData(
        theme=user_settings.theme,
        companyLogoUrl=user_settings.company_logo_url,
        toolSettings=user_settings.tool_settings
    )


@router.post("/reset", response_model=UserSettingsData)
async def reset_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    current_defaults = get_current_defaults(db)
    
    user_settings.theme = current_defaults["theme"]
    user_settings.tool_settings = current_defaults["toolSettings"]
    
    db.commit()
    db.refresh(user_settings)
    
    return UserSettingsData(
        theme=user_settings.theme,
        companyLogoUrl=user_settings.company_logo_url,
        toolSettings=user_settings.tool_settings
    )


@router.get("/info", response_model=UserSettingsResponse)
async def get_user_settings_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user settings with metadata.
    
    Returns the user's settings along with metadata like last updated time.
    
    Returns:
        UserSettingsResponse: Settings with metadata (theme, toolSettings, companyLogoUrl, updatedAt)
    """
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    return UserSettingsResponse(
        theme=user_settings.theme,
        companyLogoUrl=user_settings.company_logo_url,
        toolSettings=user_settings.tool_settings,
        updatedAt=user_settings.updated_at.isoformat()
    )


@router.put("/logo", response_model=dict)
async def upload_company_logo(
    logo_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload or update company logo.
    
    Uploads a company logo image and stores the URL in user settings.
    The logo will be displayed on sharable links for branding.
    
    Args:
        logo_file: Image file (PNG, JPG, WebP)
    
    Returns:
        {
            "companyLogoUrl": "https://...",
            "message": "Logo uploaded successfully"
        }
    """
    # Get or create user settings
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/webp", "image/gif"]
    if logo_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Delete old logo if exists
    if user_settings.company_logo_url:
        try:
            storage = StorageService()
            # Extract public_id from URL if it's a Cloudinary URL
            if "cloudinary" in user_settings.company_logo_url:
                # Cloudinary URL format: .../ai_studio/logos/{public_id}
                parts = user_settings.company_logo_url.split("/")
                if len(parts) > 0:
                    public_id = f"ai_studio/logos/{parts[-1].split('.')[0]}"
                    storage.delete_file(public_id)
        except Exception as e:
            print(f"Warning: Could not delete old logo: {str(e)}")
    
    # Upload new logo
    storage = StorageService()
    logo_url = storage.upload_file(
        logo_file.file,
        f"logo_{current_user.id}",
        logo_file.content_type,
        folder="logos"
    )
    
    # Update user settings
    user_settings.company_logo_url = logo_url
    db.commit()
    db.refresh(user_settings)
    
    return {
        "companyLogoUrl": logo_url,
        "message": "Logo uploaded successfully"
    }


@router.delete("/logo", response_model=dict)
async def delete_company_logo(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete company logo.
    
    Removes the company logo from user settings.
    
    Returns:
        {
            "message": "Logo deleted successfully",
            "companyLogoUrl": null
        }
    """
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Delete from storage
    if user_settings.company_logo_url:
        try:
            storage = StorageService()
            if "cloudinary" in user_settings.company_logo_url:
                parts = user_settings.company_logo_url.split("/")
                if len(parts) > 0:
                    public_id = f"ai_studio/logos/{parts[-1].split('.')[0]}"
                    storage.delete_file(public_id)
        except Exception as e:
            print(f"Warning: Could not delete logo from storage: {str(e)}")
    
    # Update user settings
    user_settings.company_logo_url = None
    db.commit()
    db.refresh(user_settings)
    
    return {
        "message": "Logo deleted successfully",
        "companyLogoUrl": None
    }

