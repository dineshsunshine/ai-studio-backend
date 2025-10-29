"""
User Settings Endpoints
Manages user-specific application settings (theme + tool settings)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.default_settings import get_current_defaults
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
        db.refresh(user_settings)
    
    return user_settings


@router.get("/", response_model=UserSettingsData)
@router.get("", response_model=UserSettingsData)
async def get_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user settings.
    
    Returns the user's customized settings (theme + tool settings). 
    If no settings exist yet, automatically creates and returns default settings.
    Settings are merged with current defaults to ensure all new fields are present.
    
    Returns:
        UserSettingsData: Complete user settings object with theme and toolSettings
    """
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Merge user settings with current defaults to ensure all fields are present
    # This handles cases where new fields are added to the schema
    current_defaults = get_current_defaults(db)
    
    # Deep merge tool settings
    merged_tool_settings = current_defaults["toolSettings"].copy()
    for tool_name, tool_settings in user_settings.tool_settings.items():
        if tool_name in merged_tool_settings:
            # Merge tool-specific settings
            merged_tool_settings[tool_name] = {**merged_tool_settings[tool_name], **tool_settings}
        else:
            merged_tool_settings[tool_name] = tool_settings
    
    # Return settings object with merged values
    return UserSettingsData(
        theme=user_settings.theme,
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
    
    Replaces the user's entire settings (theme + tool settings) with the provided data.
    The frontend should send the complete settings object.
    
    Body:
        UserSettingsData: Complete settings object with theme and toolSettings
    
    Returns:
        UserSettingsData: The updated settings object
    """
    # Get or create user settings
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Update theme and tool settings
    user_settings.theme = settings.theme
    user_settings.tool_settings = settings.toolSettings.model_dump()
    
    db.commit()
    db.refresh(user_settings)
    
    # Return the updated settings
    return UserSettingsData(
        theme=user_settings.theme,
        toolSettings=user_settings.tool_settings
    )


@router.post("/reset", response_model=UserSettingsData)
async def reset_user_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reset user settings to defaults.
    
    Overwrites the user's settings with the application's default values
    (default theme and default tool settings).
    
    Returns:
        UserSettingsData: The default settings object
    """
    # Get or create user settings
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    # Get current admin-configurable defaults from database
    current_defaults = get_current_defaults(db)
    
    # Reset to current defaults
    user_settings.theme = current_defaults["theme"]
    user_settings.tool_settings = current_defaults["toolSettings"]
    
    db.commit()
    db.refresh(user_settings)
    
    # Return the default settings
    return UserSettingsData(
        theme=user_settings.theme,
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
        UserSettingsResponse: Settings with metadata (theme, toolSettings, updatedAt)
    """
    user_settings = get_or_create_user_settings(str(current_user.id), db)
    
    return UserSettingsResponse(
        theme=user_settings.theme,
        toolSettings=user_settings.tool_settings,
        updatedAt=user_settings.updated_at.isoformat()
    )

