"""
Admin Subscription and Token Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.auth import require_admin
from app.models.user import User
from app.models.subscription import UserSubscription, TokenTransaction, SubscriptionTier, TIER_TOKEN_LIMITS
from app.schemas.subscription import (
    AdminUpdateSubscriptionRequest,
    AdminTopupTokensRequest,
    SubscriptionInfoResponse,
    AdminSubscriptionManagementResponse,
    TokenTransactionResponse
)
import uuid
from datetime import datetime, timedelta


router = APIRouter()


@router.get("/users/{user_id}/subscription", response_model=AdminSubscriptionManagementResponse)
async def get_user_subscription(
    user_id: str,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a user's subscription information (admin only).
    
    Returns complete subscription details including tokens and history.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no subscription"
        )
    
    # Get last transaction
    last_txn = db.query(TokenTransaction).filter(
        TokenTransaction.user_id == user_id
    ).order_by(desc(TokenTransaction.created_at)).first()
    
    last_transaction = None
    if last_txn:
        admin_email = None
        if last_txn.admin_id:
            admin = db.query(User).filter(User.id == last_txn.admin_id).first()
            admin_email = admin.email if admin else None
        
        last_transaction = TokenTransactionResponse(
            id=last_txn.id,
            type=last_txn.type,
            amount=last_txn.amount,
            description=last_txn.description,
            balanceBefore=last_txn.balance_before,
            balanceAfter=last_txn.balance_after,
            createdAt=last_txn.created_at.isoformat(),
            adminEmail=admin_email
        )
    
    return AdminSubscriptionManagementResponse(
        userId=str(user.id),
        userEmail=user.email,
        tier=subscription.tier,
        totalTokens=subscription.total_tokens,
        availableTokens=subscription.available_tokens,
        consumedTokens=subscription.consumed_tokens,
        lifetimeConsumed=subscription.lifetime_consumed,
        isUnlimited=subscription.is_unlimited(),
        periodStart=subscription.period_start.isoformat(),
        periodEnd=subscription.period_end.isoformat(),
        lastTransaction=last_transaction
    )


@router.put("/users/{user_id}/subscription/tier")
async def update_user_subscription_tier(
    user_id: str,
    request: AdminUpdateSubscriptionRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a user's subscription tier (admin only).
    
    This will:
    1. Change the user's tier
    2. Update token allocation based on new tier
    3. Reset billing period
    4. Create transaction record
    """
    # Validate tier
    try:
        new_tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {request.tier}. Must be one of: free, basic, pro, pro_plus, ultimate"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get or create subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        # Create new subscription
        period_start = datetime.utcnow()
        period_end = period_start + timedelta(days=30)
        
        subscription = UserSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tier=new_tier.value,
            total_tokens=TIER_TOKEN_LIMITS[new_tier],
            available_tokens=TIER_TOKEN_LIMITS[new_tier],
            consumed_tokens=0,
            lifetime_consumed=0,
            period_start=period_start,
            period_end=period_end
        )
        db.add(subscription)
    else:
        # Update existing subscription
        old_tier = subscription.tier
        balance_before = subscription.available_tokens
        
        # Update tier and tokens
        subscription.tier = new_tier.value
        new_token_limit = TIER_TOKEN_LIMITS[new_tier]
        subscription.total_tokens = new_token_limit if new_token_limit != -1 else subscription.total_tokens
        subscription.available_tokens = new_token_limit if new_token_limit != -1 else subscription.available_tokens
        subscription.consumed_tokens = 0
        
        # Reset billing period
        subscription.period_start = datetime.utcnow()
        subscription.period_end = subscription.period_start + timedelta(days=30)
        
        # Create transaction record
        transaction = TokenTransaction(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type="tier_change",
            amount=subscription.available_tokens - balance_before if new_token_limit != -1 else 0,
            description=f"Tier changed from {old_tier} to {new_tier.value}",
            balance_before=balance_before,
            balance_after=subscription.available_tokens,
            admin_id=str(current_admin.id)
        )
        db.add(transaction)
    
    db.commit()
    db.refresh(subscription)
    
    return {
        "status": "success",
        "message": f"User tier updated to {new_tier.value}",
        "subscription": {
            "tier": subscription.tier,
            "totalTokens": subscription.total_tokens,
            "availableTokens": subscription.available_tokens,
            "isUnlimited": subscription.is_unlimited()
        }
    }


