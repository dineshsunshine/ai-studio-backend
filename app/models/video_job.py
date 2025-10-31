"""
Video Job Model

Represents an asynchronous video generation job using Google Veo API.
Tracks job state, progress, logs, and final video URL.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class VideoJob(Base):
    """
    VideoJob represents an asynchronous video generation task.
    
    Status Flow:
    PENDING → RUNNING → SUCCEEDED
                     → FAILED
                     → CANCELLED
    """
    __tablename__ = "video_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Job parameters
    prompt = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)  # e.g., 'veo-3.1-fast-generate-preview'
    resolution = Column(String(20), nullable=False)  # '720p' or '1080p'
    aspect_ratio = Column(String(20), nullable=False)  # '16:9' or '9:16'
    duration_seconds = Column(Integer, nullable=True)  # 4 or 8
    
    # Image file paths (stored temporarily, deleted after upload to Google)
    initial_image_path = Column(String, nullable=True)
    end_frame_path = Column(String, nullable=True)
    reference_images_paths = Column(JSON, nullable=True)  # List of paths
    
    # Job state
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    # Status values: PENDING, RUNNING, SUCCEEDED, FAILED, CANCELLED
    
    status_message = Column(Text, nullable=True)  # User-friendly status message
    error_message = Column(Text, nullable=True)  # Detailed error message if FAILED
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)  # 0-100
    logs = Column(JSON, nullable=True, default=list)  # List of log entries with timestamps
    
    # Google API tracking
    google_operation_name = Column(String, nullable=True)  # Google's operation ID for polling
    google_result_uri = Column(String, nullable=True)  # Temporary Google video URL
    
    # Final result
    cloudinary_url = Column(String, nullable=True)  # Permanent Cloudinary video URL
    cloudinary_public_id = Column(String, nullable=True)  # For deletion if needed
    
    # Metadata
    tokens_consumed = Column(Integer, default=50)  # Tokens charged for this job
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)  # When processing started
    completed_at = Column(DateTime, nullable=True)  # When job finished (success or failure)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="video_jobs")

    def __repr__(self):
        return f"<VideoJob {self.id} status={self.status} user={self.user_id}>"

    def add_log(self, message: str, level: str = "info"):
        """Add a log entry to the job's logs"""
        if self.logs is None:
            self.logs = []
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,  # info, warning, error
            "message": message
        }
        self.logs.append(log_entry)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "userId": self.user_id,
            "prompt": self.prompt,
            "model": self.model,
            "resolution": self.resolution,
            "aspectRatio": self.aspect_ratio,
            "durationSeconds": self.duration_seconds,
            "status": self.status,
            "statusMessage": self.status_message,
            "errorMessage": self.error_message,
            "progressPercentage": self.progress_percentage,
            "logs": self.logs or [],
            "cloudinaryUrl": self.cloudinary_url,
            "tokensConsumed": self.tokens_consumed,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

