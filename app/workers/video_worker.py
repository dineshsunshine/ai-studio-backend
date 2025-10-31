"""
Celery worker for processing video generation jobs using Google Veo 3.1
Updated to use the new google-genai SDK as per official documentation:
https://developers.googleblog.com/en/introducing-veo-3-1-and-new-creative-capabilities-in-the-gemini-api/
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
load_dotenv()

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.video_job import VideoJob
from app.core.storage import upload_video_to_cloudinary

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validate API key and initialize client
if not GOOGLE_API_KEY:
    print("⚠️  WARNING: GOOGLE_API_KEY is not set! Video generation will fail.")
    genai_client = None
else:
    print(f"✅ Google API key loaded: {GOOGLE_API_KEY[:10]}...")
    genai_client = genai.Client(api_key=GOOGLE_API_KEY)


class VideoGenerationTask(Task):
    """Custom task class with database session management"""
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


@celery_app.task(bind=True, base=VideoGenerationTask, name="app.workers.video_worker.process_video_generation")
def process_video_generation(self, job_id: str):
    """
    Background task to process a video generation job using Google Veo 3.1.
    
    Steps:
    1. Update job status to RUNNING
    2. Call Google Veo API using the new genai SDK
    3. Wait for generation to complete
    4. Download video from Google's URI
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
        job.add_log("🚀 Starting video generation with Veo 3.1", "info")
        db.commit()
        
        # 3. Log job details
        job.add_log(f"📝 Prompt: {job.prompt[:100] if job.prompt else 'N/A'}...", "info")
        job.add_log(f"🎬 Model: {job.model}", "info")
        job.add_log(f"📐 Resolution: {job.resolution}, Aspect Ratio: {job.aspect_ratio}", "info")
        if job.duration_seconds:
            job.add_log(f"⏱️  Duration: {job.duration_seconds}s", "info")
        
        job.progress_percentage = 10
        job.status_message = "Calling Google Veo 3.1 API..."
        db.commit()
        
        # 4. Call Google Veo API using new genai SDK
        if not genai_client:
            raise Exception("GenAI client not initialized. GOOGLE_API_KEY might be missing.")
        
        try:
            job.add_log("☁️  Calling Google Veo 3.1 API...", "info")
            
            # Build configuration
            config_dict = {}
            
            # Add aspect ratio if specified
            if job.aspect_ratio:
                config_dict['aspectRatio'] = job.aspect_ratio
            
            # Add resolution if specified  
            if job.resolution:
                config_dict['resolution'] = job.resolution
            
            # Add duration in seconds (integer, not string with 's')
            if job.duration_seconds:
                config_dict['durationSeconds'] = job.duration_seconds
            
            # Create config object
            config = types.GenerateVideosConfig(**config_dict) if config_dict else None
            
            if config:
                job.add_log(f"⚙️  Config: {config_dict}", "info")
            
            # Model name should be: veo-3.1-generate-preview (not full path)
            model_name = job.model
            if model_name.startswith("models/"):
                model_name = model_name.split("/")[-1]
            
            # Call generate_videos with the new SDK
            job.add_log(f"🎯 Using model: {model_name}", "info")
            
            operation = genai_client.models.generate_videos(
                model=model_name,
                prompt=job.prompt or "A beautiful video",
                config=config
            )
            
            job.google_operation_name = operation.name if hasattr(operation, 'name') else str(operation)
            job.add_log(f"✅ Operation started: {job.google_operation_name[:50]}...", "info")
            job.progress_percentage = 15
            job.status_message = "Video generation in progress..."
            db.commit()
            
        except Exception as e:
            job.status = "FAILED"
            job.error_message = f"Failed to start generation: {str(e)}"
            job.add_log(f"❌ API error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 5. Wait for generation to complete
        job.add_log("⏳ Waiting for video generation (this may take several minutes)...", "info")
        
        try:
            max_wait_seconds = 900  # 15 minutes
            start_time = time.time()
            poll_interval = 10  # Check every 10 seconds
            
            # Poll the operation status using client.operations.get()
            # as per official documentation: https://ai.google.dev/gemini-api/docs/video
            while (time.time() - start_time) < max_wait_seconds:
                # Check if operation is done
                if operation.done:
                    # Check for errors
                    if operation.error:
                        raise Exception(f"Video generation failed: {operation.error}")
                    
                    # Success! Extract video URI from response
                    if not operation.response:
                        raise ValueError("Operation completed but no response found")
                    
                    response = operation.response
                    video_uri = None
                    
                    # Try to get video URI from generated_videos list
                    if hasattr(response, 'generated_videos') and response.generated_videos:
                        first_video = response.generated_videos[0]
                        if hasattr(first_video, 'video'):
                            if hasattr(first_video.video, 'uri'):
                                video_uri = first_video.video.uri
                            elif hasattr(first_video.video, 'url'):
                                video_uri = first_video.video.url
                    
                    if not video_uri:
                        raise ValueError(f"No video URI found in response: {response}")
                    
                    job.google_result_uri = video_uri
                    job.add_log(f"✅ Video generated! URI: {video_uri[:50]}...", "info")
                    job.progress_percentage = 70
                    job.status_message = "Downloading video..."
                    db.commit()
                    break
                
                # Not done yet, update progress and wait
                elapsed = time.time() - start_time
                progress = min(15 + int((elapsed / max_wait_seconds) * 50), 65)
                if job.progress_percentage != progress:
                    job.progress_percentage = progress
                    job.status_message = f"Generating video... ({int(elapsed)}s elapsed)"
                    db.commit()
                
                # Wait before next poll
                time.sleep(poll_interval)
                
                # Refresh operation status
                operation = genai_client.operations.get(operation)
            
            else:
                # Timeout reached
                raise TimeoutError("Video generation exceeded 15 minute timeout")
                
        except Exception as e:
            job.status = "FAILED"
            job.error_message = f"Generation failed: {str(e)}"
            job.add_log(f"❌ Error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 6. Download video from Google
        job.add_log(f"📥 Downloading video from Google...", "info")
        job.progress_percentage = 75
        db.commit()
        
        try:
            # Google requires API key authentication for downloading videos
            headers = {
                'x-goog-api-key': GOOGLE_API_KEY
            }
            response = requests.get(job.google_result_uri, headers=headers, stream=True, timeout=120)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                temp_file_path = tmp_file.name
            
            job.add_log(f"✅ Downloaded {os.path.getsize(temp_file_path) / 1024 / 1024:.2f} MB", "info")
            job.progress_percentage = 85
            db.commit()
            
        except Exception as e:
            job.status = "FAILED"
            job.error_message = f"Failed to download video: {str(e)}"
            job.add_log(f"❌ Download error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # 7. Upload to Cloudinary
        job.add_log("☁️  Uploading to storage...", "info")
        job.progress_percentage = 90
        job.status_message = "Uploading video to storage..."
        db.commit()
        
        try:
            cloudinary_result = upload_video_to_cloudinary(temp_file_path, job.id)
            job.cloudinary_url = cloudinary_result["url"]
            job.cloudinary_public_id = cloudinary_result["public_id"]
            job.add_log(f"✅ Video uploaded: {job.cloudinary_url[:50]}...", "info")
            
            # Clean up temp file
            os.remove(temp_file_path)
            
        except Exception as e:
            job.status = "FAILED"
            job.error_message = f"Failed to upload video: {str(e)}"
            job.add_log(f"❌ Upload error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
            # Clean up temp file even on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return
        
        # 8. Success!
        job.status = "SUCCEEDED"
        job.status_message = "Video generation completed successfully"
        job.progress_percentage = 100
        job.completed_at = datetime.utcnow()
        job.add_log("🎉 Job completed successfully!", "info")
        db.commit()
        
    except Exception as e:
        # Catch-all for unexpected errors
        try:
            job.status = "FAILED"
            job.error_message = f"Unexpected error: {str(e)}"
            job.add_log(f"❌ Unexpected error: {str(e)}", "error")
            job.completed_at = datetime.utcnow()
            db.commit()
        except:
            print(f"❌ Failed to update job status: {e}")
    
    finally:
        db.close()

