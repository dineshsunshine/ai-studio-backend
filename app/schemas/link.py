"""
Pydantic Schemas for Link (shareable collections of looks)
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.look import LookResponse


class LinkCreate(BaseModel):
    """Schema for creating a new link"""
    title: str = Field(..., min_length=1, max_length=255, description="Link title")
    description: Optional[str] = Field(None, max_length=1000, description="Link description")
    lookIds: List[str] = Field(..., min_items=1, description="List of look IDs to include in this link")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Spring Collection 2025",
                "description": "Elegant spring looks for modern women",
                "lookIds": ["look-uuid-1", "look-uuid-2"]
            }
        }


class LinkUpdate(BaseModel):
    """Schema for updating a link"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated link title")
    description: Optional[str] = Field(None, max_length=1000, description="Updated link description")
    lookIds: Optional[List[str]] = Field(None, min_items=1, description="Updated list of look IDs")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Summer Collection 2025",
                "description": "Beach-ready summer looks",
                "lookIds": ["look-uuid-1", "look-uuid-3"]
            }
        }


class LinkResponse(BaseModel):
    """Schema for link in API responses"""
    id: str = Field(..., description="Unique identifier (UUID)")
    linkId: str = Field(..., alias="linkId", description="Alphanumeric short link ID")
    title: str = Field(..., description="Link title")
    description: Optional[str] = Field(None, description="Link description")
    coverImageUrl: Optional[str] = Field(None, alias="coverImageUrl", description="Cover/masthead image URL")
    shortUrl: str = Field(..., alias="shortUrl", description="Full short URL to share")
    looks: List[LookResponse] = Field(..., description="List of looks in this link")
    createdAt: str = Field(..., alias="createdAt", description="Creation timestamp")
    updatedAt: str = Field(..., alias="updatedAt", description="Last update timestamp")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "linkId": "AB12CD34",
                "title": "Spring Collection 2025",
                "description": "Elegant spring looks",
                "coverImageUrl": "https://storage.com/cover.jpg",
                "shortUrl": "https://yourdomain.com/l/AB12CD34",
                "looks": [],
                "createdAt": "2025-10-11T12:00:00Z",
                "updatedAt": "2025-10-11T12:00:00Z"
            }
        }


class LinkListResponse(BaseModel):
    """Schema for paginated list of links"""
    links: List[LinkResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "links": [],
                "total": 10,
                "skip": 0,
                "limit": 100
            }
        }


class SharedLinkResponse(BaseModel):
    """Schema for publicly shared link (no auth required)"""
    linkId: str = Field(..., alias="linkId", description="Alphanumeric link ID")
    title: str = Field(..., description="Link title")
    description: Optional[str] = Field(None, description="Link description")
    coverImageUrl: Optional[str] = Field(None, alias="coverImageUrl", description="Cover/masthead image URL")
    companyLogoUrl: Optional[str] = Field(None, alias="companyLogoUrl", description="Company logo URL for branding")
    looks: List[LookResponse] = Field(..., description="List of looks to display")
    createdAt: str = Field(..., alias="createdAt", description="Creation timestamp")
    
    class Config:
        populate_by_name = True
        by_alias = True
        json_schema_extra = {
            "example": {
                "linkId": "AB12CD34",
                "title": "Spring Collection 2025",
                "description": "Elegant spring looks",
                "coverImageUrl": "https://storage.com/cover.jpg",
                "companyLogoUrl": "https://storage.com/logo.png",
                "looks": [],
                "createdAt": "2025-10-11T12:00:00Z"
            }
        }

