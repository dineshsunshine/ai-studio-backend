"""
SQLAlchemy model for Links (collections of looks shared with clients)
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Table, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


# Junction table for many-to-many relationship between links and looks
link_looks = Table(
    'link_looks',
    Base.metadata,
    Column('link_id', String(36), ForeignKey('links.id', ondelete='CASCADE'), primary_key=True),
    Column('look_id', String(36), ForeignKey('looks.id', ondelete='CASCADE'), primary_key=True),
    Column('position', Integer, nullable=False, default=0)  # For ordering looks within a link
)


class Link(Base):
    """Model for shareable link containing a collection of looks"""
    __tablename__ = "links"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Link information
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # Unique alphanumeric identifier for sharing (e.g., "AB12CD34")
    link_id = Column(String(16), unique=True, nullable=False, index=True)
    
    # Cover image for the shared link (masthead/hero image)
    cover_image_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    looks = relationship("Look", secondary=link_looks, back_populates="links", lazy="selectin")
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<Link(id={self.id}, link_id={self.link_id}, title={self.title})>"

