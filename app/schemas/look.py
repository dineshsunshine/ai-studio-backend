from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_serializer
from app.schemas.product import ProductCreate, ProductResponse
import uuid


class LookVisibility(str, Enum):
    """Visibility options for looks"""
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class LookBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Title of the look")
    notes: Optional[str] = Field(None, description="Optional notes about the look")


class LookCreate(LookBase):
    """Schema for creating a new look"""
    generated_image_base64: str = Field(..., alias="generatedImageBase64", description="Base64-encoded generated image")
    products: List[ProductCreate] = Field(..., min_items=1, description="List of products in this look")
    visibility: LookVisibility = Field(default=LookVisibility.PRIVATE, description="Visibility setting: private, shared, or public")
    shared_with_user_ids: Optional[List[str]] = Field(default=None, alias="sharedWithUserIds", description="List of user IDs to share with (only used when visibility=shared)")
    
    class Config:
        populate_by_name = True


class LookUpdate(BaseModel):
    """Schema for updating a look (only title and notes)"""
    title: Optional[str] = Field(None, max_length=255, description="Updated title")
    notes: Optional[str] = Field(None, description="Updated notes")


class LookVisibilityUpdate(BaseModel):
    """Schema for updating look visibility settings"""
    visibility: LookVisibility = Field(..., description="New visibility setting: private, shared, or public")
    shared_with_user_ids: Optional[List[str]] = Field(default=None, alias="sharedWithUserIds", description="List of user IDs to share with (only used when visibility=shared)")
    
    class Config:
        populate_by_name = True


class SharedUserInfo(BaseModel):
    """Basic user info for shared_with list"""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User name")
    
    class Config:
        from_attributes = True




class VideoInLook(BaseModel):
    """Schema for video associated with a look"""
    id: str = Field(..., description="Video job ID")
    status: str = Field(..., description="Video status: PENDING, RUNNING, SUCCEEDED, FAILED")
    cloudinary_url: Optional[str] = Field(None, alias="cloudinaryUrl", description="URL to the generated video (only if SUCCEEDED)")
    is_default: bool = Field(False, alias="isDefault", description="Whether this video is set as default for the look")
    created_at: str = Field(..., alias="createdAt", description="When the video was created")
    progress_percentage: Optional[int] = Field(None, alias="progressPercentage", description="Progress if still processing (0-100)")
    
    @field_serializer('created_at')
    def serialize_datetime(self, value):
        """Convert datetime to ISO string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True

class LookResponse(LookBase):
    """Schema for look in API responses"""
    id: str = Field(..., description="Unique identifier (UUID)")
    generated_image_url: str = Field(..., alias="generatedImageUrl", description="URL to the generated image")
    products: List[ProductResponse] = Field(..., description="List of products in this look")
    visibility: LookVisibility = Field(..., description="Visibility setting: private, shared, or public")
    shared_with: List[SharedUserInfo] = Field(default=[], alias="sharedWith", description="Users this look is shared with")
    videos: List['VideoInLook'] = Field(default=[], description="Videos created from this look (backward compatible: empty list if none)")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp")
    
    @field_serializer('id')
    def serialize_id(self, value):
        """Convert UUID to string"""
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value):
        """Convert datetime to ISO string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


class LookListResponse(BaseModel):
    """Schema for paginated list of looks"""
    looks: List[LookResponse]
    total: int
    skip: int
    limit: int

