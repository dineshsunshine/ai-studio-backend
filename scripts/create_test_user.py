#!/usr/bin/env python3
"""
Script to create a test user in the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

def create_test_user():
    """Create a test user"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if existing_user:
            print("❌ Test user already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Username: {existing_user.username}")
            return
        
        # Create test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            is_superuser=False
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ Test user created successfully!")
        print("=" * 60)
        print(f"📧 Email:    test@example.com")
        print(f"👤 Username: testuser")
        print(f"🔑 Password: testpassword123")
        print("=" * 60)
        print(f"🆔 User ID:  {test_user.id}")
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()


