"""
Pydantic schemas for Model endpoints
"""
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional


class ModelBase(BaseModel):
    """Base schema for Model"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the model")


class ModelUpload(ModelBase):
    """Schema for uploading a model with an image file"""
    pass


class ModelGenerate(ModelBase):
    """Schema for generating a model with AI"""
    prompt_details: str = Field(..., min_length=1, description="Prompt details for AI generation", alias="promptDetails")
    
    class Config:
        populate_by_name = True  # Accept both prompt_details and promptDetails


class ModelResponse(ModelBase):
    """Schema for Model response"""
    id: str = Field(..., description="Unique identifier (UUID)")
    image_url: str = Field(..., description="URL to the model's image", alias="imageUrl")
    prompt_details: Optional[str] = Field(None, description="AI generation prompt (if applicable)", alias="promptDetails")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True  # Accept both naming conventions
        by_alias = True  # Use aliases when serializing (return camelCase to frontend)


class ModelListResponse(BaseModel):
    """Schema for list of models response"""
    models: list[ModelResponse]
    total: int

