"""
Look Videos API Endpoints

Handles creating, listing, and managing videos associated with looks.
Users can create videos from their looks and set them as default for display.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
import uuid

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.look import Look, look_videos
from app.models.video_job import VideoJob
from app.schemas.look import VideoInLook
from app.schemas.video_job import VideoJobCreate, VideoJobResponse

router = APIRouter(prefix="/looks", tags=["Look Videos"])


@router.post("/{look_id}/videos", response_model=VideoJobResponse, status_code=status.HTTP_201_CREATED)
async def create_video_from_look(
    look_id: str,
    video_data: VideoJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a video from a look.
    
    **Authentication required. Only look owner can create videos.**
    
    The video will be associated with this look and can be set as default.
    Token cost: 50 tokens (for video generation)
    
    Path Parameters:
    - look_id: The ID of the look to create video from
    
    Request Body:
    - prompt: Optional text prompt for video generation
    - model: Model name (e.g., 'veo-3.1-fast-generate-preview')
    - resolution: '720p' or '1080p'
    - aspectRatio: '16:9' or '9:16'
    - durationSeconds: 4 or 8 seconds
    - generateAudio: Optional boolean for audio generation
    """
    # Get the look
    look = db.query(Look).filter(Look.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Check if current user is the look owner
    if str(look.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the look owner can create videos from this look"
        )
    
    # TODO: Create video job via existing video creation logic
    # For now, this is a placeholder that shows the structure
    # The actual video creation will delegate to existing video endpoints
    
    # Create video job
    new_video = VideoJob(
        user_id=str(current_user.id),
        prompt=video_data.prompt,
        model=video_data.model,
        resolution=video_data.resolution,
        aspect_ratio=video_data.aspectRatio,
        duration_seconds=video_data.durationSeconds,
        generate_audio=video_data.generateAudio,
        status="PENDING"
    )
    
    db.add(new_video)
    db.flush()  # Get the ID
    
    # Associate video with look
    assoc = look_videos.insert().values(
        look_id=look_id,
        video_job_id=new_video.id,
        is_default=False
    )
    db.execute(assoc)
    db.commit()
    db.refresh(new_video)
    
    # Return video response
    return VideoJobResponse(
        id=str(new_video.id),
        userId=str(new_video.user_id),
        prompt=new_video.prompt,
        model=new_video.model,
        resolution=new_video.resolution,
        aspectRatio=new_video.aspect_ratio,
        durationSeconds=new_video.duration_seconds,
        generateAudio=new_video.generate_audio,
        mockMode=new_video.mock_mode or False,
        status=new_video.status,
        statusMessage=new_video.status_message,
        errorMessage=new_video.error_message,
        progressPercentage=new_video.progress_percentage,
        logs=[],
        cloudinaryUrl=new_video.cloudinary_url,
        tokensConsumed=50,
        createdAt=new_video.created_at.isoformat() if new_video.created_at else None,
        startedAt=new_video.started_at.isoformat() if new_video.started_at else None,
        completedAt=new_video.completed_at.isoformat() if new_video.completed_at else None,
        updatedAt=new_video.updated_at.isoformat() if new_video.updated_at else None
    )


@router.get("/{look_id}/videos", response_model=List[VideoInLook])
async def list_look_videos(
    look_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all videos associated with a look.
    
    **Authentication required.**
    
    Returns all videos linked to this look, including their status and whether they're set as default.
    """
    # Verify look exists and user has access
    look = db.query(Look).filter(Look.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Get videos from junction table
    videos_data = db.query(VideoJob, look_videos.c.is_default).join(
        look_videos,
        VideoJob.id == look_videos.c.video_job_id
    ).filter(look_videos.c.look_id == look_id).all()
    
    result = []
    for video, is_default in videos_data:
        result.append(VideoInLook(
            id=str(video.id),
            status=video.status,
            cloudinary_url=video.cloudinary_url,
            is_default=is_default,
            created_at=video.created_at.isoformat() if video.created_at else None,
            progress_percentage=video.progress_percentage
        ))
    
    return result


@router.patch("/{look_id}/videos/{video_id}/set-default", status_code=status.HTTP_204_NO_CONTENT)
async def set_default_video(
    look_id: str,
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Set a video as the default for a look.
    
    **Authentication required. Only look owner can set default video.**
    
    When a video is set as default, it will be displayed instead of the look image
    in listing pages and thumbnails.
    
    Path Parameters:
    - look_id: The ID of the look
    - video_id: The ID of the video to set as default
    """
    # Verify look exists and user is owner
    look = db.query(Look).filter(Look.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    if str(look.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the look owner can set default video"
        )
    
    # Verify video exists and is associated with look
    video_assoc = db.query(look_videos).filter(
        and_(
            look_videos.c.look_id == look_id,
            look_videos.c.video_job_id == video_id
        )
    ).first()
    
    if not video_assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not associated with this look"
        )
    
    # Unset all other videos for this look
    db.execute(
        look_videos.update().where(look_videos.c.look_id == look_id).values(is_default=False)
    )
    
    # Set this video as default
    db.execute(
        look_videos.update().where(
            and_(
                look_videos.c.look_id == look_id,
                look_videos.c.video_job_id == video_id
            )
        ).values(is_default=True)
    )
    
    db.commit()


@router.delete("/{look_id}/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_look_video(
    look_id: str,
    video_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a video associated with a look.
    
    **Authentication required. Only look owner can delete videos.**
    
    If the video is set as default, it will be unset before deletion.
    The video will be removed from storage (Cloudinary or local).
    
    Path Parameters:
    - look_id: The ID of the look
    - video_id: The ID of the video to delete
    """
    # Verify look exists and user is owner
    look = db.query(Look).filter(Look.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    if str(look.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the look owner can delete videos"
        )
    
    # Verify video exists and is associated with look
    video_assoc = db.query(look_videos).filter(
        and_(
            look_videos.c.look_id == look_id,
            look_videos.c.video_job_id == video_id
        )
    ).first()
    
    if not video_assoc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not associated with this look"
        )
    
    # Get the video to check if we need to delete from storage
    video = db.query(VideoJob).filter(VideoJob.id == video_id).first()
    
    # Delete from storage if it exists
    if video and video.cloudinary_url:
        try:
            from app.core.storage import storage_service
            # Extract public_id and delete
            if video.cloudinary_public_id:
                storage_service.delete_file(video.cloudinary_public_id)
        except Exception as e:
            print(f"⚠️  Warning: Could not delete video from storage: {e}")
    
    # Remove association
    db.execute(
        look_videos.delete().where(
            and_(
                look_videos.c.look_id == look_id,
                look_videos.c.video_job_id == video_id
            )
        )
    )
    
    # Optionally delete the video job record (set to inactive or soft delete)
    if video:
        video.status = "DELETED"
        db.commit()
    else:
        db.commit()

