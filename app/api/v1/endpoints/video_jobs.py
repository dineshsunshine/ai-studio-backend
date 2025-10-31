"""
API endpoints for video generation jobs
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import uuid

from app.core.database import get_db
from app.models.video_job import VideoJob as DBVideoJob
from app.models.user import User
from app.schemas.video_job import VideoJobResponse, VideoJobListResponse
from app.core.auth import get_current_active_user
from app.core.celery_app import celery_app
from app.workers.video_worker import process_video_generation
from app.core.config import settings

router = APIRouter()

# Temporary directory for uploaded images (will be uploaded to Google then deleted)
TEMP_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "temp_uploads")
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)


@router.get("/all", response_model=VideoJobListResponse)
async def list_all_video_jobs(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    PUBLIC ENDPOINT (no auth required) - List all video jobs for monitoring.
    
    This is for the public video monitor dashboard.
    """
    query = db.query(DBVideoJob)
    total = query.count()
    jobs = query.order_by(DBVideoJob.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": total
    }


@router.post("", response_model=VideoJobResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/", response_model=VideoJobResponse, status_code=status.HTTP_202_ACCEPTED, include_in_schema=False)
async def create_video_job(
    prompt: Optional[str] = Form(None),
    model: str = Form(...),
    resolution: str = Form(...),
    aspectRatio: str = Form(..., alias="aspectRatio"),
    durationSeconds: Optional[int] = Form(None, alias="durationSeconds"),
    generateAudio: Optional[bool] = Form(False, alias="generateAudio"),
    initialImage: Optional[UploadFile] = File(None),
    endFrame: Optional[UploadFile] = File(None),
    referenceImages: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new video generation job.
    
    This endpoint:
    1. Consumes 50 tokens from the user's subscription
    2. Validates max concurrent jobs (3 per user)
    3. Creates a job record with status PENDING
    4. Queues the job for background processing
    5. Returns immediately with job ID
    """
    
    # 1. Check token consumption
    from app.api.v1.endpoints.subscription import consume_tokens_internal
    
    token_result = consume_tokens_internal(
        user_id=str(current_user.id),
        operation="video_generation",
        description=f"Video generation: {prompt[:50] if prompt else 'No prompt'}...",
        db=db
    )
    
    if not token_result["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "message": token_result["message"],
                "cost": token_result["cost"],
                "availableTokens": token_result["availableTokens"]
            }
        )
    
    # 2. Check max concurrent jobs (3 per user)
    # Use scalar query to avoid loading all columns (avoids missing column errors)
    try:
        from sqlalchemy import func
        running_jobs_count = db.query(func.count(DBVideoJob.id)).filter(
            DBVideoJob.user_id == str(current_user.id),
            DBVideoJob.status.in_(["PENDING", "RUNNING"])
        ).scalar()
    except Exception as e:
        # If there's a schema issue, default to 0 (allow the request)
        print(f"⚠️  Warning: Error checking concurrent jobs: {e}")
        running_jobs_count = 0
    
    if running_jobs_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Maximum 3 concurrent video jobs allowed. Please wait for existing jobs to complete."
        )
    
    # 3. Validate required fields
    if not prompt and not initialImage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'prompt' or 'initialImage' is required"
        )
    
    if resolution not in ["720p", "1080p"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolution must be '720p' or '1080p'"
        )
    
    if aspectRatio not in ["16:9", "9:16"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aspect ratio must be '16:9' or '9:16'"
        )
    
    # 4. Save uploaded images to temporary storage
    initial_image_path = None
    end_frame_path = None
    reference_images_paths = []
    
    job_temp_dir = os.path.join(TEMP_UPLOAD_DIR, str(uuid.uuid4()))
    os.makedirs(job_temp_dir, exist_ok=True)
    
    if initialImage and initialImage.filename:
        initial_image_path = os.path.join(job_temp_dir, f"initial_{initialImage.filename}")
        with open(initial_image_path, "wb") as f:
            shutil.copyfileobj(initialImage.file, f)
    
    if endFrame and endFrame.filename:
        end_frame_path = os.path.join(job_temp_dir, f"end_{endFrame.filename}")
        with open(end_frame_path, "wb") as f:
            shutil.copyfileobj(endFrame.file, f)
    
    if referenceImages:
        for idx, ref_img in enumerate(referenceImages):
            if ref_img.filename:
                ref_path = os.path.join(job_temp_dir, f"ref_{idx}_{ref_img.filename}")
                with open(ref_path, "wb") as f:
                    shutil.copyfileobj(ref_img.file, f)
                reference_images_paths.append(ref_path)
    
    # 5. Create job record
    new_job = DBVideoJob(
        user_id=str(current_user.id),
        prompt=prompt,
        model=model,
        resolution=resolution,
        aspect_ratio=aspectRatio,
        duration_seconds=durationSeconds,
        generate_audio=generateAudio,
        status="PENDING",
        status_message="Job queued for processing",
        tokens_consumed=token_result["consumedTokens"],
        initial_image_path=initial_image_path,
        end_frame_path=end_frame_path,
        reference_images_paths=reference_images_paths if reference_images_paths else None
    )
    
    # Capture frontend request (for monitoring dashboard)
    new_job.frontend_request = {
        "prompt": prompt,
        "model": model,
        "resolution": resolution,
        "aspectRatio": aspectRatio,
        "durationSeconds": durationSeconds,
        "generateAudio": generateAudio,
        "initialImage": initialImage.filename if initialImage else None,
        "endFrame": endFrame.filename if endFrame else None,
        "referenceImages": [img.filename for img in referenceImages] if referenceImages else None,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    new_job.add_log("📝 Job created", "info")
    new_job.add_log(f"👤 User: {current_user.email}", "info")
    new_job.add_log(f"💎 Tokens consumed: {token_result['consumedTokens']}", "info")
    
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # 5. Queue job for background processing
    try:
        process_video_generation.delay(str(new_job.id))
        new_job.add_log("✅ Job queued for background processing", "info")
        db.commit()
    except Exception as e:
        new_job.status = "FAILED"
        new_job.error_message = f"Failed to queue job: {str(e)}"
        new_job.add_log(f"❌ Failed to queue: {str(e)}", "error")
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue job: {str(e)}"
        )
    
    # 6. Return job details
    return new_job.to_dict()


@router.get("/{job_id}", response_model=VideoJobResponse)
async def get_video_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status and details of a specific video job.
    """
    job = db.query(DBVideoJob).filter(
        DBVideoJob.id == job_id,
        DBVideoJob.user_id == str(current_user.id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video job not found"
        )
    
    return job.to_dict()


@router.get("/", response_model=VideoJobListResponse)
async def list_video_jobs(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all video jobs for the current user.
    
    Query params:
    - status_filter: Filter by status (PENDING, RUNNING, SUCCEEDED, FAILED)
    - limit: Max results (default 50)
    - offset: Pagination offset (default 0)
    """
    query = db.query(DBVideoJob).filter(DBVideoJob.user_id == str(current_user.id))
    
    if status_filter:
        query = query.filter(DBVideoJob.status == status_filter.upper())
    
    total = query.count()
    jobs = query.order_by(DBVideoJob.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": total
    }


@router.get("/{job_id}/download")
async def download_video(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download the completed video.
    
    This endpoint redirects to the Cloudinary URL for fast CDN delivery.
    """
    job = db.query(DBVideoJob).filter(
        DBVideoJob.id == job_id,
        DBVideoJob.user_id == str(current_user.id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video job not found"
        )
    
    if job.status != "SUCCEEDED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Video is not ready yet. Current status: {job.status}"
        )
    
    if not job.cloudinary_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video URL not available"
        )
    
    # Redirect to Cloudinary URL for fast CDN delivery
    return RedirectResponse(url=job.cloudinary_url)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video_job(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a video job.
    
    Note: This only deletes the job record, not the video file from Cloudinary.
    """
    job = db.query(DBVideoJob).filter(
        DBVideoJob.id == job_id,
        DBVideoJob.user_id == str(current_user.id)
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video job not found"
        )
    
    # Optional: Delete video from Cloudinary
    # if job.cloudinary_public_id:
    #     try:
    #         import cloudinary.uploader
    #         cloudinary.uploader.destroy(job.cloudinary_public_id, resource_type="video")
    #     except:
    #         pass
    
    db.delete(job)
    db.commit()
    
    return None

