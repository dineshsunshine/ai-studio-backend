"""
Bootstrap endpoint for initial admin user creation
This endpoint can only be used when no admin users exist in the system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.user_settings import UserSettings
from app.core.default_settings import get_current_defaults
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/create-first-admin")
async def create_first_admin(
    email: str,
    full_name: str = "Admin",
    db: Session = Depends(get_db)
):
    """
    Create the first admin user in the system.
    
    This endpoint can ONLY be used when NO admin users exist.
    Once an admin exists, this endpoint will be disabled for security.
    
    Parameters:
    - email: Email address of the admin user
    - full_name: Full name of the admin user (default: "Admin")
    
    Returns:
    - Created admin user details
    """
    # Check if any admin users already exist
    existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already exists. This endpoint is disabled for security. Use the admin panel to manage users."
        )
    
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        # Upgrade existing user to admin
        existing_user.role = UserRole.ADMIN
        existing_user.status = UserStatus.ACTIVE
        existing_user.full_name = full_name
        existing_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_user)
        
        # Ensure user has settings
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == str(existing_user.id)).first()
        if not user_settings:
            current_defaults = get_current_defaults(db)
            user_settings = UserSettings(
                user_id=str(existing_user.id),
                theme=current_defaults["theme"],
                tool_settings=current_defaults["toolSettings"]
            )
            db.add(user_settings)
            db.commit()
        
        return {
            "status": "success",
            "message": f"User {email} upgraded to admin",
            "user": {
                "id": str(existing_user.id),
                "email": existing_user.email,
                "full_name": existing_user.full_name,
                "role": existing_user.role,
                "status": existing_user.status
            }
        }
    
    # Create new admin user
    new_admin = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name=full_name,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    # Create default settings for the admin
    current_defaults = get_current_defaults(db)
    user_settings = UserSettings(
        user_id=str(new_admin.id),
        theme=current_defaults["theme"],
        tool_settings=current_defaults["toolSettings"]
    )
    db.add(user_settings)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Admin user {email} created successfully",
        "user": {
            "id": str(new_admin.id),
            "email": new_admin.email,
            "full_name": new_admin.full_name,
            "role": new_admin.role,
            "status": new_admin.status
        }
    }


