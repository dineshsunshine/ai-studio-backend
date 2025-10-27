"""
Cloudinary storage service for handling file uploads
"""
import os
from typing import BinaryIO, Optional
import uuid


class CloudinaryStorage:
    """
    Storage service using Cloudinary for cloud-based image hosting.
    """
    
    def __init__(self):
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        self.api_key = os.getenv("CLOUDINARY_API_KEY")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET")
        self.use_cloudinary = os.getenv("USE_CLOUDINARY", "false").lower() == "true"
        
        self.cloudinary = None
        
        if self.use_cloudinary:
            if not all([self.cloud_name, self.api_key, self.api_secret]):
                print("⚠️  Cloudinary credentials not found. Please set:")
                print("   CLOUDINARY_CLOUD_NAME")
                print("   CLOUDINARY_API_KEY")
                print("   CLOUDINARY_API_SECRET")
                print("   USE_CLOUDINARY=true")
                print("📁 Falling back to local file storage")
                self.use_cloudinary = False
            else:
                try:
                    import cloudinary
                    import cloudinary.uploader
                    
                    cloudinary.config(
                        cloud_name=self.cloud_name,
                        api_key=self.api_key,
                        api_secret=self.api_secret,
                        secure=True
                    )
                    
                    self.cloudinary = cloudinary
                    print(f"✅ Cloudinary configured: {self.cloud_name}")
                except ImportError:
                    print("⚠️  Cloudinary package not installed. Install with: pip install cloudinary")
                    print("📁 Falling back to local file storage")
                    self.use_cloudinary = False
                except Exception as e:
                    print(f"⚠️  Error configuring Cloudinary: {e}")
                    print("📁 Falling back to local file storage")
                    self.use_cloudinary = False
    
    def is_enabled(self) -> bool:
        """Check if Cloudinary is enabled and properly configured"""
        return self.use_cloudinary and self.cloudinary is not None
    
    def upload_file(
        self, 
        file_data: BinaryIO, 
        folder: str = "models",
        filename: Optional[str] = None
    ) -> str:
        """
        Upload a file to Cloudinary and return the public URL.
        
        Args:
            file_data: Binary file data
            folder: Cloudinary folder (e.g., 'models', 'looks', 'products')
            filename: Optional custom filename (will generate UUID if not provided)
            
        Returns:
            Public URL to the uploaded file
        """
        if not self.is_enabled():
            raise Exception("Cloudinary is not enabled or configured")
        
        try:
            # Generate unique public_id if filename not provided
            if filename:
                # Remove extension from filename
                public_id = os.path.splitext(filename)[0]
            else:
                public_id = str(uuid.uuid4())
            
            # Full public_id with folder
            full_public_id = f"{folder}/{public_id}"
            
            # Reset file pointer
            file_data.seek(0)
            
            # Upload to Cloudinary
            result = self.cloudinary.uploader.upload(
                file_data,
                public_id=full_public_id,
                resource_type="image",
                overwrite=False,
                unique_filename=True,
                use_filename=False
            )
            
            # Return secure URL
            return result.get('secure_url')
            
        except Exception as e:
            raise Exception(f"Failed to upload to Cloudinary: {str(e)}")
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from Cloudinary.
        
        Args:
            file_url: Public URL of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            # Extract public_id from URL
            # Format: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{ext}
            if "cloudinary.com" not in file_url:
                return False
            
            # Parse URL to get public_id
            parts = file_url.split('/upload/')
            if len(parts) < 2:
                return False
            
            # Get everything after /upload/v{version}/
            path_with_version = parts[1]
            
            # Remove version number (e.g., v1234567890/)
            if path_with_version.startswith('v'):
                path_parts = path_with_version.split('/', 1)
                if len(path_parts) >= 2:
                    public_id_with_ext = path_parts[1]
                else:
                    public_id_with_ext = path_with_version
            else:
                public_id_with_ext = path_with_version
            
            # Remove extension
            public_id = os.path.splitext(public_id_with_ext)[0]
            
            # Delete from Cloudinary
            result = self.cloudinary.uploader.destroy(public_id, resource_type="image")
            
            return result.get('result') == 'ok'
            
        except Exception as e:
            print(f"⚠️  Error deleting from Cloudinary: {e}")
            return False
    
    def get_url(self, public_id: str, folder: str = "models") -> str:
        """
        Get Cloudinary URL for a given public_id.
        
        Args:
            public_id: The public ID of the image
            folder: The folder where the image is stored
            
        Returns:
            Secure Cloudinary URL
        """
        if not self.is_enabled():
            raise Exception("Cloudinary is not enabled")
        
        full_public_id = f"{folder}/{public_id}"
        return self.cloudinary.CloudinaryImage(full_public_id).build_url(secure=True)


# Global instance
cloudinary_storage = CloudinaryStorage()


