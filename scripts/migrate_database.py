"""
Database migration script for user management system.

This script will:
1. Back up the existing database
2. Drop all tables
3. Recreate all tables with new schema
4. Migrate existing data if possible

⚠️ WARNING: This will drop all existing tables!
Make sure to backup your data before running this script.
"""
import os
import sys
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from app.core.database import engine, Base
from app.models import user, access_request, model, look, product


def backup_database():
    """Backup the existing database"""
    db_path = "ai_studio.db"
    if os.path.exists(db_path):
        backup_path = f"ai_studio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    else:
        print("ℹ️  No existing database found. Starting fresh.")
        return None


def drop_all_tables():
    """Drop all existing tables"""
    print("\n🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")


def create_all_tables():
    """Create all tables with new schema"""
    print("\n📊 Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n✅ Created {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
    
    return tables


def main():
    """Main migration function"""
    print("\n" + "="*70)
    print("DATABASE MIGRATION - User Management System")
    print("="*70)
    
    print("\n⚠️  WARNING: This will drop all existing tables!")
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return
    
    try:
        # Step 1: Backup
        print("\n" + "-"*70)
        print("STEP 1: Backup")
        print("-"*70)
        backup_path = backup_database()
        
        # Step 2: Drop tables
        print("\n" + "-"*70)
        print("STEP 2: Drop existing tables")
        print("-"*70)
        drop_all_tables()
        
        # Step 3: Create new tables
        print("\n" + "-"*70)
        print("STEP 3: Create tables with new schema")
        print("-"*70)
        tables = create_all_tables()
        
        # Summary
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETE!")
        print("="*70)
        
        if backup_path:
            print(f"\n📁 Backup: {backup_path}")
        
        print(f"\n📊 New tables created:")
        for table in tables:
            print(f"   ✅ {table}")
        
        print("\n💡 Next steps:")
        print("   1. Run: python scripts/create_admin.py")
        print("   2. Update your .env file with Google OAuth credentials")
        print("   3. Start the backend: python api_with_db_and_ngrok.py")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if backup_path:
            print(f"\n💡 Restore from backup: {backup_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()

