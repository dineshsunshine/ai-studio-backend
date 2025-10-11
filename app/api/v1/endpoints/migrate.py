"""
One-time migration endpoint for production database.
This endpoint can be safely deleted after migration is complete.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.core.database import get_db, engine
from app.models.user import User, UserRole
from app.core.auth import get_current_active_user

router = APIRouter(prefix="/migrate", tags=["migration"])


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception:
        return False


@router.post("/links-columns")
async def migrate_links_columns(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Migrate links table columns from old names to new names.
    
    Changes:
    - client_name → title
    - client_phone → description
    
    This endpoint is safe to call multiple times.
    """
    
    # Only admins can run migrations
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can run migrations"
        )
    
    result = {
        "status": "checking",
        "steps": [],
        "errors": []
    }
    
    try:
        # Check current state
        has_client_name = column_exists('links', 'client_name')
        has_client_phone = column_exists('links', 'client_phone')
        has_title = column_exists('links', 'title')
        has_description = column_exists('links', 'description')
        
        result["current_state"] = {
            "has_client_name": has_client_name,
            "has_client_phone": has_client_phone,
            "has_title": has_title,
            "has_description": has_description
        }
        
        # Check if migration already done
        if has_title and has_description and not has_client_name and not has_client_phone:
            result["status"] = "already_migrated"
            result["message"] = "✅ Migration already completed! Database is up to date."
            return result
        
        # Check if we can migrate
        if not has_client_name or not has_client_phone:
            result["status"] = "error"
            result["message"] = "❌ Old columns not found. Database might be in unexpected state."
            return result
        
        # Perform migration
        result["status"] = "migrating"
        
        # Step 1: Rename client_name to title
        if has_client_name and not has_title:
            db.execute(text("ALTER TABLE links RENAME COLUMN client_name TO title"))
            db.commit()
            result["steps"].append("✅ Renamed client_name → title")
        else:
            result["steps"].append("⏭️  Skipped client_name → title (already done)")
        
        # Step 2: Rename client_phone to description
        if has_client_phone and not has_description:
            db.execute(text("ALTER TABLE links RENAME COLUMN client_phone TO description"))
            db.commit()
            result["steps"].append("✅ Renamed client_phone → description")
        else:
            result["steps"].append("⏭️  Skipped client_phone → description (already done)")
        
        # Step 3: Make description nullable
        try:
            db.execute(text("ALTER TABLE links ALTER COLUMN description DROP NOT NULL"))
            db.commit()
            result["steps"].append("✅ Made description column nullable")
        except Exception as e:
            if "does not exist" in str(e).lower():
                result["steps"].append("⏭️  description already nullable or doesn't exist")
            else:
                result["steps"].append(f"⚠️  Could not alter description: {str(e)}")
        
        # Step 4: Add cover_image_url column if it doesn't exist
        has_cover_image = column_exists('links', 'cover_image_url')
        if not has_cover_image:
            db.execute(text("ALTER TABLE links ADD COLUMN cover_image_url VARCHAR NULL"))
            db.commit()
            result["steps"].append("✅ Added cover_image_url column")
        else:
            result["steps"].append("⏭️  cover_image_url column already exists")
        
        # Verify final state
        has_title_final = column_exists('links', 'title')
        has_description_final = column_exists('links', 'description')
        has_client_name_final = column_exists('links', 'client_name')
        has_client_phone_final = column_exists('links', 'client_phone')
        
        result["final_state"] = {
            "has_title": has_title_final,
            "has_description": has_description_final,
            "has_client_name": has_client_name_final,
            "has_client_phone": has_client_phone_final
        }
        
        # Count links
        count_result = db.execute(text("SELECT COUNT(*) FROM links"))
        count = count_result.fetchone()[0]
        result["total_links"] = count
        
        result["status"] = "success"
        result["message"] = f"✅ Migration completed successfully! {count} links migrated."
        
        return result
        
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"❌ Migration failed: {str(e)}"
        result["errors"].append(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )


@router.get("/status")
async def check_migration_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Check the current state of the links table columns.
    """
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can check migration status"
        )
    
    has_client_name = column_exists('links', 'client_name')
    has_client_phone = column_exists('links', 'client_phone')
    has_title = column_exists('links', 'title')
    has_description = column_exists('links', 'description')
    
    migrated = has_title and has_description and not has_client_name and not has_client_phone
    needs_migration = has_client_name or has_client_phone
    
    return {
        "columns": {
            "client_name": has_client_name,
            "client_phone": has_client_phone,
            "title": has_title,
            "description": has_description
        },
        "migrated": migrated,
        "needs_migration": needs_migration,
        "status": "✅ Up to date" if migrated else "⚠️ Migration needed"
    }

