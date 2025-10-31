"""
User Subscription and Token Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.token_costs import get_operation_cost, get_all_costs, is_valid_operation
from app.models.user import User
from app.models.subscription import UserSubscription, TokenTransaction, SubscriptionTier, TIER_TOKEN_LIMITS
from app.schemas.subscription import (
    SubscriptionInfoResponse,
    ConsumeTokensRequest,
    ConsumeTokensResponse,
    TokenHistoryResponse,
    TokenTransactionResponse,
    SubscriptionTiersResponse,
    SubscriptionTierInfo,
    OperationCostsResponse
)
import uuid
from datetime import datetime, timedelta


router = APIRouter()


def get_or_create_subscription(user_id: str, db: Session) -> UserSubscription:
    """
    Get user subscription, creating with FREE tier if not exists
    """
    subscription = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
    
    if not subscription:
        # Create new subscription with FREE tier
        period_start = datetime.utcnow()
        period_end = period_start + timedelta(days=30)
        
        subscription = UserSubscription(
            id=str(uuid.uuid4()),
            user_id=user_id,
            tier=SubscriptionTier.FREE.value,
            total_tokens=TIER_TOKEN_LIMITS[SubscriptionTier.FREE],
            available_tokens=TIER_TOKEN_LIMITS[SubscriptionTier.FREE],
            consumed_tokens=0,
            lifetime_consumed=0,
            period_start=period_start,
            period_end=period_end
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription


@router.get("/info", response_model=SubscriptionInfoResponse)
async def get_subscription_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription information.
    
    Returns tier, tokens (total, available, consumed), and billing period.
    """
    subscription = get_or_create_subscription(str(current_user.id), db)
    
    return SubscriptionInfoResponse(
        tier=subscription.tier,
        totalTokens=subscription.total_tokens,
        availableTokens=subscription.available_tokens,
        consumedTokens=subscription.consumed_tokens,
        lifetimeConsumed=subscription.lifetime_consumed,
        isUnlimited=subscription.is_unlimited(),
        periodStart=subscription.period_start.isoformat(),
        periodEnd=subscription.period_end.isoformat()
    )


def consume_tokens_internal(user_id: str, operation: str, description: str, db: Session) -> dict:
    """
    Internal function to consume tokens without HTTP overhead.
    Used by other endpoints (e.g., video generation) to consume tokens programmatically.
    
    Returns:
        dict with keys: success, cost, availableTokens, consumedTokens, message
    """
    # Validate operation
    if not is_valid_operation(operation):
        raise ValueError(f"Invalid operation: {operation}")
    
    # Get operation cost
    cost = get_operation_cost(operation)
    
    subscription = get_or_create_subscription(user_id, db)
    
    # Check if user has enough tokens
    if not subscription.has_tokens(cost):
        return {
            "success": False,
            "cost": cost,
            "availableTokens": subscription.available_tokens,
            "consumedTokens": subscription.consumed_tokens,
            "message": f"Insufficient tokens. Operation '{operation}' costs {cost} tokens but you have {subscription.available_tokens}."
        }
    
    # Record balance before
    balance_before = subscription.available_tokens
    
    # Consume tokens
    subscription.consume_tokens(cost)
    
    # Create transaction record
    transaction = TokenTransaction(
        id=str(uuid.uuid4()),
        user_id=user_id,
        type="consumption",
        amount=-cost,
        description=description,
        balance_before=balance_before if not subscription.is_unlimited() else -1,
        balance_after=subscription.available_tokens if not subscription.is_unlimited() else -1,
        admin_id=None
    )
    db.add(transaction)
    db.commit()
    
    return {
        "success": True,
        "cost": cost,
        "availableTokens": subscription.available_tokens,
        "consumedTokens": subscription.consumed_tokens,
        "message": f"Successfully consumed {cost} tokens for '{operation}' operation."
    }


