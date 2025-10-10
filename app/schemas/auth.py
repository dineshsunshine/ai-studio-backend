from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_serializer
import uuid


# ==================== Google OAuth ====================

class GoogleAuthRequest(BaseModel):
    """Request schema for Google OAuth login"""
    google_id_token: str = Field(
        ..., 
        alias="idToken",
        description="Google ID token from OAuth"
    )
    
    class Config:
        populate_by_name = True  # Accepts google_id_token, idToken, and id_token


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = Field(None, alias="fullName")
    
    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """User response schema"""
    id: str
    profile_picture: Optional[str] = Field(None, alias="profilePicture")
    role: str
    status: str
    created_at: str = Field(..., alias="createdAt")
    last_login: Optional[str] = Field(None, alias="lastLogin")
    
    @field_serializer('id')
    def serialize_id(self, value):
        """Convert UUID to string"""
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    
    @field_serializer('created_at', 'last_login')
    def serialize_datetime(self, value):
        """Convert datetime to ISO string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


class UserUpdate(BaseModel):
    """Schema for updating user (admin only)"""
    role: Optional[str] = None
    status: Optional[str] = None


# ==================== Access Request Schemas ====================

class AccessRequestCreate(BaseModel):
    """Schema for creating access request"""
    email: EmailStr
    full_name: Optional[str] = Field(None, alias="fullName")
    reason: Optional[str] = None
    
    class Config:
        populate_by_name = True


class AccessRequestResponse(BaseModel):
    """Schema for access request response"""
    id: str
    email: EmailStr
    full_name: Optional[str] = Field(None, alias="fullName")
    profile_picture: Optional[str] = Field(None, alias="profilePicture")
    reason: Optional[str] = None
    status: str
    requested_at: str = Field(..., alias="requestedAt")
    reviewed_at: Optional[str] = Field(None, alias="reviewedAt")
    rejection_reason: Optional[str] = Field(None, alias="rejectionReason")
    
    @field_serializer('id')
    def serialize_id(self, value):
        """Convert UUID to string"""
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    
    @field_serializer('requested_at', 'reviewed_at')
    def serialize_datetime(self, value):
        """Convert datetime to ISO string"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


class AccessRequestListResponse(BaseModel):
    """Schema for paginated access request list"""
    requests: list[AccessRequestResponse]
    total: int
    skip: int
    limit: int


class AccessRequestApprove(BaseModel):
    """Schema for approving access request"""
    role: Optional[str] = "user"  # Default to user role


class AccessRequestReject(BaseModel):
    """Schema for rejecting access request"""
    reason: Optional[str] = None


# ==================== Authentication Response Schemas ====================

class TokenData(BaseModel):
    """JWT token data"""
    user: UserResponse
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field(default="Bearer", alias="tokenType")
    expires_in: int = Field(..., alias="expiresIn")  # Seconds until expiry
    
    class Config:
        populate_by_name = True
        by_alias = True


class AuthResponse(BaseModel):
    """Generic auth response"""
    status: str  # success, pending, request_created, rejected
    message: str
    data: Optional[TokenData | dict] = None


# ==================== User List Response ====================

class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    skip: int
    limit: int

