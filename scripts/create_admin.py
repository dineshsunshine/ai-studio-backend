"""
Script to create the first admin user.

This script creates an admin user that can:
- Approve/reject access requests
- Manage all users
- Access all models and looks
"""
import os
import sys
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.models.user import User, UserRole, UserStatus
from app.core.config import settings


def create_admin_user(
    email: str,
    full_name: str,
    google_id: str = None
):
    """
    Create an admin user.
    
    Args:
        email: Admin email address
        full_name: Full name of the admin
        google_id: Optional Google ID if using OAuth
    """
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == email).first()
        
        if existing_admin:
            print(f"\n⚠️  User with email {email} already exists!")
            print(f"   Role: {existing_admin.role.value}")
            print(f"   Status: {existing_admin.status.value}")
            
            if existing_admin.role != UserRole.ADMIN:
                response = input("\nPromote this user to admin? (yes/no): ")
                if response.lower() == "yes":
                    existing_admin.role = UserRole.ADMIN
                    existing_admin.status = UserStatus.ACTIVE
                    db.commit()
                    print(f"✅ User {email} promoted to admin!")
                else:
                    print("❌ Operation cancelled")
            else:
                print("✅ User is already an admin")
            
            return existing_admin
        
        # Create new admin user
        admin_user = User(
            email=email,
            google_id=google_id,
            full_name=full_name,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"\n👤 Admin Details:")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.full_name}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   Status: {admin_user.status.value}")
        print(f"   ID: {admin_user.id}")
        
        return admin_user
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function"""
    print("\n" + "="*70)
    print("CREATE ADMIN USER")
    print("="*70)
    
    # Check if FIRST_ADMIN_EMAIL is set in config
    if settings.FIRST_ADMIN_EMAIL:
        print(f"\nℹ️  Using admin email from config: {settings.FIRST_ADMIN_EMAIL}")
        email = settings.FIRST_ADMIN_EMAIL
    else:
        email = input("\nEnter admin email: ").strip()
        
        if not email:
            print("❌ Email is required")
            sys.exit(1)
    
    full_name = input("Enter admin full name: ").strip()
    if not full_name:
        full_name = "Admin User"
    
    print(f"\n📝 Creating admin user:")
    print(f"   Email: {email}")
    print(f"   Name: {full_name}")
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Operation cancelled")
        return
    
    try:
        admin_user = create_admin_user(email, full_name)
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        
        print("\n💡 Next steps:")
        print("   1. Update .env with your Google OAuth credentials:")
        print("      GOOGLE_CLIENT_ID=your_client_id")
        print("      GOOGLE_CLIENT_SECRET=your_client_secret")
        print("\n   2. Start the backend:")
        print("      python api_with_db_and_ngrok.py")
        print("\n   3. Login with Google using the admin email:")
        print(f"      {email}")
        
    except Exception as e:
        print(f"\n❌ Failed to create admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