@router.post("/consume", response_model=ConsumeTokensResponse)
async def consume_tokens(
    request: ConsumeTokensRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Consume tokens for the current user based on operation type.
    
    Frontend should call this endpoint BEFORE performing an AI operation.
    The backend determines the token cost based on the operation type.
    
    Request body:
    - operation: Operation name (e.g., 'text_to_image', 'multi_modal')
    - description: Optional context about the operation
    
    Returns:
    - success: True if tokens were consumed, False if insufficient
    - cost: Number of tokens this operation costs
    - availableTokens: Remaining token balance
    - consumedTokens: Total consumed this period
    - message: Status message
    
    Example:
    ```
    POST /api/v1/subscription/consume
    {
        "operation": "text_to_image",
        "description": "Generated model: Fashion Model A"
    }
    ```
    """
    # Validate operation
    if not is_valid_operation(request.operation):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {request.operation}. Valid operations: {list(get_all_costs().keys())}"
        )
    
    # Get operation cost
    try:
        cost = get_operation_cost(request.operation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    subscription = get_or_create_subscription(str(current_user.id), db)
    
    # Check if user has enough tokens
    if not subscription.has_tokens(cost):
        return ConsumeTokensResponse(
            success=False,
            cost=cost,
            availableTokens=subscription.available_tokens,
            consumedTokens=subscription.consumed_tokens,
            message=f"Insufficient tokens. Operation '{request.operation}' costs {cost} tokens but you have {subscription.available_tokens}."
        )
    
    # Record balance before
    balance_before = subscription.available_tokens
    
    # Consume tokens
    subscription.consume_tokens(cost)
    
    # Create transaction record
    description = request.description or f"{request.operation} operation"
    transaction = TokenTransaction(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        type="consumption",
        amount=-cost,  # Negative for consumption
        description=description,
        balance_before=balance_before if not subscription.is_unlimited() else -1,
        balance_after=subscription.available_tokens if not subscription.is_unlimited() else -1,
        admin_id=None
    )
    db.add(transaction)
    db.commit()
    db.refresh(subscription)
    
    return ConsumeTokensResponse(
        success=True,
        cost=cost,
        availableTokens=subscription.available_tokens,
        consumedTokens=subscription.consumed_tokens,
        message=f"Successfully consumed {cost} tokens for '{request.operation}' operation."
    )


@router.get("/history", response_model=TokenHistoryResponse)
async def get_token_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's token transaction history.
    
    Shows all token consumptions, top-ups, and tier changes.
    """
    # Get total count
    total = db.query(TokenTransaction).filter(
        TokenTransaction.user_id == str(current_user.id)
    ).count()
    
    # Get transactions
    transactions = db.query(TokenTransaction).filter(
        TokenTransaction.user_id == str(current_user.id)
    ).order_by(desc(TokenTransaction.created_at)).offset(skip).limit(limit).all()
    
    # Get admin emails for admin actions
    transaction_responses = []
    for txn in transactions:
        admin_email = None
        if txn.admin_id:
            admin = db.query(User).filter(User.id == txn.admin_id).first()
            admin_email = admin.email if admin else None
        
        transaction_responses.append(TokenTransactionResponse(
            id=txn.id,
            type=txn.type,
            amount=txn.amount,
            description=txn.description,
            balanceBefore=txn.balance_before,
            balanceAfter=txn.balance_after,
            createdAt=txn.created_at.isoformat(),
            adminEmail=admin_email
        ))
    
    return TokenHistoryResponse(
        transactions=transaction_responses,
        total=total
    )


@router.get("/tiers", response_model=SubscriptionTiersResponse)
async def get_subscription_tiers():
    """
    Get information about all available subscription tiers.
    
    Returns tier names, token limits, and pricing information.
    """
    tier_names = {
        SubscriptionTier.FREE: "Free",
        SubscriptionTier.BASIC: "Basic",
        SubscriptionTier.PRO: "Pro",
        SubscriptionTier.PRO_PLUS: "Pro+",
        SubscriptionTier.ULTIMATE: "Ultimate"
    }
    
    tiers = []
    for tier in SubscriptionTier:
        token_limit = TIER_TOKEN_LIMITS[tier]
        tiers.append(SubscriptionTierInfo(
            tier=tier.value,
            name=tier_names[tier],
            tokensPerMonth=token_limit if token_limit != -1 else 0,
            isUnlimited=token_limit == -1
        ))
    
    return SubscriptionTiersResponse(tiers=tiers)


@router.get("/costs", response_model=OperationCostsResponse)
async def get_operation_costs():
    """
    Get token costs for all AI operations.
    
    Returns a dictionary of operation names to their token costs.
    Frontend can use this to display costs to users before they perform operations.
    
    Example response:
    ```json
    {
        "costs": {
            "text_to_image": 10,
            "multi_modal": 20,
            "multi_modal_light": 8,
            "image_to_text": 5,
            "text_to_text": 3
        }
    }
    ```
    
    No authentication required - costs are public information.
    """
    return OperationCostsResponse(costs=get_all_costs())

