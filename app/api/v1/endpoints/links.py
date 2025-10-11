"""
API endpoints for Links (shareable collections of looks)
"""
import random
import string
import io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.link import Link, link_looks
from app.models.look import Look
from app.schemas.link import (
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkListResponse,
    SharedLinkResponse
)
from app.schemas.look import LookResponse
from app.schemas.product import ProductResponse
import os

router = APIRouter()


def generate_link_id(length: int = 8) -> str:
    """Generate a unique alphanumeric link ID"""
    # Use uppercase letters and numbers for readability
    chars = string.ascii_uppercase + string.digits
    # Exclude confusing characters: 0, O, 1, I, L
    chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '').replace('L', '')
    return ''.join(random.choices(chars, k=length))


def get_short_url(link_id: str) -> str:
    """Generate the full short URL for a link"""
    # Check if we're on production (Render) or development (ngrok/local)
    base_url = os.getenv("BASE_URL")
    ngrok_url = os.getenv("NGROK_PUBLIC_URL")
    
    if base_url:
        # Production (Render) - no prefix needed
        public_url = base_url.rstrip('/')
        return f"{public_url}/l/{link_id}"
    elif ngrok_url:
        # Development (ngrok) - needs /AIStudio prefix for reverse proxy
        public_url = ngrok_url.rstrip('/')
        return f"{public_url}/AIStudio/l/{link_id}"
    else:
        # Local fallback
        return f"http://localhost:8000/l/{link_id}"


def serialize_link(link: Link, db: Session = None) -> dict:
    """Serialize a Link object to dictionary with ordered looks"""
    # Get looks ordered by position from junction table
    from sqlalchemy import text
    if db:
        result = db.execute(
            text("""
                SELECT l.*, ll.position 
                FROM looks l
                JOIN link_looks ll ON l.id = ll.look_id
                WHERE ll.link_id = :link_id
                ORDER BY ll.position
            """),
            {"link_id": link.id}
        )
        ordered_look_ids = [row[0] for row in result]
        # Sort looks based on the ordered IDs
        looks_dict = {str(look.id): look for look in link.looks}
        ordered_looks = [looks_dict[look_id] for look_id in ordered_look_ids if look_id in looks_dict]
    else:
        ordered_looks = link.looks
    
    return {
        "id": str(link.id),
        "linkId": link.link_id,
        "title": link.title,
        "description": link.description,
        "coverImageUrl": link.cover_image_url,
        "shortUrl": get_short_url(link.link_id),
        "looks": [
            {
                "id": str(look.id),
                "title": look.title,
                "notes": look.notes,
                "generatedImageUrl": look.generated_image_url,
                "products": [
                    {
                        "id": str(product.id),
                        "sku": product.sku,
                        "name": product.name,
                        "designer": product.designer,
                        "price": product.price,
                        "productUrl": product.product_url,
                        "thumbnailUrl": product.thumbnail_url,
                        "createdAt": product.created_at.isoformat()
                    }
                    for product in look.products
                ],
                "createdAt": look.created_at.isoformat(),
                "updatedAt": look.updated_at.isoformat()
            }
            for look in ordered_looks
        ],
        "createdAt": link.created_at.isoformat(),
        "updatedAt": link.updated_at.isoformat()
    }


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link_data: LinkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new shareable link with a collection of looks.
    
    **Authentication required.**
    
    - Users can only include their own looks in links
    - Generates a unique alphanumeric link ID
    - Returns the short URL to share with clients
    
    Request Body:
    - title: Link title (required)
    - description: Link description (optional)
    - lookIds: Array of look UUIDs to include (required, min 1)
    
    Returns the created link with short URL.
    """
    # Verify all looks exist and belong to the user
    looks = db.query(Look).filter(
        Look.id.in_(link_data.lookIds),
        Look.user_id == str(current_user.id)
    ).all()
    
    if len(looks) != len(link_data.lookIds):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more looks not found or do not belong to you"
        )
    
    # Generate unique link ID
    link_id = generate_link_id()
    # Ensure uniqueness
    while db.query(Link).filter(Link.link_id == link_id).first():
        link_id = generate_link_id()
    
    # Create link
    new_link = Link(
        user_id=str(current_user.id),
        title=link_data.title,
        description=link_data.description,
        link_id=link_id
    )
    
    db.add(new_link)
    db.flush()  # Get the link ID
    
    # Add looks to link with position
    from sqlalchemy import text
    for position, look_id in enumerate(link_data.lookIds):
        db.execute(
            text("INSERT INTO link_looks (link_id, look_id, position) VALUES (:link_id, :look_id, :position)"),
            {"link_id": new_link.id, "look_id": look_id, "position": position}
        )
    
    db.commit()
    db.refresh(new_link)
    
    return LinkResponse(**serialize_link(new_link))


@router.get("/", response_model=LinkListResponse)
async def list_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all links created by the authenticated user.
    
    **Authentication required.**
    
    - Users see only their own links
    - Supports pagination
    
    Query Parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    
    Returns paginated list of links with their looks.
    """
    # Get user's links
    query = db.query(Link).filter(Link.user_id == str(current_user.id))
    
    total = query.count()
    links = query.order_by(Link.created_at.desc()).offset(skip).limit(limit).all()
    
    return LinkListResponse(
        links=[LinkResponse(**serialize_link(link)) for link in links],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a single link by its database ID.
    
    **Authentication required.**
    
    - Users can only view their own links
    - Admins can view any link
    
    Path Parameters:
    - link_id: UUID of the link
    
    Returns the complete link with all looks and products.
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and link.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this link"
        )
    
    return LinkResponse(**serialize_link(link))


