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

router = APIRouter()


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


@router.post("/look-visibility")
async def migrate_look_visibility(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Add visibility column and look_shares table for look sharing feature.
    
    Changes:
    - Add 'visibility' column to looks table (default: 'private')
    - Create 'look_shares' junction table for sharing looks with specific users
    
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
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        has_visibility = column_exists('looks', 'visibility')
        has_look_shares = 'look_shares' in existing_tables
        
        result["current_state"] = {
            "has_visibility_column": has_visibility,
            "has_look_shares_table": has_look_shares
        }
        
        # Check if migration already done
        if has_visibility and has_look_shares:
            result["status"] = "already_migrated"
            result["message"] = "✅ Look visibility migration already completed!"
            return result
        
        # Perform migration
        result["status"] = "migrating"
        
        # Step 1: Add visibility column to looks table
        if not has_visibility:
            # Add column with default value
            db.execute(text(
                "ALTER TABLE looks ADD COLUMN visibility VARCHAR(20) DEFAULT 'private' NOT NULL"
            ))
            db.commit()
            result["steps"].append("✅ Added visibility column to looks table")
            
            # Create index on visibility for faster queries
            try:
                db.execute(text(
                    "CREATE INDEX idx_looks_visibility ON looks(visibility)"
                ))
                db.commit()
                result["steps"].append("✅ Created index on visibility column")
            except Exception as e:
                result["steps"].append(f"⚠️  Index creation skipped (may already exist): {str(e)}")
        else:
            result["steps"].append("⏭️  Skipped visibility column (already exists)")
        
        # Step 2: Create look_shares junction table
        if not has_look_shares:
            # Import look model to ensure look_shares is registered
            from app.models.look import look_shares, Look
            
            # Create the table
            look_shares.create(bind=engine, checkfirst=True)
            result["steps"].append("✅ Created look_shares junction table")
        else:
            result["steps"].append("⏭️  Skipped look_shares table (already exists)")
        
        # Final verification
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        has_visibility_now = column_exists('looks', 'visibility')
        has_look_shares_now = 'look_shares' in existing_tables
        
        if has_visibility_now and has_look_shares_now:
            result["status"] = "success"
            result["message"] = "✅ Look visibility migration completed successfully!"
            result["final_state"] = {
                "visibility_column": "✅ exists",
                "look_shares_table": "✅ exists"
            }
        else:
            result["status"] = "partial"
            result["message"] = "⚠️  Migration partially completed"
            result["final_state"] = {
                "visibility_column": "✅ exists" if has_visibility_now else "❌ missing",
                "look_shares_table": "✅ exists" if has_look_shares_now else "❌ missing"
            }
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )


@router.post("/update-default-settings")
async def update_default_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Update default settings with new fields from hardcoded defaults.
    
    This merges new fields (like stepByStep prompts) into the database defaults
    while preserving any admin customizations.
    
    Safe to run multiple times.
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
        from app.models.default_settings_model import DefaultSettingsModel
        from app.core.default_settings import get_default_tool_settings
        import copy
        
        # Get the database defaults
        db_defaults = db.query(DefaultSettingsModel).first()
        
        if not db_defaults:
            result["status"] = "no_defaults"
            result["message"] = "⚠️  No defaults in database - will use hardcoded defaults"
            return result
        
        # Get the latest hardcoded defaults
        hardcoded_defaults = get_default_tool_settings()
        
        # Deep merge: keep admin customizations, add new fields
        updated_tool_settings = copy.deepcopy(hardcoded_defaults)
        
        result["steps"].append(f"📋 Starting with {len(hardcoded_defaults)} tools from hardcoded defaults")
        
        for tool_name, db_tool_settings in db_defaults.default_tool_settings.items():
            if tool_name in updated_tool_settings:
                # Count fields before merge
                before_count = len(updated_tool_settings[tool_name])
                
                # Merge tool settings
                for key, value in db_tool_settings.items():
                    if isinstance(value, dict) and key in updated_tool_settings[tool_name]:
                        # Merge nested dicts (like sceneDescriptions)
                        updated_tool_settings[tool_name][key] = {**updated_tool_settings[tool_name][key], **value}
                    else:
                        # Override with DB value (admin customization)
                        updated_tool_settings[tool_name][key] = value
                
                after_count = len(updated_tool_settings[tool_name])
                if after_count > before_count:
                    result["steps"].append(f"✅ {tool_name}: Added {after_count - before_count} new field(s)")
                else:
                    result["steps"].append(f"⏭️  {tool_name}: No new fields")
        
        # Update the database
        db_defaults.default_tool_settings = updated_tool_settings
        db.commit()
        
        result["status"] = "success"
        result["message"] = "✅ Default settings updated successfully!"
        result["updated_defaults"] = {
            tool_name: list(settings.keys())
            for tool_name, settings in updated_tool_settings.items()
        }
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )



@router.post("/video-jobs-generate-audio")
async def migrate_video_jobs_generate_audio(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Add generate_audio column to video_jobs table.
    
    This migration adds the generate_audio column for the audio generation feature.
    
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
        # Check if column already exists
        has_generate_audio = column_exists('video_jobs', 'generate_audio')
        
        result["current_state"] = {
            "has_generate_audio": has_generate_audio
        }
        
        # Check if migration already done
        if has_generate_audio:
            result["status"] = "already_migrated"
            result["message"] = "✅ Migration already completed! generate_audio column exists."
            return result
        
        # Perform migration
        result["status"] = "migrating"
        result["steps"].append("Adding generate_audio column...")
        
        # Add generate_audio column
        # Check database type to use correct syntax
        db_url = str(engine.url)
        if 'postgresql' in db_url or 'postgres' in db_url:
            # PostgreSQL
            db.execute(text("ALTER TABLE video_jobs ADD COLUMN generate_audio BOOLEAN DEFAULT FALSE"))
            result["steps"].append("✅ Added generate_audio column (PostgreSQL)")
        else:
            # SQLite
            db.execute(text("ALTER TABLE video_jobs ADD COLUMN generate_audio BOOLEAN DEFAULT 0"))
            result["steps"].append("✅ Added generate_audio column (SQLite)")
        
        db.commit()
        
        # Verify
        has_generate_audio_after = column_exists('video_jobs', 'generate_audio')
        if has_generate_audio_after:
            result["status"] = "success"
            result["message"] = "✅ Migration completed successfully! generate_audio column added."
        else:
            result["status"] = "warning"
            result["message"] = "⚠️ Column might not have been created. Please verify."
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )


@router.post("/video-jobs-request-response-columns")
async def migrate_video_jobs_request_response_columns(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Add request/response tracking columns to video_jobs table.
    
    This migration adds:
    - frontend_request (JSON)
    - veo_request (JSON)
    - veo_response (JSON)
    - backend_response (JSON)
    
    These columns are used for monitoring and debugging video generation jobs.
    
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
        # Check which columns exist
        has_frontend_request = column_exists('video_jobs', 'frontend_request')
        has_veo_request = column_exists('video_jobs', 'veo_request')
        has_veo_response = column_exists('video_jobs', 'veo_response')
        has_backend_response = column_exists('video_jobs', 'backend_response')
        
        result["current_state"] = {
            "has_frontend_request": has_frontend_request,
            "has_veo_request": has_veo_request,
            "has_veo_response": has_veo_response,
            "has_backend_response": has_backend_response
        }
        
        # Check if migration already done
        if has_frontend_request and has_veo_request and has_veo_response and has_backend_response:
            result["status"] = "already_migrated"
            result["message"] = "✅ Migration already completed! All request/response columns exist."
            return result
        
        # Perform migration
        result["status"] = "migrating"
        
        # Check database type
        db_url = str(engine.url)
        is_postgres = 'postgresql' in db_url or 'postgres' in db_url
        
        # Add frontend_request column
        if not has_frontend_request:
            result["steps"].append("Adding frontend_request column...")
            if is_postgres:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN frontend_request JSONB"))
            else:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN frontend_request TEXT"))
            result["steps"].append("✅ Added frontend_request column")
        
        # Add veo_request column
        if not has_veo_request:
            result["steps"].append("Adding veo_request column...")
            if is_postgres:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN veo_request JSONB"))
            else:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN veo_request TEXT"))
            result["steps"].append("✅ Added veo_request column")
        
        # Add veo_response column
        if not has_veo_response:
            result["steps"].append("Adding veo_response column...")
            if is_postgres:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN veo_response JSONB"))
            else:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN veo_response TEXT"))
            result["steps"].append("✅ Added veo_response column")
        
        # Add backend_response column
        if not has_backend_response:
            result["steps"].append("Adding backend_response column...")
            if is_postgres:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN backend_response JSONB"))
            else:
                db.execute(text("ALTER TABLE video_jobs ADD COLUMN backend_response TEXT"))
            result["steps"].append("✅ Added backend_response column")
        
        db.commit()
        
        # Verify
        has_all = (
            column_exists('video_jobs', 'frontend_request') and
            column_exists('video_jobs', 'veo_request') and
            column_exists('video_jobs', 'veo_response') and
            column_exists('video_jobs', 'backend_response')
        )
        
        if has_all:
            result["status"] = "success"
            result["message"] = "✅ Migration completed successfully! All request/response columns added."
        else:
            result["status"] = "warning"
            result["message"] = "⚠️ Some columns might not have been created. Please verify."
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )


@router.post("/video-jobs-all-columns")
async def migrate_video_jobs_all_columns(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Ensure all video_jobs table columns exist.
    
    This migration checks and adds any missing columns that might cause 500 errors.
    
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
        # Check database type
        db_url = str(engine.url)
        is_postgres = 'postgresql' in db_url or 'postgres' in db_url
        
        # List of all columns that should exist
        required_columns = {
            'generate_audio': 'BOOLEAN DEFAULT FALSE',
            'mock_mode': 'BOOLEAN DEFAULT FALSE',
            'frontend_request': 'JSONB',
            'veo_request': 'JSONB',
            'veo_response': 'JSONB',
            'backend_response': 'JSONB',
            'cloudinary_public_id': 'VARCHAR(255)',
            'tokens_consumed': 'INTEGER DEFAULT 50',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'google_operation_name': 'VARCHAR(255)',
            'google_result_uri': 'TEXT',
        }
        
        # For SQLite, use different syntax
        sqlite_types = {
            'generate_audio': 'BOOLEAN DEFAULT 0',
            'mock_mode': 'BOOLEAN DEFAULT 0',
            'frontend_request': 'TEXT',
            'veo_request': 'TEXT',
            'veo_response': 'TEXT',
            'backend_response': 'TEXT',
            'cloudinary_public_id': 'VARCHAR(255)',
            'tokens_consumed': 'INTEGER DEFAULT 50',
            'updated_at': 'TIMESTAMP',
            'google_operation_name': 'VARCHAR(255)',
            'google_result_uri': 'TEXT',
        }
        
        result["current_state"] = {}
        missing_columns = []
        
        # Check each column
        for col_name, col_type in required_columns.items():
            exists = column_exists('video_jobs', col_name)
            result["current_state"][col_name] = exists
            if not exists:
                missing_columns.append(col_name)
        
        if not missing_columns:
            result["status"] = "already_migrated"
            result["message"] = "✅ All columns exist! No migration needed."
            return result
        
        # Perform migration
        result["status"] = "migrating"
        
        for col_name in missing_columns:
            result["steps"].append(f"Adding {col_name} column...")
            
            if is_postgres:
                col_type = required_columns[col_name]
                if 'DEFAULT' in col_type:
                    db.execute(text(f"ALTER TABLE video_jobs ADD COLUMN {col_name} {col_type}"))
                else:
                    db.execute(text(f"ALTER TABLE video_jobs ADD COLUMN {col_name} {col_type}"))
            else:
                col_type = sqlite_types.get(col_name, 'TEXT')
                db.execute(text(f"ALTER TABLE video_jobs ADD COLUMN {col_name} {col_type}"))
            
            result["steps"].append(f"✅ Added {col_name} column")
        
        db.commit()
        
        # Verify all columns exist
        all_exist = all(column_exists('video_jobs', col) for col in required_columns.keys())
        
        if all_exist:
            result["status"] = "success"
            result["message"] = f"✅ Migration completed successfully! Added {len(missing_columns)} column(s)."
        else:
            result["status"] = "warning"
            result["message"] = "⚠️ Some columns might not have been created. Please verify."
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )

@router.post("/video-jobs-mock-mode")
async def migrate_video_jobs_mock_mode(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **ADMIN ONLY**: Add mock_mode column to video_jobs table.
    
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
        "errors": [],
        "current_state": {}
    }
    
    try:
        # Check database type
        db_url = str(engine.url)
        is_postgres = 'postgresql' in db_url or 'postgres' in db_url
        
        # Check if mock_mode column exists
        exists = column_exists('video_jobs', 'mock_mode')
        result["current_state"]["mock_mode"] = exists
        
        if exists:
            result["status"] = "already_migrated"
            result["message"] = "✅ mock_mode column already exists! No migration needed."
            return result
        
        # Perform migration
        result["status"] = "migrating"
        result["steps"].append("Adding mock_mode column...")
        
        if is_postgres:
            db.execute(text("ALTER TABLE video_jobs ADD COLUMN mock_mode BOOLEAN DEFAULT FALSE"))
        else:
            db.execute(text("ALTER TABLE video_jobs ADD COLUMN mock_mode BOOLEAN DEFAULT 0"))
        
        db.commit()
        result["steps"].append("✅ Added mock_mode column")
        
        # Verify
        if column_exists('video_jobs', 'mock_mode'):
            result["status"] = "success"
            result["message"] = "✅ Migration completed successfully! mock_mode column added."
        else:
            result["status"] = "error"
            result["message"] = "⚠️  Column added but verification failed"
        
        return result
        
    except Exception as e:
        db.rollback()
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"❌ Migration failed: {str(e)}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )
