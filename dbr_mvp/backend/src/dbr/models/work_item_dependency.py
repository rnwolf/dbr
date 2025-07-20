# src/dbr/models/work_item_dependency.py
from sqlalchemy import Column, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum


class DependencyType(enum.Enum):
    """Work item dependency type enumeration"""
    FINISH_TO_START = "finish_to_start"
    START_TO_START = "start_to_start"
    FINISH_TO_FINISH = "finish_to_finish"
    START_TO_FINISH = "start_to_finish"


class WorkItemDependency(BaseModel):
    """Work item dependency model - represents dependencies between work items"""
    __tablename__ = "work_item_dependencies"
    
    # Dependency relationship
    dependent_work_item_id = Column(String(36), ForeignKey('work_items.id'), nullable=False)
    prerequisite_work_item_id = Column(String(36), ForeignKey('work_items.id'), nullable=False)
    
    # Dependency configuration
    dependency_type = Column(Enum(DependencyType), nullable=False, default=DependencyType.FINISH_TO_START)
    description = Column(Text, nullable=True)
    
    # Relationships (can be added later when needed)
    # dependent_work_item = relationship("WorkItem", foreign_keys=[dependent_work_item_id], back_populates="dependencies")
    # prerequisite_work_item = relationship("WorkItem", foreign_keys=[prerequisite_work_item_id], back_populates="prerequisites")
    
    def __repr__(self):
        return f"<WorkItemDependency(id={self.id}, dependent={self.dependent_work_item_id}, prerequisite={self.prerequisite_work_item_id}, type={self.dependency_type.value})>"