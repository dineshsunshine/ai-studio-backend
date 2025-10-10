"""
Authentication endpoints for Google OAuth and user management
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import (
    verify_google_token,
    create_token_for_user,
    get_current_user,
    get_current_active_user
)
from app.models.user import User, UserRole, UserStatus
from app.models.access_request import AccessRequest, RequestStatus
from app.schemas.auth import (
    GoogleAuthRequest,
    AuthResponse,
    TokenData,
    UserResponse,
    AccessRequestCreate,
    AccessRequestResponse
)


router = APIRouter()


# ==================== Google OAuth Login/Register ====================

@router.post("/google/", response_model=AuthResponse)
@router.post("/google", response_model=AuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth ID token.
    
    Flow:
    1. Verify Google ID token
    2. Check if user exists:
       - If user exists and is active → return JWT token (login)
       - If user exists and is pending → return pending status
       - If user exists and is rejected → return rejected status
       - If user doesn't exist → create access request
    
    Returns:
        AuthResponse with status and appropriate data
    """
    # Verify Google token
    google_user_info = verify_google_token(request.google_id_token)
    if not google_user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token"
        )
    
    email = google_user_info["email"]
    google_id = google_user_info["google_id"]
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        # User exists - check status
        if existing_user.status == UserStatus.ACTIVE:
            # Update user info from Google (profile picture, name, google_id)
            existing_user.google_id = google_id
            existing_user.full_name = google_user_info.get("full_name") or existing_user.full_name
            existing_user.profile_picture = google_user_info.get("profile_picture")
            existing_user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(existing_user)
            
            # Generate JWT token
            token_info = create_token_for_user(existing_user)
            
            user_response = UserResponse(
                id=str(existing_user.id),
                email=existing_user.email,
                fullName=existing_user.full_name,
                profilePicture=existing_user.profile_picture,
                role=existing_user.role.value,
                status=existing_user.status.value,
                createdAt=existing_user.created_at.isoformat(),
                lastLogin=existing_user.last_login.isoformat() if existing_user.last_login else None
            )
            
            return AuthResponse(
                status="success",
                message="Login successful",
                data=TokenData(
                    user=user_response,
                    accessToken=token_info["access_token"],
                    tokenType=token_info["token_type"],
                    expiresIn=token_info["expires_in"]
                )
            )
        
        elif existing_user.status == UserStatus.PENDING:
            # User is pending approval
            # Check if there's an access request
            access_request = db.query(AccessRequest).filter(
                AccessRequest.email == email,
                AccessRequest.status == RequestStatus.PENDING
            ).first()
            
            return AuthResponse(
                status="pending",
                message="Your access request is pending approval",
                data={
                    "requestId": str(access_request.id) if access_request else None,
                    "requestedAt": access_request.requested_at.isoformat() if access_request else None
                }
            )
        
        elif existing_user.status == UserStatus.SUSPENDED:
            # User is suspended
            return AuthResponse(
                status="suspended",
                message="Your account has been suspended. Please contact support.",
                data=None
            )
    
    # User doesn't exist - check if there's already an access request
    existing_request = db.query(AccessRequest).filter(
        AccessRequest.email == email
    ).order_by(AccessRequest.requested_at.desc()).first()
    
    if existing_request:
        if existing_request.status == RequestStatus.PENDING:
            return AuthResponse(
                status="pending",
                message="Your access request is pending approval",
                data={
                    "requestId": str(existing_request.id),
                    "requestedAt": existing_request.requested_at.isoformat()
                }
            )
        elif existing_request.status == RequestStatus.REJECTED:
            return AuthResponse(
                status="rejected",
                message="Your access request was rejected",
                data={
                    "rejectedAt": existing_request.reviewed_at.isoformat() if existing_request.reviewed_at else None,
                    "rejectionReason": existing_request.rejection_reason
                }
            )
    
    # Create new access request
    new_request = AccessRequest(
        email=email,
        google_id=google_id,
        full_name=google_user_info.get("full_name"),
        profile_picture=google_user_info.get("profile_picture"),
        reason=None  # Can be added later via separate endpoint
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return AuthResponse(
        status="request_created",
        message="Access request submitted successfully. You will be notified once approved.",
        data={
            "requestId": str(new_request.id),
            "email": email,
            "requestedAt": new_request.requested_at.isoformat()
        }
    )


# ==================== Get Current User ====================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's information.
    
    Returns:
        Current user details
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        fullName=current_user.full_name,
        profilePicture=current_user.profile_picture,
        role=current_user.role.value,
        status=current_user.status.value,
        createdAt=current_user.created_at.isoformat(),
        lastLogin=current_user.last_login.isoformat() if current_user.last_login else None
    )


# ==================== Logout ====================

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (token invalidation would be handled client-side).
    
    Note: With JWT, logout is primarily client-side (delete token).
    For true server-side logout, implement a token blacklist.
    
    Returns:
        Success message
    """
    return {"message": "Logout successful"}


# ==================== Request Access (Alternative to OAuth) ====================

@router.post("/request-access", response_model=AccessRequestResponse)
async def request_access(
    request: AccessRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submit an access request manually (without Google OAuth).
    This is an alternative way to request access.
    
    Returns:
        Created access request
    """
    # Check if email already has a user
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Check if there's already a pending request
    existing_request = db.query(AccessRequest).filter(
        AccessRequest.email == request.email,
        AccessRequest.status == RequestStatus.PENDING
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Access request already exists for this email"
        )
    
    # Create new request
    new_request = AccessRequest(
        email=request.email,
        full_name=request.full_name,
        reason=request.reason
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return AccessRequestResponse(
        id=str(new_request.id),
        email=new_request.email,
        fullName=new_request.full_name,
        profilePicture=new_request.profile_picture,
        reason=new_request.reason,
        status=new_request.status.value,
        requestedAt=new_request.requested_at.isoformat(),
        reviewedAt=None,
        rejectionReason=None
    )


# ==================== Check Request Status ====================

@router.get("/request-status")
async def check_request_status(
    email: str = Query(..., description="Email to check request status for"),
    db: Session = Depends(get_db)
):
    """
    Check the status of an access request by email.
    
    Returns:
        Request status information
    """
    request = db.query(AccessRequest).filter(
        AccessRequest.email == email
    ).order_by(AccessRequest.requested_at.desc()).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No access request found for this email"
        )
    
    return {
        "status": request.status.value,
        "requestId": str(request.id),
        "requestedAt": request.requested_at.isoformat(),
        "reviewedAt": request.reviewed_at.isoformat() if request.reviewed_at else None,
        "message": _get_status_message(request.status)
    }


def _get_status_message(status: RequestStatus) -> str:
    """Helper to get user-friendly status message"""
    messages = {
        RequestStatus.PENDING: "Your request is under review",
        RequestStatus.APPROVED: "Your request has been approved. You can now login.",
        RequestStatus.REJECTED: "Your request was rejected"
    }
    return messages.get(status, "Unknown status")
