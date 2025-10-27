"""
Database configuration
Supports both SQLite (development) and PostgreSQL (production)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, use SQLite for development
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./ai_studio.db"
    print("⚠️  Using SQLite for development")
else:
    print(f"✅ Using PostgreSQL: {DATABASE_URL[:30]}...")

# Create engine based on database type
if DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres"):
    # PostgreSQL configuration
    # Note: Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Max connections beyond pool_size
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False  # Set to True for SQL query logging
    )
else:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Database dependency for FastAPI
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this on startup
    """
    from app.models import (
        user, access_request, user_settings, 
        default_settings_model, model, look, product, subscription
    )
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")
