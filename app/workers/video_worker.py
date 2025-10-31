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
        job.status_message = "Preparing images and calling Google Veo 3.1 API..."
        db.commit()
        
        # 4. Upload images to Google File API (if provided)
        initial_image_file = None
        end_frame_file = None
        reference_image_files = []
        
        if job.initial_image_path and os.path.exists(job.initial_image_path):
            try:
                job.add_log(f"📤 Preparing initial image...", "info")
                # Read image bytes and determine MIME type
                with open(job.initial_image_path, 'rb') as f:
                    image_bytes = f.read()
                
                # Detect MIME type from file extension
                import mimetypes
                mime_type = mimetypes.guess_type(job.initial_image_path)[0] or 'image/png'
                
                # Create Image object for Veo
                initial_image_file = types.Image(
                    image_bytes=image_bytes,
                    mime_type=mime_type
                )
                job.add_log(f"✅ Initial image prepared: {len(image_bytes)} bytes, {mime_type}", "info")
            except Exception as e:
                job.add_log(f"⚠️  Failed to prepare initial image: {str(e)}", "warning")
        
        if job.end_frame_path and os.path.exists(job.end_frame_path):
            try:
                job.add_log(f"📤 Preparing end frame...", "info")
                with open(job.end_frame_path, 'rb') as f:
                    image_bytes = f.read()
                import mimetypes
                mime_type = mimetypes.guess_type(job.end_frame_path)[0] or 'image/png'
                end_frame_file = types.Image(
                    image_bytes=image_bytes,
                    mime_type=mime_type
                )
                job.add_log(f"✅ End frame prepared: {len(image_bytes)} bytes, {mime_type}", "info")
            except Exception as e:
                job.add_log(f"⚠️  Failed to prepare end frame: {str(e)}", "warning")
        
        if job.reference_images_paths:
            for ref_path in job.reference_images_paths:
                if os.path.exists(ref_path):
                    try:
                        with open(ref_path, 'rb') as f:
                            image_bytes = f.read()
                        import mimetypes
                        mime_type = mimetypes.guess_type(ref_path)[0] or 'image/png'
                        ref_file = types.Image(
                            image_bytes=image_bytes,
                            mime_type=mime_type
                        )
                        reference_image_files.append(ref_file)
                        job.add_log(f"✅ Reference image prepared: {len(image_bytes)} bytes", "info")
                    except Exception as e:
                        job.add_log(f"⚠️  Failed to prepare reference image: {str(e)}", "warning")
        
        # 5. Call Google Veo API using new genai SDK
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
            
            # Add audio generation option if specified
            if job.generate_audio:
                config_dict['generateAudio'] = True
                job.add_log("🔊 Audio generation enabled", "info")
            
            # Log which images are being used (initial image goes as top-level param, not in config)
            if initial_image_file:
                job.add_log(f"🖼️  Using initial image (Image object)", "info")
            
            # Add end frame to config if uploaded
            if end_frame_file:
                config_dict['lastFrame'] = end_frame_file
                job.add_log(f"🖼️  Using end frame (Image object)", "info")
            
            # Add reference images to config if uploaded
            if reference_image_files:
                config_dict['referenceImages'] = reference_image_files
                job.add_log(f"🖼️  Using {len(reference_image_files)} reference image(s)", "info")
            
            # Create config object
            config = types.GenerateVideosConfig(**config_dict) if config_dict else None
            
            if config:
                job.add_log(f"⚙️  Config: {str(config_dict)[:200]}...", "info")
            
            # Model name should be: veo-3.1-generate-preview (not full path)
            model_name = job.model
            if model_name.startswith("models/"):
                model_name = model_name.split("/")[-1]
            
            # Call generate_videos with the new SDK
            job.add_log(f"🎯 Using model: {model_name}", "info")
            
            # Capture Veo request for monitoring
            veo_config_for_log = dict(config_dict) if config_dict else {}
            # Replace Image objects with descriptors for logging
            if 'lastFrame' in veo_config_for_log:
                veo_config_for_log['lastFrame'] = "Image object" if end_frame_file else None
            if 'referenceImages' in veo_config_for_log:
                veo_config_for_log['referenceImages'] = [f"Image {i+1}" for i in range(len(reference_image_files))]
            
            job.veo_request = {
                "model": model_name,
                "prompt": job.prompt or "A beautiful video",
                "image": "Image object" if initial_image_file else None,  # Top-level param
                "config": veo_config_for_log,
                "timestamp": datetime.utcnow().isoformat()
            }
            db.commit()
            
            # Call Google Veo 3.1 API with image parameter
            operation = genai_client.models.generate_videos(
                model=model_name,
                prompt=job.prompt or "A beautiful video",
                image=initial_image_file,  # Pass initial image as top-level parameter
                config=config
            )
            
            job.google_operation_name = operation.name if hasattr(operation, 'name') else str(operation)
            job.add_log(f"✅ Operation started: {job.google_operation_name[:50]}...", "info")
            
            # Capture initial Veo response
            job.veo_response = {
                "operation_name": operation.name if hasattr(operation, 'name') else str(operation),
                "done": operation.done if hasattr(operation, 'done') else None,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "initiated"
            }
            
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
                    
                    # Update Veo response with final result
                    job.veo_response = {
                        "operation_name": operation.name if hasattr(operation, 'name') else str(operation),
                        "done": True,
                        "video_uri": video_uri,
                        "status": "completed",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
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
        
        # Capture final backend response
        job.backend_response = {
            "status": "SUCCEEDED",
            "cloudinary_url": job.cloudinary_url,
            "cloudinary_public_id": job.cloudinary_public_id,
            "progress": 100,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Clean up temporary image files
        if job.initial_image_path and os.path.exists(job.initial_image_path):
            try:
                job_dir = os.path.dirname(job.initial_image_path)
                import shutil
                shutil.rmtree(job_dir, ignore_errors=True)
                job.add_log("🧹 Cleaned up temporary files", "info")
            except Exception as e:
                job.add_log(f"⚠️  Failed to clean up temp files: {str(e)}", "warning")
        
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

