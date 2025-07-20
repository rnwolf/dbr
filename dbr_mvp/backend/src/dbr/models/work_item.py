# src/dbr/models/work_item.py
from sqlalchemy import Column, String, Enum, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum
import json
from typing import Dict, List, Any, Optional


class WorkItemStatus(enum.Enum):
    """Work item status enumeration"""
    BACKLOG = "Backlog"
    READY = "Ready"
    STANDBY = "Standby"
    IN_PROGRESS = "In-Progress"
    DONE = "Done"


class WorkItemPriority(enum.Enum):
    """Work item priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkItem(BaseModel):
    """Work item model - fundamental unit of work in the DBR system"""
    __tablename__ = "work_items"
    
    # Basic work item information
    organization_id = Column(String(36), nullable=False)
    collection_id = Column(String(36), nullable=True)  # Can be null for standalone items
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling and status
    due_date = Column(DateTime, nullable=True)
    due_date_timezone = Column(String(50), nullable=True, default="UTC")
    status = Column(Enum(WorkItemStatus), nullable=False, default=WorkItemStatus.BACKLOG)
    priority = Column(Enum(WorkItemPriority), nullable=False, default=WorkItemPriority.MEDIUM)
    
    # Effort estimation
    estimated_total_hours = Column(Float, nullable=True, default=0.0)
    ccr_hours_required = Column(JSON, nullable=True)  # JSON object for CCR hours
    
    # Financial information
    estimated_sales_price = Column(Float, nullable=True, default=0.0)
    estimated_variable_cost = Column(Float, nullable=True, default=0.0)
    
    # Task management (JSON field)
    tasks = Column(JSON, nullable=True, default=list)
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="work_items")
    # collection = relationship("Collection", back_populates="work_items")
    
    def calculate_throughput(self) -> float:
        """Calculate work item throughput (sales_price - variable_cost)"""
        sales_price = self.estimated_sales_price or 0.0
        variable_cost = self.estimated_variable_cost or 0.0
        return sales_price - variable_cost
    
    def calculate_total_ccr_hours(self) -> float:
        """Calculate total CCR hours required"""
        if not self.ccr_hours_required:
            return 0.0
        return sum(self.ccr_hours_required.values())
    
    def update_ccr_hours(self, ccr_name: str, hours: float) -> None:
        """Update hours for a specific CCR"""
        if not self.ccr_hours_required:
            self.ccr_hours_required = {}
        self.ccr_hours_required[ccr_name] = hours
    
    def add_ccr_hours(self, ccr_name: str, hours: float) -> None:
        """Add hours for a new CCR"""
        if not self.ccr_hours_required:
            self.ccr_hours_required = {}
        self.ccr_hours_required[ccr_name] = hours
    
    def get_ccr_hours(self, ccr_name: str) -> float:
        """Get hours for a specific CCR"""
        if not self.ccr_hours_required:
            return 0.0
        return self.ccr_hours_required.get(ccr_name, 0.0)
    
    # Task management methods
    def add_task(self, title: str, task_id: int = None) -> None:
        """Add a new task to the work item"""
        if not self.tasks:
            self.tasks = []
        
        if task_id is None:
            # Generate next ID
            existing_ids = [task.get("id", 0) for task in self.tasks]
            task_id = max(existing_ids, default=0) + 1
        
        new_task = {
            "id": task_id,
            "title": title,
            "completed": False
        }
        self.tasks.append(new_task)
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        if not self.tasks:
            return False
        
        for task in self.tasks:
            if task.get("id") == task_id:
                task["completed"] = True
                return True
        return False
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by its ID"""
        if not self.tasks:
            return None
        
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None
    
    def calculate_progress(self) -> float:
        """Calculate progress based on completed tasks"""
        if not self.tasks or len(self.tasks) == 0:
            return 0.0
        
        completed_tasks = sum(1 for task in self.tasks if task.get("completed", False))
        return completed_tasks / len(self.tasks)
    
    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get all completed tasks"""
        if not self.tasks:
            return []
        return [task for task in self.tasks if task.get("completed", False)]
    
    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks"""
        if not self.tasks:
            return []
        return [task for task in self.tasks if not task.get("completed", False)]
    
    def __repr__(self):
        return f"<WorkItem(id={self.id}, title='{self.title}', status='{self.status.value}', priority='{self.priority.value}')>"