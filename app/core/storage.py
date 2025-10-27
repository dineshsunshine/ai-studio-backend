"""
Cloud storage service for handling file uploads
Supports Google Cloud Storage and Cloudinary
"""
import os
from typing import BinaryIO, Optional
import uuid
from datetime import timedelta
import mimetypes


class StorageService:
    """
    Storage service for uploading and managing files in cloud storage.
    Supports: Cloudinary (recommended), Google Cloud Storage, and Local Storage.
    
    Priority: Cloudinary > GCS > Local
    """
    
    def __init__(self):
        # Cloudinary configuration (recommended for production)
        self.use_cloudinary = os.getenv("USE_CLOUDINARY", "false").lower() == "true"
        
        # GCS configuration (alternative cloud storage)
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "ai-studio-models")
        self.use_gcs = os.getenv("USE_GCS", "false").lower() == "true"
        
        # Use assets directory for better organization
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.local_upload_dir = os.path.join(base_dir, "assets", "images")
        
        # Create local upload directory structure
        if not self.use_gcs:
            os.makedirs(os.path.join(self.local_upload_dir, "models"), exist_ok=True)
            os.makedirs(os.path.join(self.local_upload_dir, "generated"), exist_ok=True)
            os.makedirs(os.path.join(self.local_upload_dir, "uploads"), exist_ok=True)
            os.makedirs(os.path.join(self.local_upload_dir, "looks"), exist_ok=True)
            os.makedirs(os.path.join(self.local_upload_dir, "products"), exist_ok=True)
        
        # Initialize Cloudinary if enabled
        self.cloudinary_service = None
        if self.use_cloudinary:
            try:
                from app.core.cloudinary_storage import cloudinary_storage
                if cloudinary_storage.is_enabled():
                    self.cloudinary_service = cloudinary_storage
                    print("✅ Using Cloudinary for image storage")
                else:
                    print("⚠️  Cloudinary configuration incomplete")
                    self.use_cloudinary = False
            except Exception as e:
                print(f"⚠️  Could not initialize Cloudinary: {e}")
                self.use_cloudinary = False
        
        # Initialize GCS if enabled (and Cloudinary not enabled)
        self.client = None
        self.bucket = None
        
        if self.use_gcs and not self.use_cloudinary:
            try:
                from google.cloud import storage
                self.client = storage.Client()
                self.bucket = self.client.bucket(self.bucket_name)
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize GCS client: {e}")
                print("📁 Falling back to local file storage")
                self.use_gcs = False
    
    def upload_file(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        content_type: Optional[str] = None,
        folder: str = "models"
    ) -> str:
        """
        Upload a file to cloud storage and return the public URL.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            content_type: MIME type of the file
            folder: Storage folder (models, looks, products, etc.)
            
        Returns:
            Public URL to the uploaded file
        """
        # Priority: Cloudinary > GCS > Local
        if self.use_cloudinary and self.cloudinary_service:
            return self.cloudinary_service.upload_file(file_data, folder, filename)
        elif self.use_gcs:
            # Generate unique filename for GCS
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"
            return self._upload_to_gcs(file_data, unique_filename, content_type)
        else:
            # Generate unique filename for local storage
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"
            return self._upload_to_local(file_data, unique_filename)
    
    def _upload_to_gcs(
        self, 
        file_data: BinaryIO, 
        filename: str, 
        content_type: Optional[str]
    ) -> str:
        """Upload file to Google Cloud Storage"""
        try:
            from google.cloud import storage
            
            blob = self.bucket.blob(filename)
            
            # Determine content type
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
            
            # Upload file
            file_data.seek(0)  # Reset file pointer
            blob.upload_from_file(file_data, content_type=content_type)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Return public URL
            return blob.public_url
        except Exception as e:
            raise Exception(f"Failed to upload to GCS: {str(e)}")
    
    def _upload_to_local(self, file_data: BinaryIO, filename: str) -> str:
        """Upload file to local storage (for development/testing)"""
        try:
            # Create full path
            file_path = os.path.join(self.local_upload_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            file_data.seek(0)  # Reset file pointer
            with open(file_path, "wb") as f:
                f.write(file_data.read())
            
            # Return PUBLIC URL (using ngrok or base URL)
            # Try to load from config settings first, then environment variables
            try:
                from app.core.config import settings
                public_url = getattr(settings, 'NGROK_PUBLIC_URL', None)
                if not public_url:
                    public_url = os.getenv("NGROK_PUBLIC_URL", os.getenv("BASE_URL", "http://localhost:8000"))
            except:
                # Fallback to environment variable
                public_url = os.getenv("NGROK_PUBLIC_URL", os.getenv("BASE_URL", "http://localhost:8000"))
            
            # Determine if we're using ngrok (has /AIStudio prefix) or production (no prefix)
            if "ngrok" in public_url or "localhost:8888" in public_url:
                # Development: use /AIStudio prefix
                public_url = public_url.rstrip('/AIStudio').rstrip('/')
                return f"{public_url}/AIStudio/assets/images/{filename}"
            else:
                # Production: no prefix
                public_url = public_url.rstrip('/')
                return f"{public_url}/assets/images/{filename}"
        except Exception as e:
            raise Exception(f"Failed to upload to local storage: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from cloud storage.
        
        Args:
            file_url: Public URL of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Detect storage type from URL
        if "cloudinary.com" in file_url and self.cloudinary_service:
            return self.cloudinary_service.delete_file(file_url)
        elif self.use_gcs and "googleapis.com" in file_url:
            return self._delete_from_gcs(file_url)
        else:
            return self._delete_from_local(file_url)
    
    def _delete_from_gcs(self, file_url: str) -> bool:
        """Delete file from Google Cloud Storage"""
        try:
            # Extract blob name from URL
            # Format: https://storage.googleapis.com/{bucket_name}/{blob_name}
            parts = file_url.split(f"{self.bucket_name}/")
            if len(parts) < 2:
                return False
            
            blob_name = parts[1]
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete from GCS: {e}")
            return False
    
    def _delete_from_local(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            # Extract filename from URL
            # Format: http://domain/AIStudio/assets/{filename}
            if "/assets/" in file_url:
                filename = file_url.split("/assets/")[-1]
            elif "/uploads/" in file_url:  # Backward compatibility
                filename = file_url.split("/uploads/")[-1]
            else:
                return False
                
            file_path = os.path.join(self.local_upload_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"⚠️  Warning: Failed to delete from local storage: {e}")
            return False


# Global storage service instance
storage_service = StorageService()

