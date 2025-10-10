#!/usr/bin/env python3
"""
Initialize Production Database
Run this ONCE after deploying to production to set up tables and admin user
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.models.default_settings_model import DefaultSettingsModel
from app.core.default_settings import DEFAULT_THEME, get_default_tool_settings
from datetime import datetime
import uuid


def init_database():
    """Initialize database with tables"""
    print("📊 Creating database tables...")
    
    # Import all models to register them
    from app.models import (
        user, access_request, user_settings,
        default_settings_model, model, look, product
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")


def create_default_settings():
    """Create default settings record"""
    print("\n⚙️  Creating default settings...")
    
    db = SessionLocal()
    try:
        # Check if default settings already exist
        existing = db.query(DefaultSettingsModel).first()
        if existing:
            print("ℹ️  Default settings already exist")
            return
        
        # Create default settings
        defaults = DefaultSettingsModel(
            id=str(uuid.uuid4()),
            default_theme=DEFAULT_THEME,
            default_tool_settings=get_default_tool_settings(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(defaults)
        db.commit()
        print("✅ Default settings created")
        
    finally:
        db.close()


def create_admin_user():
    """Create first admin user"""
    admin_email = os.getenv("FIRST_ADMIN_EMAIL")
    
    if not admin_email:
        print("\n⚠️  FIRST_ADMIN_EMAIL not set in environment")
        print("   Skipping admin user creation")
        return
    
    print(f"\n👤 Creating admin user: {admin_email}")
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"ℹ️  Admin user {admin_email} already exists")
            if existing.role != UserRole.ADMIN:
                existing.role = UserRole.ADMIN
                db.commit()
                print(f"✅ Upgraded {admin_email} to admin")
            return
        
        # Create admin user
        admin = User(
            id=str(uuid.uuid4()),
            email=admin_email,
            full_name="Admin",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        db.add(admin)
        db.commit()
        print(f"✅ Admin user created: {admin_email}")
        print(f"   User ID: {admin.id}")
        
    finally:
        db.close()


def main():
    """Main initialization"""
    print("=" * 70)
    print("🚀 AI Studio - Production Database Initialization")
    print("=" * 70)
    
    # Check if we're in production
    database_url = os.getenv("DATABASE_URL", "")
    if database_url.startswith("sqlite"):
        print("\n⚠️  WARNING: Running on SQLite (development mode)")
        print("   This script is meant for production PostgreSQL")
        response = input("\nContinue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    else:
        print(f"\n✅ PostgreSQL detected: {database_url[:30]}...")
    
    try:
        # Initialize database
        init_database()
        
        # Create default settings
        create_default_settings()
        
        # Create admin user
        create_admin_user()
        
        print("\n" + "=" * 70)
        print("✅ Production database initialized successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Try accessing /health endpoint")
        print("2. Login with admin email to verify OAuth")
        print("3. Check /docs for API documentation")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

