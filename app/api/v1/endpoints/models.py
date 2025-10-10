"""
Models API endpoints (User-scoped)
Unified endpoint for creating models (upload or AI generation)
"""
import uuid
import io
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.model import Model as DBModel
from app.models.user import User, UserRole
from app.schemas.model import ModelResponse, ModelListResponse
from app.core.storage import StorageService

router = APIRouter()
storage_service = StorageService()

# Mock AI generation function (will be replaced with actual AI later)
async def generate_model_image(name: str, prompt_details: str) -> str:
    """Generate a placeholder image for AI generation"""
    from PIL import Image, ImageDraw
    from io import BytesIO
    import uuid
    
    # Create placeholder image
    img = Image.new('RGB', (800, 1200), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)
    draw.text((50, 500), f"AI Generated: {name}\n{prompt_details[:100]}", fill=(255, 255, 255))
    
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Create mock upload file
    class MockUploadFile:
        def __init__(self, file_content, filename, content_type):
            self.file = BytesIO(file_content)
            self.filename = filename
            self.content_type = content_type
            self.file.seek(0)
        
        def read(self):
            return self.file.read()
    
    mock_file = MockUploadFile(img_byte_arr.getvalue(), f"generated/{uuid.uuid4()}.png", "image/png")
    image_url = storage_service.upload_file(mock_file.file, mock_file.filename, mock_file.content_type)
    return image_url


@router.get("/", response_model=ModelListResponse)
async def list_models(
    all: bool = Query(False, description="Show all models (admin only)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List models with pagination.
    
    - Regular users see only their own models
    - Admins can use ?all=true to see all models
    
    Query Parameters:
    - all: Show all models (admin only)
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return
    
    Returns:
    - List of model objects with total count
    """
    query = db.query(DBModel)
    
    # Filter by user unless admin requests all models
    if not (all and current_user.role == UserRole.ADMIN):
        query = query.filter(DBModel.user_id == str(current_user.id))
    
    total = query.count()
    models = query.offset(skip).limit(limit).all()
    
    return {"models": models, "total": total}


@router.post("/", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    name: str = Form(..., description="Name of the model"),
    image: Optional[UploadFile] = File(None, description="Image file to upload (optional)"),
    promptDetails: Optional[str] = Form(None, alias="prompt_details", description="AI generation prompt (optional)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new model - either by uploading an image OR by AI generation.
    
    **Authentication required.**
    
    **Two ways to create a model:**
    
    1. **Upload an existing image:**
       - Provide: name + image file
       - Example: FormData with 'name' and 'image' fields
    
    2. **Generate with AI:**
       - Provide: name + promptDetails
       - Example: FormData with 'name' and 'promptDetails' fields
    
    **You must provide EITHER an image file OR promptDetails, but not both.**
    
    Form Fields:
    - name (required): Name of the model
    - image (optional): Image file (JPEG, PNG, etc.)
    - promptDetails (optional): Text description for AI generation
    
    Returns:
    - The newly created model object with public image URL
    """
    # Validate: Must provide either image OR promptDetails
    if image and promptDetails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either 'image' (for upload) OR 'promptDetails' (for AI generation), not both."
        )
    
    if not image and not promptDetails:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either 'image' (for upload) OR 'promptDetails' (for AI generation)."
        )
    
    try:
        image_url = None
        prompt_used = None
        
        # Path 1: Upload existing image
        if image:
            # Validate file type
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded file must be an image (JPEG, PNG, etc.)"
                )
            
            # Upload image to storage
            file_data = await image.read()
            file_stream = io.BytesIO(file_data)
            filename = f"models/{image.filename}"
            image_url = storage_service.upload_file(file_stream, filename, image.content_type)
            print(f"✅ Uploaded image: {image_url}")
        
        # Path 2: Generate with AI
        elif promptDetails:
            # Generate image using AI
            image_url = await generate_model_image(name, promptDetails)
            prompt_used = promptDetails
            print(f"✅ Generated AI image: {image_url}")
        
        # Create model record in database with user association
        db_model = DBModel(
            name=name,
            image_url=image_url,
            prompt_details=prompt_used,
            user_id=str(current_user.id)  # Associate with current user
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        
        print(f"✅ Created model: {db_model.id} - {db_model.name} for user {current_user.email}")
        return db_model
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create model: {str(e)}"
        )


@router.get("/{model_id}/", response_model=ModelResponse)
@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single model by its ID.
    
    - Users can only view their own models
    - Admins can view any model
    
    Path Parameters:
    - model_id: UUID of the model (as string)
    
    Returns:
    - Model object with all details
    """
    model = db.query(DBModel).filter(DBModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id {model_id} not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and model.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this model"
        )
    
    return model


@router.delete("/{model_id}/", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a model by its ID.
    
    - Users can only delete their own models
    - Admins can delete any model
    
    This will:
    1. Delete the associated image from storage
    2. Delete the model record from database
    
    Path Parameters:
    - model_id: UUID of the model to delete (as string)
    
    Returns:
    - 204 No Content on success
    """
    model = db.query(DBModel).filter(DBModel.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with id {model_id} not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and model.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this model"
        )
    
    try:
        # Delete image from storage
        storage_service.delete_file(model.image_url)
        
        # Delete from database
        db.delete(model)
        db.commit()
        
        print(f"✅ Deleted model: {model_id} by user {current_user.email}")
        return None
        
    except Exception as e:
        print(f"❌ Error deleting model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete model: {str(e)}"
        )
