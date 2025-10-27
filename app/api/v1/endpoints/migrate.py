"""
One-time migration endpoint for production database.
This endpoint can be safely deleted after migration is complete.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.core.database import get_db, engine, Base
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
        has_cover_image_url = column_exists('links', 'cover_image_url')
        
        result["current_state"] = {
            "has_client_name": has_client_name,
            "has_client_phone": has_client_phone,
            "has_title": has_title,
            "has_description": has_description,
            "has_cover_image_url": has_cover_image_url
        }
        
        # Check if migration already done (all new columns exist, no old columns)
        if has_title and has_description and has_cover_image_url and not has_client_name and not has_client_phone:
            result["status"] = "already_migrated"
            result["message"] = "✅ Migration already completed! Database is up to date."
            return result
        
        # Perform migration (handle partial migrations gracefully)
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
        if not has_cover_image_url:
            db.execute(text("ALTER TABLE links ADD COLUMN cover_image_url VARCHAR NULL"))
            db.commit()
            result["steps"].append("✅ Added cover_image_url column")
        else:
            result["steps"].append("⏭️  cover_image_url column already exists")
        
        # Step 5: Check and add position column to link_looks if missing
        has_position = False
        try:
            from sqlalchemy import inspect as sqla_inspect
            inspector = sqla_inspect(db.bind)
            link_looks_cols = [col['name'] for col in inspector.get_columns('link_looks')]
            has_position = 'position' in link_looks_cols
        except Exception:
            has_position = False
        
        if not has_position:
            try:
                # Add position column with default value
                db.execute(text("ALTER TABLE link_looks ADD COLUMN position INTEGER NOT NULL DEFAULT 0"))
                db.commit()
                result["steps"].append("✅ Added position column to link_looks")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    result["steps"].append("⏭️  position column already exists in link_looks")
                else:
                    result["steps"].append(f"⚠️  Could not add position column: {str(e)}")
        else:
            result["steps"].append("⏭️  position column already exists in link_looks")
        
        # Verify final state
        has_title_final = column_exists('links', 'title')
        has_description_final = column_exists('links', 'description')
        has_client_name_final = column_exists('links', 'client_name')
        has_client_phone_final = column_exists('links', 'client_phone')
        
        has_cover_image_url_final = column_exists('links', 'cover_image_url')
        
        result["final_state"] = {
            "has_title": has_title_final,
            "has_description": has_description_final,
            "has_cover_image_url": has_cover_image_url_final,
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


@router.post("/create-subscription-tables")
async def create_subscription_tables(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Create subscription tables (user_subscriptions, token_transactions).
    
    This endpoint is safe to call multiple times - it will only create tables if they don't exist.
    """
    
    # Only admins can run migrations
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can run migrations"
        )
    
    result = {
        "status": "checking",
        "steps": []
    }
    
    try:
        # Check if tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        has_user_subscriptions = 'user_subscriptions' in existing_tables
        has_token_transactions = 'token_transactions' in existing_tables
        
        if has_user_subscriptions and has_token_transactions:
            result["status"] = "already_exists"
            result["message"] = "✅ Subscription tables already exist"
            result["tables"] = {
                "user_subscriptions": "exists",
                "token_transactions": "exists"
            }
            return result
        
        # Import subscription models to register them with SQLAlchemy
        from app.models.subscription import UserSubscription, TokenTransaction
        
        # Create only subscription tables
        result["steps"].append("Importing subscription models...")
        
        # Create tables using SQLAlchemy metadata
        result["steps"].append("Creating subscription tables...")
        
        # Get subscription tables from metadata
        subscription_tables = []
        for table_name, table in Base.metadata.tables.items():
            if table_name in ['user_subscriptions', 'token_transactions']:
                subscription_tables.append(table)
        
        # Create tables
        for table in subscription_tables:
            table.create(bind=engine, checkfirst=True)
            result["steps"].append(f"✅ Created table: {table.name}")
        
        # Verify tables were created
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        result["status"] = "success"
        result["message"] = "✅ Subscription tables created successfully"
        result["tables"] = {
            "user_subscriptions": "created" if 'user_subscriptions' in existing_tables else "failed",
            "token_transactions": "created" if 'token_transactions' in existing_tables else "failed"
        }
        
        return result
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )

