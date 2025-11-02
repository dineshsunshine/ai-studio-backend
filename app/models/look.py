import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base


# Custom UUID type for SQLite compatibility (copied from model.py)
class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR(32)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value)).replace('-', '')  # Remove dashes for SQLite
            return str(value).replace('-', '')

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value


class LookVisibility(str, Enum):
    """Visibility options for looks"""
    PRIVATE = "private"      # Only visible to creator
    SHARED = "shared"        # Visible to specific users
    PUBLIC = "public"        # Visible to everyone


# Junction table for look sharing (many-to-many: Look <-> User)
look_shares = Table(
    'look_shares',
    Base.metadata,
    Column('look_id', String(36), ForeignKey('looks.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('shared_at', DateTime, default=datetime.utcnow)
)


class Look(Base):
    """
    Look represents a fashion look with products.
    Each look belongs to a user.
    Can be private, shared with specific users, or public.
    """
    __tablename__ = "looks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    generated_image_url = Column(String, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)  # Owner of the look
    visibility = Column(String(20), nullable=False, default=LookVisibility.PRIVATE.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="look", cascade="all, delete-orphan")
    links = relationship("Link", secondary="link_looks", back_populates="looks")
    shared_with = relationship("User", secondary=look_shares, backref="shared_looks")
    videos = relationship("VideoJob", secondary="look_videos", backref="looks")

    def __repr__(self):
        return f"<Look(id='{self.id}', title='{self.title}', user_id='{self.user_id}', visibility='{self.visibility}')>"


# Junction table for look-video relationships (many-to-many: Look <-> VideoJob)
look_videos = Table(
    'look_videos',
    Base.metadata,
    Column('look_id', String(36), ForeignKey('looks.id', ondelete='CASCADE'), primary_key=True),
    Column('video_job_id', String(36), ForeignKey('video_jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('is_default', Boolean, default=False, nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)
