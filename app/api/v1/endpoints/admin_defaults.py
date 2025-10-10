"""
Admin endpoints for managing default settings
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_admin
from app.core.default_settings import get_default_settings, get_default_tool_settings, DEFAULT_THEME
from app.models.user import User
from app.models.default_settings_model import DefaultSettingsModel
from app.schemas.default_settings_schema import DefaultSettingsData, DefaultSettingsResponse


router = APIRouter()


def get_or_create_default_settings(db: Session) -> DefaultSettingsModel:
    """
    Get the singleton default settings record, create if not exists
    """
    default_settings = db.query(DefaultSettingsModel).first()
    
    if not default_settings:
        # Create with hardcoded defaults from code
        default_settings = DefaultSettingsModel(
            default_theme=DEFAULT_THEME,
            default_tool_settings=get_default_tool_settings()
        )
        db.add(default_settings)
        db.commit()
        db.refresh(default_settings)
    
    return default_settings


@router.get("/defaults", response_model=DefaultSettingsResponse)
async def get_admin_defaults(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get current default settings that new users will receive (admin only).
    
    These are the settings that will be automatically assigned to:
    - Newly approved users
    - Users who reset their settings
    
    Returns:
        DefaultSettingsResponse: Current default theme and tool settings
    """
    defaults = get_or_create_default_settings(db)
    
    return DefaultSettingsResponse(
        defaultTheme=defaults.default_theme,
        defaultToolSettings=defaults.default_tool_settings,
        updatedAt=defaults.updated_at.isoformat(),
        updatedBy=defaults.updated_by
    )


@router.put("/defaults", response_model=DefaultSettingsResponse)
async def update_admin_defaults(
    settings: DefaultSettingsData,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update default settings for new users (admin only).
    
    This will change:
    - Default theme for new users
    - Default tool settings for new users
    - Settings that users get when they reset
    
    IMPORTANT: This does NOT affect existing users' settings.
    Only new users and reset operations will use these defaults.
    
    Body:
        DefaultSettingsData: New default theme and tool settings
    
    Returns:
        DefaultSettingsResponse: Updated defaults with metadata
    """
    defaults = get_or_create_default_settings(db)
    
    # Update the defaults
    defaults.default_theme = settings.defaultTheme
    defaults.default_tool_settings = settings.defaultToolSettings.model_dump()
    defaults.updated_by = str(current_admin.id)
    
    db.commit()
    db.refresh(defaults)
    
    return DefaultSettingsResponse(
        defaultTheme=defaults.default_theme,
        defaultToolSettings=defaults.default_tool_settings,
        updatedAt=defaults.updated_at.isoformat(),
        updatedBy=defaults.updated_by
    )


@router.post("/defaults/reset", response_model=DefaultSettingsResponse)
async def reset_admin_defaults(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reset default settings to hardcoded system defaults (admin only).
    
    This restores the default settings to the original values
    defined in the codebase.
    
    Returns:
        DefaultSettingsResponse: Reset defaults
    """
    defaults = get_or_create_default_settings(db)
    
    # Reset to hardcoded defaults from code
    defaults.default_theme = DEFAULT_THEME
    defaults.default_tool_settings = get_default_tool_settings()
    defaults.updated_by = str(current_admin.id)
    
    db.commit()
    db.refresh(defaults)
    
    return DefaultSettingsResponse(
        defaultTheme=defaults.default_theme,
        defaultToolSettings=defaults.default_tool_settings,
        updatedAt=defaults.updated_at.isoformat(),
        updatedBy=defaults.updated_by
    )

