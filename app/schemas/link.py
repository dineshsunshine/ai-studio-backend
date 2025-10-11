"""
Pydantic Schemas for Link (shareable collections of looks)
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.look import LookResponse


class LinkCreate(BaseModel):
    """Schema for creating a new link"""
    clientName: str = Field(..., min_length=1, max_length=255, description="Client's name")
    clientPhone: Optional[str] = Field(None, max_length=50, description="Client's phone number")
    lookIds: List[str] = Field(..., min_items=1, description="List of look IDs to include in this link")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "clientName": "John Doe",
                "clientPhone": "+1234567890",
                "lookIds": ["look-uuid-1", "look-uuid-2"]
            }
        }


class LinkUpdate(BaseModel):
    """Schema for updating a link"""
    clientName: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated client name")
    clientPhone: Optional[str] = Field(None, max_length=50, description="Updated client phone")
    lookIds: Optional[List[str]] = Field(None, min_items=1, description="Updated list of look IDs")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "clientName": "Jane Smith",
                "clientPhone": "+1987654321",
                "lookIds": ["look-uuid-1", "look-uuid-3"]
            }
        }


class LinkResponse(BaseModel):
    """Schema for link in API responses"""
    id: str = Field(..., description="Unique identifier (UUID)")
    linkId: str = Field(..., alias="linkId", description="Alphanumeric short link ID")
    clientName: str = Field(..., alias="clientName", description="Client's name")
    clientPhone: Optional[str] = Field(None, alias="clientPhone", description="Client's phone number")
    shortUrl: str = Field(..., alias="shortUrl", description="Full short URL to share with client")
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
                "clientName": "John Doe",
                "clientPhone": "+1234567890",
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
    clientName: str = Field(..., alias="clientName", description="Client's name")
    looks: List[LookResponse] = Field(..., description="List of looks to display")
    createdAt: str = Field(..., alias="createdAt", description="Creation timestamp")
    
    class Config:
        populate_by_name = True
        by_alias = True
        json_schema_extra = {
            "example": {
                "linkId": "AB12CD34",
                "clientName": "John Doe",
                "looks": [],
                "createdAt": "2025-10-11T12:00:00Z"
            }
        }

