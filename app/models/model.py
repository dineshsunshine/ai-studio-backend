"""
Model database model for fashion models management
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid


class Model(Base):
    """
    Model represents a fashion model with an image.
    Models can be uploaded or AI-generated.
    Each model belongs to a user.
    """
    __tablename__ = "models"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, index=True)
    image_url = Column(String(512), nullable=False)
    prompt_details = Column(Text, nullable=True)  # Only for AI-generated models
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # Owner of the model
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Model(id={self.id}, name={self.name}, user_id={self.user_id})>"

