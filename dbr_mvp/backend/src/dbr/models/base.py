# src/dbr/models/base.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID

# Create the base class for all models (SQLAlchemy 2.0 style)
Base = declarative_base()


class BaseModel(Base):
    """Base model class with common fields for all entities"""
    __abstract__ = True
    
    # UUID primary key for all models
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Audit fields
    created_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"