@router.patch("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    link_data: LinkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a link's client information or looks.
    
    **Authentication required.**
    
    - Users can only update their own links
    - Can update client name, phone, or the collection of looks
    
    Path Parameters:
    - link_id: UUID of the link to update
    
    Request Body (all optional):
    - title: Updated link title
    - description: Updated link description
    - lookIds: Updated array of look UUIDs
    
    Returns the updated link.
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership
    if link.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this link"
        )
    
    # Update link information
    if link_data.title is not None:
        link.title = link_data.title
    
    if link_data.description is not None:
        link.description = link_data.description
    
    # Update looks if provided
    if link_data.lookIds is not None:
        # Verify all looks exist and belong to the user
        looks = db.query(Look).filter(
            Look.id.in_(link_data.lookIds),
            Look.user_id == str(current_user.id)
        ).all()
        
        if len(looks) != len(link_data.lookIds):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more looks not found or do not belong to you"
            )
        
        # Clear existing associations
        from sqlalchemy import text
        db.execute(
            text("DELETE FROM link_looks WHERE link_id = :link_id"),
            {"link_id": link.id}
        )
        
        # Add new associations with position
        for position, look_id in enumerate(link_data.lookIds):
            db.execute(
                text("INSERT INTO link_looks (link_id, look_id, position) VALUES (:link_id, :look_id, :position)"),
                {"link_id": link.id, "look_id": look_id, "position": position}
            )
    
    db.commit()
    db.refresh(link)
    
    return LinkResponse(**serialize_link(link))


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a link.
    
    **Authentication required.**
    
    - Users can only delete their own links
    - Deleting a link does NOT delete the looks (only the link itself)
    
    Path Parameters:
    - link_id: UUID of the link to delete
    
    Returns 204 No Content on success.
    """
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership
    if link.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this link"
        )
    
    db.delete(link)
    db.commit()
    
    return None


@router.get("/shared/{alphanumeric_link_id}", response_model=SharedLinkResponse)
async def get_shared_link(
    alphanumeric_link_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a link by its alphanumeric link ID (for sharing with clients).
    
    **No authentication required** - this is a public endpoint.
    
    Path Parameters:
    - alphanumeric_link_id: The short alphanumeric ID (e.g., "AB12CD34")
    
    Returns the link with all looks and products for client viewing.
    
    This endpoint is designed to be called from the short URL:
    https://yourdomain.com/l/{alphanumeric_link_id}
    """
    link = db.query(Link).filter(Link.link_id == alphanumeric_link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found or has been deleted"
        )
    
    return SharedLinkResponse(
        linkId=link.link_id,
        title=link.title,
        description=link.description,
        coverImageUrl=link.cover_image_url,
        looks=[
            LookResponse(
                id=str(look.id),
                title=look.title,
                notes=look.notes,
                generatedImageUrl=look.generated_image_url,
                products=[
                    ProductResponse(
                        id=str(product.id),
                        sku=product.sku,
                        name=product.name,
                        designer=product.designer,
                        price=product.price,
                        productUrl=product.product_url,
                        thumbnailUrl=product.thumbnail_url,
                        createdAt=product.created_at.isoformat()
                    )
                    for product in look.products
                ],
                createdAt=look.created_at.isoformat(),
                updatedAt=look.updated_at.isoformat()
            )
            for look in link.looks
        ],
        createdAt=link.created_at.isoformat()
    )


@router.put("/{link_id}/cover", response_model=LinkResponse)
async def upload_cover_image(
    link_id: str,
    cover_image: UploadFile = File(..., description="Cover image file"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload or update cover image for a link.
    
    **Authentication required.**
    
    - Users can only update their own links
    - Accepts image files (JPEG, PNG, WebP, GIF)
    - Deletes old cover image if it exists
    - Saves new image to cloud storage
    
    Path Parameters:
    - link_id: UUID of the link
    
    Request Body (multipart/form-data):
    - cover_image: Image file
    
    Returns the updated link with new cover image URL.
    """
    from app.core.storage import storage_service
    
    # Find the link
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership
    if link.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this link"
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
    if cover_image.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Delete old cover image if it exists
    if link.cover_image_url:
        try:
            storage_service.delete_file(link.cover_image_url)
        except Exception as e:
            print(f"Warning: Failed to delete old cover image: {e}")
    
    # Upload new cover image
    try:
        file_data = io.BytesIO(await cover_image.read())
        new_cover_url = storage_service.upload_file(
            file_data=file_data,
            filename=cover_image.filename,
            content_type=cover_image.content_type,
            folder="links"
        )
        
        # Update link with new cover image URL
        link.cover_image_url = new_cover_url
        db.commit()
        db.refresh(link)
        
        return LinkResponse(**serialize_link(link))
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload cover image: {str(e)}"
        )


@router.delete("/{link_id}/cover", response_model=LinkResponse)
async def remove_cover_image(
    link_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove cover image from a link.
    
    **Authentication required.**
    
    - Users can only update their own links
    - Deletes the cover image from cloud storage
    - Sets cover_image_url to null in database
    
    Path Parameters:
    - link_id: UUID of the link
    
    Returns the updated link with cover_image_url set to null.
    """
    from app.core.storage import storage_service
    
    # Find the link
    link = db.query(Link).filter(Link.id == link_id).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership
    if link.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this link"
        )
    
    # Delete cover image if it exists
    if link.cover_image_url:
        try:
            storage_service.delete_file(link.cover_image_url)
        except Exception as e:
            print(f"Warning: Failed to delete cover image: {e}")
    
    # Set cover_image_url to null
    link.cover_image_url = None
    db.commit()
    db.refresh(link)
    
    return LinkResponse(**serialize_link(link))

