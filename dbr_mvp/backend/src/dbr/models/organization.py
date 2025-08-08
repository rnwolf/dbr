# src/dbr/models/organization.py
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum


class OrganizationStatus(enum.Enum):
    """Organization status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Organization(BaseModel):
    """Organization model representing a tenant in the multi-tenant system"""
    __tablename__ = "organizations"
    
    # Basic organization information
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(Enum(OrganizationStatus), nullable=False, default=OrganizationStatus.ACTIVE)
    
    # Contact information
    contact_email = Column(String(255), nullable=False)
    country = Column(String(2), nullable=False)  # ISO country code
    
    # Subscription information
    subscription_level = Column(String(50), nullable=False, default="basic")
    
    # Default board reference (will be added later when we create BoardConfig)
    default_board_id = Column(String(36), nullable=True)
    
    # Relationships
    work_items = relationship("WorkItem", back_populates="organization")
    collections = relationship("Collection", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}', status='{self.status.value}')>"