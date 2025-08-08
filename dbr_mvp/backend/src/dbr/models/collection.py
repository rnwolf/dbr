# src/dbr/models/collection.py
from sqlalchemy import Column, String, Enum, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum


class CollectionStatus(enum.Enum):
    """Collection status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"


class Collection(BaseModel):
    """Collection model - container for related work items"""
    __tablename__ = "collections"
    
    # Basic collection information
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
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
    
    # Relationships
    organization = relationship("Organization", back_populates="collections")
    owner = relationship("User", back_populates="owned_collections")
    work_items = relationship("WorkItem", back_populates="collection")
    
    def calculate_throughput(self) -> float:
        """Calculate collection throughput (sales_price - variable_cost)"""
        sales_price = self.estimated_sales_price or 0.0
        variable_cost = self.estimated_variable_cost or 0.0
        return sales_price - variable_cost
    
    # Work item management methods
    def get_work_items(self, session):
        """Get all work items in this collection"""
        from dbr.models.work_item import WorkItem
        return session.query(WorkItem).filter_by(collection_id=self.id).all()
    
    def remove_work_item(self, session, work_item_id: str):
        """Remove a work item from this collection"""
        from dbr.models.work_item import WorkItem
        work_item = session.query(WorkItem).filter_by(id=work_item_id, collection_id=self.id).first()
        if work_item:
            work_item.collection_id = None
            session.commit()
            return True
        return False
    
    def add_work_item(self, session, work_item_id: str):
        """Add a work item to this collection"""
        from dbr.models.work_item import WorkItem
        work_item = session.query(WorkItem).filter_by(id=work_item_id).first()
        if work_item and work_item.organization_id == self.organization_id:
            work_item.collection_id = self.id
            session.commit()
            return True
        return False
    
    # Collection-level calculations
    def calculate_completion_percentage(self, session) -> float:
        """Calculate completion percentage based on work items"""
        work_items = self.get_work_items(session)
        if not work_items:
            return 0.0
        
        from dbr.models.work_item import WorkItemStatus
        completed_items = sum(1 for item in work_items if item.status == WorkItemStatus.DONE)
        return completed_items / len(work_items)
    
    def calculate_total_sales_price(self, session) -> float:
        """Calculate total sales price from all work items"""
        work_items = self.get_work_items(session)
        return sum(item.estimated_sales_price or 0.0 for item in work_items)
    
    def calculate_total_variable_cost(self, session) -> float:
        """Calculate total variable cost from all work items"""
        work_items = self.get_work_items(session)
        return sum(item.estimated_variable_cost or 0.0 for item in work_items)
    
    def calculate_total_throughput(self, session) -> float:
        """Calculate total throughput from all work items"""
        return self.calculate_total_sales_price(session) - self.calculate_total_variable_cost(session)
    
    def calculate_total_hours(self, session) -> float:
        """Calculate total estimated hours from all work items"""
        work_items = self.get_work_items(session)
        return sum(item.estimated_total_hours or 0.0 for item in work_items)
    
    # Analytics and reporting
    def get_analytics(self, session) -> dict:
        """Get comprehensive analytics for this collection"""
        from dbr.models.work_item import WorkItemStatus
        
        work_items = self.get_work_items(session)
        
        # Work item counts by status
        total_items = len(work_items)
        completed_items = sum(1 for item in work_items if item.status == WorkItemStatus.DONE)
        in_progress_items = sum(1 for item in work_items if item.status == WorkItemStatus.IN_PROGRESS)
        ready_items = sum(1 for item in work_items if item.status == WorkItemStatus.READY)
        backlog_items = sum(1 for item in work_items if item.status == WorkItemStatus.BACKLOG)
        
        # Financial calculations
        total_sales = self.calculate_total_sales_price(session)
        total_costs = self.calculate_total_variable_cost(session)
        total_throughput = self.calculate_total_throughput(session)
        
        # Effort calculations
        total_hours = self.calculate_total_hours(session)
        completed_hours = sum(
            item.estimated_total_hours or 0.0 
            for item in work_items 
            if item.status == WorkItemStatus.DONE
        )
        remaining_hours = total_hours - completed_hours
        
        # Collection vs work items variance
        collection_sales = self.estimated_sales_price or 0.0
        collection_costs = self.estimated_variable_cost or 0.0
        collection_throughput = self.calculate_throughput()
        
        return {
            # Work item counts
            "total_work_items": total_items,
            "completed_work_items": completed_items,
            "in_progress_work_items": in_progress_items,
            "ready_work_items": ready_items,
            "backlog_work_items": backlog_items,
            
            # Progress
            "completion_percentage": completed_items / total_items if total_items > 0 else 0.0,
            
            # Work item financial totals
            "total_estimated_sales": total_sales,
            "total_estimated_costs": total_costs,
            "total_estimated_throughput": total_throughput,
            
            # Effort analytics
            "total_estimated_hours": total_hours,
            "completed_hours": completed_hours,
            "remaining_hours": remaining_hours,
            
            # Collection-level estimates
            "collection_estimated_sales": collection_sales,
            "collection_estimated_costs": collection_costs,
            "collection_throughput": collection_throughput,
            
            # Variance analysis
            "sales_variance": collection_sales - total_sales,
            "cost_variance": collection_costs - total_costs,
            "throughput_variance": collection_throughput - total_throughput,
        }
    
    def get_work_items_by_status(self, session, status) -> list:
        """Get work items filtered by status"""
        from dbr.models.work_item import WorkItem
        return session.query(WorkItem).filter_by(
            collection_id=self.id, 
            status=status
        ).all()
    
    def get_blocked_work_items(self, session) -> list:
        """Get work items that are blocked by dependencies"""
        from dbr.core.dependencies import get_blocked_work_items
        all_blocked = get_blocked_work_items(session, self.organization_id)
        return [item for item in all_blocked if item.collection_id == self.id]
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', status='{self.status.value}')>"