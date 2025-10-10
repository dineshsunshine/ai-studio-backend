from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
import uuid


class ProductBase(BaseModel):
    sku: Optional[str] = Field(None, description="Product SKU")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    designer: Optional[str] = Field(None, max_length=255, description="Designer/brand name")
    price: Optional[float] = Field(None, ge=0, description="Product price")
    product_url: Optional[str] = Field(None, alias="productUrl", description="URL to product page")


class ProductCreate(ProductBase):
    """Schema for creating a product with base64 thumbnail"""
    thumbnail_base64: str = Field(..., alias="thumbnailBase64", description="Base64-encoded thumbnail image")
    
    class Config:
        populate_by_name = True


class ProductResponse(ProductBase):
    """Schema for product in API responses"""
    id: str = Field(..., description="Unique identifier (UUID)")
    thumbnail_url: str = Field(..., alias="thumbnailUrl", description="URL to product thumbnail image")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    
    @field_serializer('id')
    def serialize_id(self, value):
        """Convert UUID to string"""
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)
    
    @field_serializer('created_at')
    def serialize_created_at(self, value):
        """Convert datetime to ISO string"""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True

