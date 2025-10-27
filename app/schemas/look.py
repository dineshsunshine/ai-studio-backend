from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from app.schemas.product import ProductCreate, ProductResponse
import uuid


class LookBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Title of the look")
    notes: Optional[str] = Field(None, description="Optional notes about the look")


class LookCreate(LookBase):
    """Schema for creating a new look"""
    generated_image_base64: str = Field(..., alias="generatedImageBase64", description="Base64-encoded generated image")
    products: List[ProductCreate] = Field(..., min_items=1, description="List of products in this look")
    
    class Config:
        populate_by_name = True


class LookUpdate(BaseModel):
    """Schema for updating a look (only title and notes)"""
    title: Optional[str] = Field(None, max_length=255, description="Updated title")
    notes: Optional[str] = Field(None, description="Updated notes")


class LookResponse(LookBase):
    """Schema for look in API responses"""
    id: str = Field(..., description="Unique identifier (UUID)")
    generated_image_url: str = Field(..., alias="generatedImageUrl", description="URL to the generated image")
    products: List[ProductResponse] = Field(..., description="List of products in this look")
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