@router.post("/users/{user_id}/subscription/topup")
async def topup_user_tokens(
    user_id: str,
    request: AdminTopupTokensRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Adjust a user's tokens (admin only).
    
    - Positive amount: Adds tokens (top-up)
    - Negative amount: Deducts tokens (penalty/adjustment)
    
    The adjustment is applied to both available and total tokens.
    For deductions, available tokens cannot go below 0.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no subscription"
        )
    
    # Don't allow adjustment for unlimited tier
    if subscription.is_unlimited():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot adjust tokens for unlimited tier"
        )
    
    # Record balance before
    balance_before = subscription.available_tokens
    
    # Check if deduction would result in negative balance
    if request.amount < 0:
        new_available = subscription.available_tokens + request.amount
        if new_available < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deduct {abs(request.amount)} tokens. User only has {subscription.available_tokens} available tokens."
            )
    
    # Apply adjustment
    subscription.available_tokens += request.amount
    subscription.total_tokens += request.amount
    
    # Determine transaction type and description
    is_topup = request.amount > 0
    transaction_type = "topup" if is_topup else "admin_deduction"
    
    if request.description:
        description = request.description
    else:
        if is_topup:
            description = f"Admin top-up of {request.amount} tokens"
        else:
            description = f"Admin deduction of {abs(request.amount)} tokens"
    
    # Create transaction record
    transaction = TokenTransaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type=transaction_type,
        amount=request.amount,
        description=description,
        balance_before=balance_before,
        balance_after=subscription.available_tokens,
        admin_id=str(current_admin.id)
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(subscription)
    
    action = "Added" if is_topup else "Deducted"
    return {
        "status": "success",
        "message": f"{action} {abs(request.amount)} tokens {'to' if is_topup else 'from'} user's account",
        "subscription": {
            "availableTokens": subscription.available_tokens,
            "totalTokens": subscription.total_tokens
        }
    }


@router.post("/users/{user_id}/subscription/reset-period")
async def reset_user_billing_period(
    user_id: str,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reset a user's billing period (admin only).
    
    This will:
    1. Reset consumed tokens to 0
    2. Restore available tokens to tier limit
    3. Set new billing period (30 days from now)
    4. Create transaction record
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get subscription
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no subscription"
        )
    
    # Record old values
    balance_before = subscription.available_tokens
    
    # Reset period
    tier = SubscriptionTier(subscription.tier)
    token_limit = TIER_TOKEN_LIMITS[tier]
    
    subscription.period_start = datetime.utcnow()
    subscription.period_end = subscription.period_start + timedelta(days=30)
    subscription.consumed_tokens = 0
    
    if token_limit != -1:  # Not unlimited
        subscription.total_tokens = token_limit
        subscription.available_tokens = token_limit
    
    # Create transaction record
    transaction = TokenTransaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type="reset",
        amount=subscription.available_tokens - balance_before if token_limit != -1 else 0,
        description="Billing period reset by admin",
        balance_before=balance_before,
        balance_after=subscription.available_tokens,
        admin_id=str(current_admin.id)
    )
    db.add(transaction)
    
    db.commit()
    db.refresh(subscription)
    
    return {
        "status": "success",
        "message": "Billing period reset successfully",
        "subscription": {
            "periodStart": subscription.period_start.isoformat(),
            "periodEnd": subscription.period_end.isoformat(),
            "availableTokens": subscription.available_tokens,
            "consumedTokens": subscription.consumed_tokens
        }
    }

