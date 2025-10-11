#!/usr/bin/env python3
"""
Migration script to rename columns in the links table for production (PostgreSQL).
This script is safe to run multiple times - it checks if columns exist before migrating.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text, inspect
from app.core.database import engine

def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_links_table():
    """Migrate the links table from old column names to new ones"""
    
    print("\n" + "="*70)
    print("PRODUCTION DATABASE MIGRATION: Links Table")
    print("="*70 + "\n")
    
    with engine.connect() as conn:
        # Check current state
        has_client_name = column_exists('links', 'client_name')
        has_client_phone = column_exists('links', 'client_phone')
        has_title = column_exists('links', 'title')
        has_description = column_exists('links', 'description')
        
        print("Current state:")
        print(f"  - client_name column exists: {has_client_name}")
        print(f"  - client_phone column exists: {has_client_phone}")
        print(f"  - title column exists: {has_title}")
        print(f"  - description column exists: {has_description}")
        print()
        
        if has_title and has_description and not has_client_name and not has_client_phone:
            print("✅ Migration already completed! Database is up to date.")
            return
        
        if not has_client_name or not has_client_phone:
            print("❌ ERROR: Old columns (client_name, client_phone) not found!")
            print("   The database might be in an unexpected state.")
            print("   Please check manually.")
            return
        
        # PostgreSQL supports RENAME COLUMN directly
        print("Starting migration...")
        print()
        
        # Step 1: Rename client_name to title
        if has_client_name and not has_title:
            print("1. Renaming client_name → title...")
            conn.execute(text("ALTER TABLE links RENAME COLUMN client_name TO title"))
            conn.commit()
            print("   ✅ Done")
        else:
            print("1. Skipping client_name → title (already done)")
        
        # Step 2: Rename client_phone to description
        if has_client_phone and not has_description:
            print("2. Renaming client_phone → description...")
            conn.execute(text("ALTER TABLE links RENAME COLUMN client_phone TO description"))
            conn.commit()
            print("   ✅ Done")
        else:
            print("2. Skipping client_phone → description (already done)")
        
        # Step 3: Make description nullable if it's not (PostgreSQL might have it as NOT NULL)
        print("3. Ensuring description is nullable...")
        conn.execute(text("ALTER TABLE links ALTER COLUMN description DROP NOT NULL"))
        conn.commit()
        print("   ✅ Done")
        
        print()
        print("="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*70)
        print()
        
        # Verify final state
        has_title_final = column_exists('links', 'title')
        has_description_final = column_exists('links', 'description')
        has_client_name_final = column_exists('links', 'client_name')
        has_client_phone_final = column_exists('links', 'client_phone')
        
        print("Final state:")
        print(f"  ✓ title column exists: {has_title_final}")
        print(f"  ✓ description column exists: {has_description_final}")
        print(f"  ✓ client_name column removed: {not has_client_name_final}")
        print(f"  ✓ client_phone column removed: {not has_client_phone_final}")
        print()
        
        # Count links
        result = conn.execute(text("SELECT COUNT(*) FROM links"))
        count = result.fetchone()[0]
        print(f"Total links in database: {count}")
        print()

if __name__ == "__main__":
    try:
        migrate_links_table()
    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        print("\nPlease check the error message and database state.")
        sys.exit(1)

