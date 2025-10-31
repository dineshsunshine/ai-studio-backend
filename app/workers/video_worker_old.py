"""
Celery worker for processing video generation jobs
"""

import os
import time
import requests
import tempfile
from datetime import datetime
from typing import Optional
from celery import Task
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
# This is critical for Celery workers to access GOOGLE_API_KEY
load_dotenv()

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video_job import VideoJob
from app.core.storage import upload_video_to_cloudinary

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API key is loaded
if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY is not set! Video generation will fail.")
    print("   Please add GOOGLE_API_KEY to your .env file")
    genai_client = None
else:
    print(f"✅ Google API key loaded: {GOOGLE_API_KEY[:10]}...")
    # Initialize the GenAI client with API key
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY  # Ensure it's in environment
    genai_client = genai.Client(api_key=GOOGLE_API_KEY)


class VideoGenerationTask(Task):
    """Custom task class with database session management"""
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


@celery_app.task(bind=True, base=VideoGenerationTask, name="app.workers.video_worker.process_video_generation")
def process_video_generation(self, job_id: str):
    """
    Background task to process a video generation job.
    
    Steps:
    1. Update job status to RUNNING
    2. Call Google Veo API to start generation
    3. Poll Google operation until complete
    4. Download video from Google's resultUri
    5. Upload to Cloudinary
    6. Update job with final URL and status SUCCEEDED
    """
    db = SessionLocal()
    
    try:
        # 1. Get job from database
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            print(f"❌ Job {job_id} not found")
            return
        
        # 2. Update status to RUNNING
        job.status = "RUNNING"
        job.started_at = datetime.utcnow()
        job.status_message = "Initializing video generation..."
        job.progress_percentage = 5
        job.add_log("🚀 Starting video generation", "info")
        db.commit()
        
        # 3. Prepare Google API request
        job.add_log(f"📝 Prompt: {job.prompt[:100]}...", "info")
        job.add_log(f"🎬 Model: {job.model}", "info")
        job.add_log(f"📐 Resolution: {job.resolution}, Aspect Ratio: {job.aspect_ratio}", "info")
        
        google_request_body = {
            "prompt": job.prompt or "",
            "model": job.model,
            "aspectRatio": job.aspect_ratio,
            "resolution": job.resolution,
        }
        
        if job.duration_seconds:
            google_request_body["durationSeconds"] = job.duration_seconds
        
        job.progress_percentage = 10
        job.status_message = "Calling Google Veo API..."
        db.commit()
        
        # 4. Call Google Veo API
        try:
            job.add_log("☁️  Calling Google Veo API...", "info")
            google_response = requests.post(
                f"{GOOGLE_GENAI_BASE_URL}/models/{job.model}:generateVideos?key={GOOGLE_API_KEY}",
                json=google_request_body,
                timeout=60
            )
            google_response.raise_for_status()
            operation_data = google_response.json()
            
            # Extract operation name
            operation_name = operation_data.get("name")
            if not operation_name:
                raise ValueError("No operation name returned from Google API")
            
            job.google_operation_name = operation_name
            job.add_log(f"✅ Google operation started: {operation_name}", "info")
            job.progress_percentage = 15
            job.status_message = "Video generation in progress..."
            db.commit()
            
        except requests.exceptions.RequestException as e:
            job.status = "FAILED"
            job.error_message = f"Failed to call Google API: {str(e)}"
            job.add_log(f"❌ Google API error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 5. Poll Google operation until complete
        job.add_log("⏳ Polling Google API for completion...", "info")
        max_polls = 180  # 15 minutes max (5 seconds interval)
        poll_count = 0
        
        while poll_count < max_polls:
            try:
                operation_response = requests.get(
                    f"{GOOGLE_GENAI_BASE_URL}/{operation_name}?key={GOOGLE_API_KEY}",
                    timeout=30
                )
                operation_response.raise_for_status()
                operation_status = operation_response.json()
                
                # Check if done
                if operation_status.get("done"):
                    # Check for errors
                    if "error" in operation_status:
                        error_msg = operation_status["error"].get("message", "Unknown error")
                        job.status = "FAILED"
                        job.error_message = f"Google API error: {error_msg}"
                        job.add_log(f"❌ Generation failed: {error_msg}", "error")
                        job.completed_at = datetime.utcnow()
                        db.commit()
                        return
                    
                    # Success! Extract resultUri
                    response_data = operation_status.get("response", {})
                    result_uri = response_data.get("resultUri")
                    
                    if not result_uri:
                        job.status = "FAILED"
                        job.error_message = "No resultUri in Google response"
                        job.add_log("❌ No video URL returned", "error")
                        job.completed_at = datetime.utcnow()
                        db.commit()
                        return
                    
                    job.google_result_uri = result_uri
                    job.add_log(f"✅ Video generation complete! Google URI: {result_uri[:50]}...", "info")
                    job.progress_percentage = 70
                    job.status_message = "Downloading video from Google..."
                    db.commit()
                    break
                
                # Update progress
                poll_count += 1
                progress = min(15 + int((poll_count / max_polls) * 50), 65)
                if job.progress_percentage != progress:
                    job.progress_percentage = progress
                    if poll_count % 12 == 0:  # Log every minute
                        job.add_log(f"⏳ Still generating... ({poll_count * 5}s elapsed)", "info")
                    db.commit()
                
                time.sleep(5)  # Poll every 5 seconds
                
            except requests.exceptions.RequestException as e:
                job.add_log(f"⚠️  Polling error: {str(e)}, retrying...", "warning")
                time.sleep(5)
                continue
        
        if poll_count >= max_polls:
            job.status = "FAILED"
            job.error_message = "Video generation timed out (15 minutes)"
            job.add_log("❌ Generation timed out", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 6. Download video from Google
        job.add_log("📥 Downloading video from Google...", "info")
        job.progress_percentage = 75
        db.commit()
        
        try:
            # Download to temporary file
            video_response = requests.get(
                f"{job.google_result_uri}?key={GOOGLE_API_KEY}",
                stream=True,
                timeout=300  # 5 minutes for download
            )
            video_response.raise_for_status()
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_file_path = temp_file.name
                for chunk in video_response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
            
            job.add_log(f"✅ Video downloaded: {os.path.getsize(temp_file_path) / (1024*1024):.2f} MB", "info")
            job.progress_percentage = 85
            job.status_message = "Uploading to Cloudinary..."
            db.commit()
            
        except requests.exceptions.RequestException as e:
            job.status = "FAILED"
            job.error_message = f"Failed to download video: {str(e)}"
            job.add_log(f"❌ Download error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 7. Upload to Cloudinary
        try:
            job.add_log("☁️  Uploading to Cloudinary...", "info")
            cloudinary_result = upload_video_to_cloudinary(temp_file_path, job_id)
            
            job.cloudinary_url = cloudinary_result["url"]
            job.cloudinary_public_id = cloudinary_result["public_id"]
            job.add_log(f"✅ Upload complete! URL: {job.cloudinary_url}", "info")
            job.progress_percentage = 95
            db.commit()
            
        except Exception as e:
            job.status = "FAILED"
            job.error_message = f"Failed to upload to Cloudinary: {str(e)}"
            job.add_log(f"❌ Cloudinary upload error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                job.add_log("🗑️  Temporary file cleaned up", "info")
        
        # 8. Mark as succeeded
        job.status = "SUCCEEDED"
        job.status_message = "Video generation completed successfully!"
        job.progress_percentage = 100
        job.completed_at = datetime.utcnow()
        job.add_log("🎉 Job completed successfully!", "info")
        db.commit()
        
        print(f"✅ Job {job_id} completed successfully: {job.cloudinary_url}")
        
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"❌ Unexpected error in job {job_id}: {str(e)}")
        try:
            job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
            if job:
                job.status = "FAILED"
                job.error_message = f"Unexpected error: {str(e)}"
                job.add_log(f"❌ Unexpected error: {str(e)}", "error")
                job.completed_at = datetime.utcnow()
                db.commit()
        except:
            pass
    
    finally:
        db.close()

