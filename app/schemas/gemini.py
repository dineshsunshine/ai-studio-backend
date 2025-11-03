"""
Pydantic schemas for Gemini API endpoints.
These schemas validate and serialize requests/responses for all Gemini wrapper endpoints.
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field


# ============================================================================
# Shared/Common Schemas
# ============================================================================

class Part(BaseModel):
    """A single part of a content message (text or inline data)."""
    text: Optional[str] = None
    inlineData: Optional[Dict[str, Any]] = Field(None, alias="inlineData")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class Contents(BaseModel):
    """Contents for a generation request."""
    parts: List[Dict[str, Any]] = Field(..., description="List of content parts (text, images, etc)")
    
    class Config:
        from_attributes = True


class GenerationConfig(BaseModel):
    """Configuration for text generation."""
    maxOutputTokens: Optional[int] = Field(None, alias="maxOutputTokens")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ============================================================================
# 1. Generate Text
# ============================================================================

class GenerateTextRequest(BaseModel):
    """Request for text generation endpoint."""
    model: str = Field(..., description="Model name (e.g., 'gemini-2.5-flash')")
    systemInstruction: Optional[str] = Field(None, alias="systemInstruction", description="Optional system prompt")
    contents: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Content to process (dict or list for conversation history)")
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GenerateTextResponse(BaseModel):
    """Response for text generation."""
    text: str = Field(..., description="Generated text")
    
    class Config:
        from_attributes = True


# ============================================================================
# 2. Generate Image
# ============================================================================

class ImageConfig(BaseModel):
    """Image-specific configuration."""
    aspectRatio: Optional[str] = Field(None, alias="aspectRatio")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GenerateImageRequest(BaseModel):
    """Request for image generation endpoint."""
    model: str = Field(..., description="Model name (e.g., 'gemini-2.5-flash-image')")
    systemInstruction: Optional[str] = Field(None, alias="systemInstruction")
    contents: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Content with prompt and images (can be dict or list for conversation history)")
    history: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GenerateImageResponse(BaseModel):
    """Response for image generation."""
    imageBase64: str = Field(..., alias="imageBase64", description="Base64-encoded generated image")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ============================================================================
# 3. Generate Imagen
# ============================================================================

class GenerateImagenRequest(BaseModel):
    """Request for Imagen high-quality model generation."""
    prompt: str = Field(..., description="Text prompt for image generation")
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class GenerateImagenResponse(BaseModel):
    """Response for Imagen generation."""
    imageBase64: str = Field(..., alias="imageBase64", description="Base64-encoded generated image")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ============================================================================
# 4. Generate JSON
# ============================================================================

class ResponseSchema(BaseModel):
    """JSON schema for structured responses."""
    type: str
    properties: Dict[str, Any]
    required: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


class GenerateJsonRequest(BaseModel):
    """Request for structured JSON generation."""
    model: str = Field(..., description="Model name")
    systemInstruction: Optional[str] = Field(None, alias="systemInstruction")
    contents: Union[Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Content to process (dict or list)")
    config: Optional[Dict[str, Any]] = None
    taskType: Optional[str] = Field(None, description="Task identifier for response transformation: IMPROVE_SYSTEM_PROMPT, GENERATE_VIDEO_PROMPTS, ANALYZE_PRODUCT_IMAGE, GENERATE_PRODUCT_COPY")
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GenerateJsonResponse(BaseModel):
    """Response for JSON generation - can be any JSON structure (dict, list, or primitive)."""
    
    class Config:
        from_attributes = True
        extra = "allow"  # Allow any additional fields
    
    def __init__(self, **data):
        """Override to allow storing raw dict/list/any structure."""
        # If a single argument is passed (the parsed JSON response),
        # we need to store it directly
        super().__init__(**data)


# ============================================================================
# 5. Grounded Search
# ============================================================================

class GroundedSearchRequest(BaseModel):
    """Request for Google Search grounded generation."""
    model: str = Field(..., description="Model name")
    systemInstruction: Optional[str] = Field(None, alias="systemInstruction")
    contents: Union[str, Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Text content or brand/product info")
    config: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True


class GroundedSearchResponse(BaseModel):
    """Response for grounded search."""
    text: str = Field(..., description="Search-grounded text response")
    
    class Config:
        from_attributes = True


# ============================================================================
# Error Response
# ============================================================================

class GeminiErrorResponse(BaseModel):
    """Standard error response from Gemini endpoints."""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")
    
    class Config:
        from_attributes = True
