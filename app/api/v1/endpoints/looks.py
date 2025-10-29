"""
Looks API endpoints (User-scoped)
"""
import uuid
import base64
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.auth import get_current_user, require_admin
from app.models.look import Look as DBLook
from app.models.product import Product as DBProduct
from app.models.user import User, UserRole
from app.schemas.look import LookCreate, LookUpdate, LookVisibilityUpdate, LookResponse, LookListResponse
from app.core.storage import storage_service

router = APIRouter()


def decode_base64_image(base64_string: str) -> bytes:
    """
    Decode a base64 image string to bytes.
    Handles both with and without data URI prefix.
    """
    try:
        # Remove data URI prefix if present (e.g., "data:image/png;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',', 1)[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        return image_bytes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid base64 image: {str(e)}"
        )


@router.post("/", response_model=LookResponse, status_code=status.HTTP_201_CREATED)
async def create_look(
    look_data: LookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new look with products.
    
    **Authentication required.**
    
    The backend will:
    1. Decode the base64-encoded generated image
    2. Save it to storage (local or cloud)
    3. Decode and save each product thumbnail
    4. Create the look record with all products
    
    Request Body (JSON):
    - title: Optional title for the look
    - notes: Optional notes
    - generatedImageBase64: Base64-encoded main image (required)
    - products: Array of products with thumbnailBase64 (required, min 1)
    
    Returns the created look with all generated URLs.
    """
    try:
        # 1. Process the main generated image
        print(f"📸 Processing generated image for new look...")
        generated_image_bytes = decode_base64_image(look_data.generated_image_base64)
        generated_image_stream = io.BytesIO(generated_image_bytes)
        
        # Upload generated image
        generated_image_filename = f"looks/{uuid.uuid4()}.png"
        generated_image_url = storage_service.upload_file(
            generated_image_stream,
            generated_image_filename,
            "image/png"
        )
        print(f"✅ Uploaded generated image: {generated_image_url}")
        
        # 2. Create the look record with user association
        new_look = DBLook(
            title=look_data.title,
            notes=look_data.notes,
            generated_image_url=generated_image_url,
            user_id=str(current_user.id),  # Associate with current user
            visibility=look_data.visibility.value  # Set visibility
        )
        db.add(new_look)
        db.flush()  # Get the look ID without committing
        
        # 2b. Handle sharing if visibility is SHARED
        if look_data.visibility.value == "shared" and look_data.shared_with_user_ids:
            from app.models.user import User as DBUser
            # Validate that all user IDs exist
            for user_id in look_data.shared_with_user_ids:
                user = db.query(DBUser).filter(DBUser.id == user_id).first()
                if user:
                    new_look.shared_with.append(user)
                else:
                    print(f"⚠️  User {user_id} not found, skipping...")
            print(f"🔗 Shared look with {len(new_look.shared_with)} users")
        
        # 3. Process and create product records
        # Deduplicate products by SKU to prevent duplicates
        seen_skus = set()
        unique_products = []
        for product_data in look_data.products:
            if product_data.sku not in seen_skus:
                seen_skus.add(product_data.sku)
                unique_products.append(product_data)
            else:
                print(f"⚠️  Skipping duplicate product with SKU: {product_data.sku}")
        
        print(f"📦 Processing {len(unique_products)} unique products (removed {len(look_data.products) - len(unique_products)} duplicates)...")
        for product_data in unique_products:
            # Decode and upload product thumbnail
            thumbnail_bytes = decode_base64_image(product_data.thumbnail_base64)
            thumbnail_stream = io.BytesIO(thumbnail_bytes)
            
            # Use SKU in filename if available, otherwise use UUID
            thumbnail_filename = f"products/{product_data.sku or uuid.uuid4()}.png"
            thumbnail_url = storage_service.upload_file(
                thumbnail_stream,
                thumbnail_filename,
                "image/png"
            )
            
            # Create product record
            new_product = DBProduct(
                look_id=new_look.id,
                sku=product_data.sku,
                name=product_data.name,
                designer=product_data.designer,
                price=product_data.price,
                product_url=product_data.product_url,
                thumbnail_url=thumbnail_url
            )
            db.add(new_product)
        
        # 4. Commit all changes
        db.commit()
        db.refresh(new_look)
        
        print(f"✅ Created look {new_look.id} with {len(new_look.products)} products for user {current_user.email}")
        
        # Convert to dict with proper serialization
        from app.schemas.look import SharedUserInfo
        return LookResponse(
            id=str(new_look.id),
            title=new_look.title,
            notes=new_look.notes,
            generatedImageUrl=new_look.generated_image_url,
            visibility=new_look.visibility,
            sharedWith=[
                SharedUserInfo(
                    id=str(user.id),
                    email=user.email,
                    name=user.name
                )
                for user in new_look.shared_with
            ],
            products=[
                {
                    "id": str(p.id),
                    "sku": p.sku,
                    "name": p.name,
                    "designer": p.designer,
                    "price": p.price,
                    "productUrl": p.product_url,
                    "thumbnailUrl": p.thumbnail_url,
                    "createdAt": p.created_at.isoformat()
                }
                for p in new_look.products
            ],
            createdAt=new_look.created_at.isoformat(),
            updatedAt=new_look.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating look: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create look: {str(e)}"
        )


@router.get("/", response_model=LookListResponse)
async def list_looks(
    all: bool = Query(False, description="Show all looks (admin only)"),
    view_type: str = Query(None, description="Filter by view type: 'my_private', 'shared_with_me', 'public'"),
    search: str = Query(None, description="Search looks by title, notes, product name, or SKU"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List looks with pagination, filtering, and search.
    
    **View Type Filters:**
    - my_private: Looks created by you (private or shared)
    - shared_with_me: Looks shared with you by others
    - public: All public looks
    - (no view_type): Defaults to your private looks
    
    **Search:**
    Search across look title, notes, product names, and product SKUs
    
    **Query Parameters:**
    - all: Show all looks (admin only, overrides view_type)
    - view_type: Filter by visibility type
    - search: Search keyword
    - skip: Number of records to skip (default: 0)
    - limit: Maximum number of records to return (default: 100, max: 1000)
    
    Returns a paginated list of looks with their products.
    """
    # Enforce max limit
    if limit > 1000:
        limit = 1000
    
    # Start with base query
    query = db.query(DBLook).distinct()
    
    # Admin can see all looks if requested
    if all and current_user.role == UserRole.ADMIN:
        pass  # No filter, show all
    else:
        # Apply view type filters
        if view_type == "my_private":
            # Looks created by current user
            query = query.filter(DBLook.user_id == str(current_user.id))
        elif view_type == "shared_with_me":
            # Looks shared with current user (not created by them)
            from app.models.look import look_shares
            from app.models.user import User as DBUser
            query = query.join(look_shares).filter(
                look_shares.c.user_id == str(current_user.id),
                DBLook.user_id != str(current_user.id),
                DBLook.visibility == "shared"
            )
        elif view_type == "public":
            # All public looks
            query = query.filter(DBLook.visibility == "public")
        else:
            # Default: show user's own looks
            query = query.filter(DBLook.user_id == str(current_user.id))
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        # Search in look title, notes, or join with products for name/SKU
        query = query.outerjoin(DBProduct).filter(
            (DBLook.title.ilike(search_term)) |
            (DBLook.notes.ilike(search_term)) |
            (DBProduct.name.ilike(search_term)) |
            (DBProduct.sku.ilike(search_term))
        )
    
    total = query.count()
    looks = query.order_by(DBLook.created_at.desc()).offset(skip).limit(limit).all()
    
    # Serialize looks properly
    from app.schemas.look import SharedUserInfo
    serialized_looks = [
        LookResponse(
            id=str(look.id),
            title=look.title,
            notes=look.notes,
            generatedImageUrl=look.generated_image_url,
            visibility=look.visibility,
            sharedWith=[
                SharedUserInfo(
                    id=str(user.id),
                    email=user.email,
                    name=user.name
                )
                for user in look.shared_with
            ],
            products=[
                {
                    "id": str(p.id),
                    "sku": p.sku,
                    "name": p.name,
                    "designer": p.designer,
                    "price": p.price,
                    "productUrl": p.product_url,
                    "thumbnailUrl": p.thumbnail_url,
                    "createdAt": p.created_at.isoformat()
                }
                for p in look.products
            ],
            createdAt=look.created_at.isoformat(),
            updatedAt=look.updated_at.isoformat()
        )
        for look in looks
    ]
    
    return {
        "looks": serialized_looks,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{look_id}/", response_model=LookResponse)
@router.get("/{look_id}", response_model=LookResponse)
async def get_look(
    look_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single look by its ID.
    
    - Users can only view their own looks
    - Admins can view any look
    
    Returns the complete look with all product details.
    """
    # The GUID type will handle UUID format conversion automatically
    look = db.query(DBLook).filter(DBLook.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and look.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this look"
        )
    
    from app.schemas.look import SharedUserInfo
    return LookResponse(
        id=str(look.id),
        title=look.title,
        notes=look.notes,
        generatedImageUrl=look.generated_image_url,
        visibility=look.visibility,
        sharedWith=[
            SharedUserInfo(
                id=str(user.id),
                email=user.email,
                name=user.name
            )
            for user in look.shared_with
        ],
        products=[
            {
                "id": str(p.id),
                "sku": p.sku,
                "name": p.name,
                "designer": p.designer,
                "price": p.price,
                "productUrl": p.product_url,
                "thumbnailUrl": p.thumbnail_url,
                "createdAt": p.created_at.isoformat()
            }
            for p in look.products
        ],
        createdAt=look.created_at.isoformat(),
        updatedAt=look.updated_at.isoformat()
    )


@router.patch("/{look_id}/", response_model=LookResponse)
@router.patch("/{look_id}", response_model=LookResponse)
async def update_look(
    look_id: str,
    look_update: LookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a look's title or notes.
    
    - Users can only update their own looks
    - Admins can update any look
    
    Only title and notes can be updated.
    Products and images cannot be modified after creation.
    """
    # The GUID type will handle UUID format conversion automatically
    look = db.query(DBLook).filter(DBLook.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and look.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this look"
        )
    
    # Update only provided fields
    if look_update.title is not None:
        look.title = look_update.title
    if look_update.notes is not None:
        look.notes = look_update.notes
    
    try:
        db.commit()
        db.refresh(look)
        
        from app.schemas.look import SharedUserInfo
        return LookResponse(
            id=str(look.id),
            title=look.title,
            notes=look.notes,
            generatedImageUrl=look.generated_image_url,
            visibility=look.visibility,
            sharedWith=[
                SharedUserInfo(
                    id=str(user.id),
                    email=user.email,
                    name=user.name
                )
                for user in look.shared_with
            ],
            products=[
                {
                    "id": str(p.id),
                    "sku": p.sku,
                    "name": p.name,
                    "designer": p.designer,
                    "price": p.price,
                    "productUrl": p.product_url,
                    "thumbnailUrl": p.thumbnail_url,
                    "createdAt": p.created_at.isoformat()
                }
                for p in look.products
            ],
            createdAt=look.created_at.isoformat(),
            updatedAt=look.updated_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update look: {str(e)}"
        )


@router.patch("/{look_id}/visibility/", response_model=LookResponse)
@router.patch("/{look_id}/visibility", response_model=LookResponse)
async def update_look_visibility(
    look_id: str,
    visibility_update: LookVisibilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a look's visibility settings.
    
    - Users can only update visibility of their own looks
    - Admins can update visibility of any look
    
    Visibility options:
    - private: Only visible to creator
    - shared: Visible to specific users (provide sharedWithUserIds)
    - public: Visible to everyone
    """
    # Find the look
    look = db.query(DBLook).filter(DBLook.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and look.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this look"
        )
    
    try:
        # Update visibility
        look.visibility = visibility_update.visibility.value
        
        # Clear existing shares
        look.shared_with.clear()
        
        # Add new shares if visibility is SHARED
        if visibility_update.visibility.value == "shared" and visibility_update.shared_with_user_ids:
            from app.models.user import User as DBUser
            for user_id in visibility_update.shared_with_user_ids:
                user = db.query(DBUser).filter(DBUser.id == user_id).first()
                if user:
                    look.shared_with.append(user)
                else:
                    print(f"⚠️  User {user_id} not found, skipping...")
            print(f"🔗 Updated sharing: Look now shared with {len(look.shared_with)} users")
        
        db.commit()
        db.refresh(look)
        
        from app.schemas.look import SharedUserInfo
        return LookResponse(
            id=str(look.id),
            title=look.title,
            notes=look.notes,
            generatedImageUrl=look.generated_image_url,
            visibility=look.visibility,
            sharedWith=[
                SharedUserInfo(
                    id=str(user.id),
                    email=user.email,
                    name=user.name
                )
                for user in look.shared_with
            ],
            products=[
                {
                    "id": str(p.id),
                    "sku": p.sku,
                    "name": p.name,
                    "designer": p.designer,
                    "price": p.price,
                    "productUrl": p.product_url,
                    "thumbnailUrl": p.thumbnail_url,
                    "createdAt": p.created_at.isoformat()
                }
                for p in look.products
            ],
            createdAt=look.created_at.isoformat(),
            updatedAt=look.updated_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update look visibility: {str(e)}"
        )


@router.delete("/{look_id}/", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/{look_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_look(
    look_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a look by its ID.
    
    - Users can only delete their own looks
    - Admins can delete any look
    
    This will also:
    - Delete all associated products (cascade)
    - Remove the generated image from storage
    - Remove all product thumbnails from storage
    """
    # The GUID type will handle UUID format conversion automatically
    look = db.query(DBLook).options(joinedload(DBLook.products)).filter(DBLook.id == look_id).first()
    if not look:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Look not found"
        )
    
    # Check ownership (unless admin)
    if current_user.role != UserRole.ADMIN and look.user_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this look"
        )
    
    try:
        # Delete generated image from storage
        storage_service.delete_file(look.generated_image_url)
        
        # Delete product thumbnails from storage
        for product in look.products:
            storage_service.delete_file(product.thumbnail_url)
        
        # Delete from database (products will cascade delete)
        db.delete(look)
        db.commit()
        
        print(f"✅ Deleted look {look_id} by user {current_user.email}")
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete look: {str(e)}"
        )
