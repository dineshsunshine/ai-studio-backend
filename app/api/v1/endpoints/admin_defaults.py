"""
Admin endpoints for managing default settings
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_admin
from app.core.default_settings import get_default_settings, get_default_tool_settings, DEFAULT_THEME
from app.models.user import User
from app.models.user_settings import UserSettings
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


@router.put("/defaults")
async def update_admin_defaults(
    settings: DefaultSettingsData,
    apply_to_all: bool = Query(False, description="Apply these settings to all existing users"),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update default settings (admin only).
    
    This will change:
    - Default theme for new users
    - Default tool settings for new users
    - Settings that users get when they reset
    
    Query Parameters:
        apply_to_all: If true, applies these settings to ALL existing users immediately.
                     If false (default), only affects new users and reset operations.
    
    Body:
        DefaultSettingsData: New default theme and tool settings
    
    Returns:
        Updated defaults with metadata and count of affected users
    """
    defaults = get_or_create_default_settings(db)
    
    # Update the defaults
    defaults.default_theme = settings.defaultTheme
    defaults.default_tool_settings = settings.defaultToolSettings.model_dump()
    defaults.updated_by = str(current_admin.id)
    
    db.commit()
    db.refresh(defaults)
    
    affected_users = 0
    
    # If apply_to_all is true, update all existing users' settings
    if apply_to_all:
        all_user_settings = db.query(UserSettings).all()
        for user_setting in all_user_settings:
            user_setting.theme = defaults.default_theme
            user_setting.tool_settings = defaults.default_tool_settings
            affected_users += 1
        db.commit()
    
    response_data = {
        "defaultTheme": defaults.default_theme,
        "defaultToolSettings": defaults.default_tool_settings,
        "updatedAt": defaults.updated_at.isoformat(),
        "updatedBy": defaults.updated_by,
        "affectedUsers": affected_users
    }
    
    return response_data


@router.post("/defaults/apply-to-all")
async def apply_defaults_to_all_users(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Apply current default settings to ALL existing users (admin only).
    
    This will overwrite all users' settings with the current default settings.
    Use this carefully as it will override any customizations users have made.
    
    Returns:
        Count of affected users and default settings applied
    """
    defaults = get_or_create_default_settings(db)
    
    # Update all existing users' settings
    all_user_settings = db.query(UserSettings).all()
    affected_users = 0
    
    for user_setting in all_user_settings:
        user_setting.theme = defaults.default_theme
        user_setting.tool_settings = defaults.default_tool_settings
        affected_users += 1
    
    db.commit()
    
    return {
        "status": "success",
        "message": f"Applied default settings to {affected_users} users",
        "affectedUsers": affected_users,
        "appliedSettings": {
            "defaultTheme": defaults.default_theme,
            "defaultToolSettings": defaults.default_tool_settings
        }
    }


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


