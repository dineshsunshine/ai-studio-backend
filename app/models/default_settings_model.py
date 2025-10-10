"""
Default Settings Model
Stores admin-configurable default settings for new users
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from app.core.database import Base


class DefaultSettingsModel(Base):
    """
    Admin-configurable default settings
    Only one record should exist (singleton pattern)
    """
    __tablename__ = "default_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Default theme
    default_theme = Column(String(10), nullable=False, default='light')
    
    # Default tool settings as JSON
    default_tool_settings = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    updated_by = Column(String(36), nullable=True)  # admin user ID who last updated
    
    def __repr__(self):
        return f"<DefaultSettings(theme='{self.default_theme}', updated={self.updated_at})>"

