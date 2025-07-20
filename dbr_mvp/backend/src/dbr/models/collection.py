# src/dbr/models/collection.py
from sqlalchemy import Column, String, Enum, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum


class CollectionType(enum.Enum):
    """Collection type enumeration"""
    PROJECT = "Project"
    MOVE = "MOVE"
    EPIC = "Epic"
    RELEASE = "Release"


class CollectionStatus(enum.Enum):
    """Collection status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"


class Collection(BaseModel):
    """Collection model - container for related work items (Project/MOVE)"""
    __tablename__ = "collections"
    
    # Basic collection information
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    type = Column(Enum(CollectionType), nullable=False, default=CollectionType.PROJECT)
    status = Column(Enum(CollectionStatus), nullable=False, default=CollectionStatus.PLANNING)
    
    # Ownership and dates
    owner_user_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    target_completion_date = Column(DateTime, nullable=True)
    target_completion_date_timezone = Column(String(50), nullable=True, default="UTC")
    
    # Financial information
    estimated_sales_price = Column(Float, nullable=True, default=0.0)
    estimated_variable_cost = Column(Float, nullable=True, default=0.0)
    
    # External reference
    url = Column(String(500), nullable=True)
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="collections")
    # owner = relationship("User", back_populates="owned_collections")
    # work_items = relationship("WorkItem", back_populates="collection")
    
    def calculate_throughput(self) -> float:
        """Calculate collection throughput (sales_price - variable_cost)"""
        sales_price = self.estimated_sales_price or 0.0
        variable_cost = self.estimated_variable_cost or 0.0
        return sales_price - variable_cost
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', type='{self.type.value}', status='{self.status.value}')>"