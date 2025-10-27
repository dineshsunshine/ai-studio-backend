"""
Subscription and Token Management Models
"""
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class SubscriptionTier(str, Enum):
    """Subscription tier enum"""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    PRO_PLUS = "pro_plus"
    ULTIMATE = "ultimate"


# Token limits per tier per month
TIER_TOKEN_LIMITS = {
    SubscriptionTier.FREE: 100,
    SubscriptionTier.BASIC: 300,
    SubscriptionTier.PRO: 1000,
    SubscriptionTier.PRO_PLUS: 3000,
    SubscriptionTier.ULTIMATE: -1  # -1 means unlimited
}


class UserSubscription(Base):
    """
    User subscription information
    Tracks current tier, tokens, and usage
    """
    __tablename__ = "user_subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Subscription details
    tier = Column(String, nullable=False, default=SubscriptionTier.FREE.value)
    
    # Token management
    total_tokens = Column(Integer, nullable=False, default=100)  # Total tokens allocated this period
    available_tokens = Column(Integer, nullable=False, default=100)  # Remaining tokens
    consumed_tokens = Column(Integer, nullable=False, default=0)  # Tokens used this period
    
    # Lifetime stats
    lifetime_consumed = Column(Integer, nullable=False, default=0)  # All-time consumption
    
    # Billing period (for monthly reset)
    period_start = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    def is_unlimited(self) -> bool:
        """Check if user has unlimited tokens"""
        return self.tier == SubscriptionTier.ULTIMATE.value
    
    def has_tokens(self, required: int = 1) -> bool:
        """Check if user has enough tokens"""
        if self.is_unlimited():
            return True
        return self.available_tokens >= required
    
    def consume_tokens(self, amount: int) -> bool:
        """
        Consume tokens if available
        Returns True if successful, False if insufficient tokens
        """
        if self.is_unlimited():
            self.consumed_tokens += amount
            self.lifetime_consumed += amount
            return True
        
        if self.available_tokens >= amount:
            self.available_tokens -= amount
            self.consumed_tokens += amount
            self.lifetime_consumed += amount
            return True
        
        return False


class TokenTransaction(Base):
    """
    Token transaction history for auditing
    Tracks every token consumption and top-up
    """
    __tablename__ = "token_transactions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Transaction details
    type = Column(String, nullable=False)  # 'consumption', 'topup', 'reset', 'tier_change'
    amount = Column(Integer, nullable=False)  # Positive for topup, negative for consumption
    
    # Context
    description = Column(Text, nullable=True)  # What the tokens were used for
    extra_data = Column(Text, nullable=True)  # Additional JSON data (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Before/after balance
    balance_before = Column(Integer, nullable=False)
    balance_after = Column(Integer, nullable=False)
    
    # Admin action
    admin_id = Column(String, ForeignKey("users.id"), nullable=True)  # If admin performed this action
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

