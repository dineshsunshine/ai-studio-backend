"""
Authentication utilities for JWT and Google OAuth
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from google.auth.transport import requests
from google.oauth2 import id_token
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole, UserStatus
import uuid


# Security scheme for JWT Bearer tokens
security = HTTPBearer()


# ==================== JWT Functions ====================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT access token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_token_for_user(user: User) -> Dict[str, Any]:
    """
    Create JWT token with user information.
    
    Args:
        user: User model instance
        
    Returns:
        Dictionary with token data
    """
    token_data = {
        "sub": str(user.id),  # Subject (user ID)
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value
    }
    
    access_token = create_access_token(token_data)
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": expires_in
    }


# ==================== Google OAuth Functions ====================

def verify_google_token(id_token_str: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google OAuth ID token and extract user information.
    
    Args:
        id_token_str: Google ID token string
        
    Returns:
        Dictionary with user info (sub, email, name, picture) or None if invalid
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Extract user information
        return {
            "google_id": idinfo['sub'],
            "email": idinfo['email'],
            "full_name": idinfo.get('name'),
            "profile_picture": idinfo.get('picture')
        }
    except ValueError as e:
        print(f"❌ Google token verification failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error verifying Google token: {e}")
        return None


# ==================== Authentication Middleware ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract token
    token = credentials.credentials
    
    # Verify token
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # Check if user is active
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}. Access denied."
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is not active
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user has admin role.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Current user (if admin)
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ==================== Optional Authentication ====================

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current user (returns None if not authenticated).
    Useful for endpoints that work both with and without authentication.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        db: Database session
        
    Returns:
        Current user or None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


