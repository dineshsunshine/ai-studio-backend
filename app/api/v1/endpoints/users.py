from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel

router = APIRouter()


@router.post("", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(UserModel).filter(
        (UserModel.email == user_in.email) | (UserModel.username == user_in.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    db_user = UserModel(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("", response_model=List[User])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all users"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None


