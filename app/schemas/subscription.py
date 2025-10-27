"""
Subscription and Token Management Schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class SubscriptionInfoResponse(BaseModel):
    """User's subscription information"""
    tier: str
    totalTokens: int
    availableTokens: int
    consumedTokens: int
    lifetimeConsumed: int
    isUnlimited: bool
    periodStart: str
    periodEnd: str


class ConsumeTokensRequest(BaseModel):
    """Request to consume tokens"""
    operation: str = Field(..., description="Operation name (e.g., 'text_to_image', 'multi_modal')")
    description: Optional[str] = Field(None, description="Additional context about the operation")


class ConsumeTokensResponse(BaseModel):
    """Response after consuming tokens"""
    success: bool
    cost: int
    availableTokens: int
    consumedTokens: int
    message: str


class OperationCostsResponse(BaseModel):
    """Response with all operation costs"""
    costs: dict = Field(..., description="Dictionary of operation names to token costs")


class AdminUpdateSubscriptionRequest(BaseModel):
    """Admin request to update user's subscription"""
    tier: str = Field(..., description="Subscription tier: free, basic, pro, pro_plus, ultimate")


class AdminTopupTokensRequest(BaseModel):
    """Admin request to adjust user's tokens (top-up or deduct)"""
    amount: int = Field(..., description="Number of tokens to add (positive) or deduct (negative). Cannot be zero.")
    description: Optional[str] = Field(None, description="Reason for adjustment")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v


class TokenTransactionResponse(BaseModel):
    """Token transaction record"""
    id: str
    type: str
    amount: int
    description: Optional[str]
    balanceBefore: int
    balanceAfter: int
    createdAt: str
    adminEmail: Optional[str]


class TokenHistoryResponse(BaseModel):
    """List of token transactions"""
    transactions: List[TokenTransactionResponse]
    total: int


class SubscriptionTierInfo(BaseModel):
    """Information about a subscription tier"""
    tier: str
    name: str
    tokensPerMonth: int
    isUnlimited: bool


class SubscriptionTiersResponse(BaseModel):
    """List of all available subscription tiers"""
    tiers: List[SubscriptionTierInfo]


class AdminSubscriptionManagementResponse(BaseModel):
    """Admin view of user subscription with management options"""
    userId: str
    userEmail: str
    tier: str
    totalTokens: int
    availableTokens: int
    consumedTokens: int
    lifetimeConsumed: int
    isUnlimited: bool
    periodStart: str
    periodEnd: str
    lastTransaction: Optional[TokenTransactionResponse]

