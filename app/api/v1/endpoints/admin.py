"""
Admin endpoints for managing access requests and users
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_admin
from app.core.default_settings import get_current_defaults
from app.models.user import User, UserRole, UserStatus
from app.models.access_request import AccessRequest, RequestStatus
from app.models.user_settings import UserSettings
from app.schemas.auth import (
    AccessRequestListResponse,
    AccessRequestResponse,
    AccessRequestApprove,
    AccessRequestReject,
    UserResponse,
    UserListResponse,
    UserUpdate
)


router = APIRouter()


# ==================== Access Request Management ====================

@router.get("/access-requests", response_model=AccessRequestListResponse)
async def list_access_requests(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all access requests (admin only).
    
    Query Parameters:
        - status: Filter by status (pending/approved/rejected)
        - skip: Number of records to skip
        - limit: Maximum records to return
    
    Returns:
        Paginated list of access requests
    """
    query = db.query(AccessRequest)
    
    # Filter by status if provided
    if status_filter:
        try:
            status_enum = RequestStatus(status_filter)
            query = query.filter(AccessRequest.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    requests = query.order_by(AccessRequest.requested_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response schema
    request_responses = [
        AccessRequestResponse(
            id=str(req.id),
            email=req.email,
            fullName=req.full_name,
            profilePicture=req.profile_picture,
            reason=req.reason,
            status=req.status.value,
            requestedAt=req.requested_at.isoformat(),
            reviewedAt=req.reviewed_at.isoformat() if req.reviewed_at else None,
            rejectionReason=req.rejection_reason
        )
        for req in requests
    ]
    
    return AccessRequestListResponse(
        requests=request_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/access-requests/{request_id}/approve", response_model=UserResponse)
async def approve_access_request(
    request_id: str,
    approve_data: AccessRequestApprove,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Approve an access request and create a user account (admin only).
    
    Path Parameters:
        - request_id: ID of the access request
    
    Body:
        - role: Role to assign (default: "user")
    
    Returns:
        Created user
    """
    # Get the access request
    access_request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )
    
    # Check if already processed
    if access_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access request already {access_request.status.value}"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == access_request.email).first()
    if existing_user:
        # Update existing user to active
        existing_user.status = UserStatus.ACTIVE
        existing_user.role = UserRole(approve_data.role) if approve_data.role else UserRole.USER
        new_user = existing_user
    else:
        # Create new user
        try:
            role_enum = UserRole(approve_data.role) if approve_data.role else UserRole.USER
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {approve_data.role}"
            )
        
        new_user = User(
            email=access_request.email,
            google_id=access_request.google_id,
            full_name=access_request.full_name,
            profile_picture=access_request.profile_picture,
            role=role_enum,
            status=UserStatus.ACTIVE
        )
        db.add(new_user)
        db.flush()  # Flush to get the generated ID
    
    # Update access request
    access_request.status = RequestStatus.APPROVED
    access_request.reviewed_at = datetime.utcnow()
    access_request.reviewed_by = str(current_admin.id)  # Convert to string for consistency
    
    # Create user settings with defaults if they don't exist
    user_id_str = str(new_user.id)
    existing_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id_str).first()
    if not existing_settings:
        # Get current admin-configurable defaults from database
        current_defaults = get_current_defaults(db)
        user_settings = UserSettings(
            user_id=user_id_str,
            theme=current_defaults["theme"],
            tool_settings=current_defaults["toolSettings"]
        )
        db.add(user_settings)
    
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        fullName=new_user.full_name,
        profilePicture=new_user.profile_picture,
        role=new_user.role.value,
        status=new_user.status.value,
        createdAt=new_user.created_at.isoformat(),
        lastLogin=new_user.last_login.isoformat() if new_user.last_login else None
    )


@router.post("/access-requests/{request_id}/reject")
async def reject_access_request(
    request_id: str,
    reject_data: AccessRequestReject,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reject an access request (admin only).
    
    Path Parameters:
        - request_id: ID of the access request
    
    Body:
        - reason: Optional rejection reason
    
    Returns:
        Success message
    """
    # Get the access request
    access_request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not access_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access request not found"
        )
    
    # Check if already processed
    if access_request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access request already {access_request.status.value}"
        )
    
    # Update access request
    access_request.status = RequestStatus.REJECTED
    access_request.reviewed_at = datetime.utcnow()
    access_request.reviewed_by = current_admin.id
    access_request.rejection_reason = reject_data.reason
    
    db.commit()
    
    return {
        "message": "Access request rejected successfully",
        "requestId": str(access_request.id)
    }


# ==================== User Management ====================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    role_filter: Optional[str] = Query(None, alias="role", description="Filter by role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin only).
    
    Query Parameters:
        - status: Filter by status (active/pending/suspended)
        - role: Filter by role (user/admin)
        - skip: Number of records to skip
        - limit: Maximum records to return
    
    Returns:
        Paginated list of users
    """
    query = db.query(User)
    
    # Filter by status if provided
    if status_filter:
        try:
            status_enum = UserStatus(status_filter)
            query = query.filter(User.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Filter by role if provided
    if role_filter:
        try:
            role_enum = UserRole(role_filter)
            query = query.filter(User.role == role_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {role_filter}"
            )
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert to response schema
    user_responses = [
        UserResponse(
            id=str(u.id),
            email=u.email,
            fullName=u.full_name,
            profilePicture=u.profile_picture,
            role=u.role.value,
            status=u.status.value,
            createdAt=u.created_at.isoformat(),
            lastLogin=u.last_login.isoformat() if u.last_login else None
        )
        for u in users
    ]
    
    return UserListResponse(
        users=user_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's role or status (admin only).
    
    Path Parameters:
        - user_id: ID of the user to update
    
    Body:
        - role: New role (optional)
        - status: New status (optional)
    
    Returns:
        Updated user
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from modifying themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot modify your own account"
        )
    
    # Update role if provided
    if user_update.role:
        try:
            user.role = UserRole(user_update.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role: {user_update.role}"
            )
    
    # Update status if provided
    if user_update.status:
        try:
            user.status = UserStatus(user_update.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {user_update.status}"
            )
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        fullName=user.full_name,
        profilePicture=user.profile_picture,
        role=user.role.value,
        status=user.status.value,
        createdAt=user.created_at.isoformat(),
        lastLogin=user.last_login.isoformat() if user.last_login else None
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (admin only).
    
    Path Parameters:
        - user_id: ID of the user to delete
    
    Returns:
        Success message
    """
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

