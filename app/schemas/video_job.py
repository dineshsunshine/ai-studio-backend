"""
Pydantic schemas for Video Job API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VideoJobCreate(BaseModel):
    """Schema for creating a new video generation job"""
    prompt: Optional[str] = Field(None, description="Text prompt for video generation")
    model: str = Field(..., description="Model name, e.g., 'veo-3.1-fast-generate-preview'")
    resolution: str = Field(..., description="Video resolution: '720p' or '1080p'")
    aspectRatio: str = Field(..., alias="aspectRatio", description="Aspect ratio: '16:9' or '9:16'")
    durationSeconds: Optional[int] = Field(None, alias="durationSeconds", description="Duration: 4 or 8 seconds")
    generateAudio: Optional[bool] = Field(False, alias="generateAudio", description="Enable AI-generated audio/sound")


class LogEntry(BaseModel):
    """Single log entry"""
    timestamp: str
    level: str  # info, warning, error
    message: str


class VideoJobResponse(BaseModel):
    """Schema for video job in API responses"""
    id: str
    userId: str
    prompt: Optional[str]
    model: str
    resolution: str
    aspectRatio: str
    durationSeconds: Optional[int]
    generateAudio: Optional[bool] = False
    mockMode: bool = Field(..., alias="mockMode", description="Mock mode flag (required): true to skip Veo API, false to use real Veo API")
    status: str  # PENDING, RUNNING, SUCCEEDED, FAILED, CANCELLED
    statusMessage: Optional[str]
    errorMessage: Optional[str]
    progressPercentage: int
    logs: List[LogEntry]
    cloudinaryUrl: Optional[str]
    tokensConsumed: int
    createdAt: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    updatedAt: Optional[str]
    # Request/Response tracking (Optional dict for flexibility)
    frontendRequest: Optional[dict] = None
    veoRequest: Optional[dict] = None
    veoResponse: Optional[dict] = None
    backendResponse: Optional[dict] = None

    class Config:
        from_attributes = True


class VideoJobListResponse(BaseModel):
    """Schema for listing video jobs"""
    jobs: List[VideoJobResponse]
    total: int

