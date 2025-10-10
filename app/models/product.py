import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.database import Base


# Custom UUID type for SQLite compatibility
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


class Product(Base):
    __tablename__ = "products"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    look_id = Column(GUID(), ForeignKey("looks.id", ondelete="CASCADE"), nullable=False)
    
    sku = Column(String, nullable=True)
    name = Column(String, nullable=False)
    designer = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    product_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to look
    look = relationship("Look", back_populates="products")

    def __repr__(self):
        return f"<Product(id='{self.id}', name='{self.name}', look_id='{self.look_id}')>"

