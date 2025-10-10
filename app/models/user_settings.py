"""
User Settings Model
Stores user-specific application settings as JSON
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserSettings(Base):
    """
    User Settings Model
    Each user has one settings record containing their customized app configuration
    """
    __tablename__ = "user_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Theme setting: 'light' or 'dark'
    theme = Column(String(10), nullable=False, default='light')
    
    # Flexible JSON field to store tool settings
    # Structure: { lookCreator: {...}, copywriter: {...}, finishingStudio: {...}, modelManager: {...} }
    tool_settings = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings(user_id='{self.user_id}')>"

