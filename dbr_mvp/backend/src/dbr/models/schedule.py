# src/dbr/models/schedule.py
from sqlalchemy import Column, String, Enum, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship, Session
from dbr.models.base import BaseModel
import enum
from datetime import datetime, timezone
from typing import List, Optional


class ScheduleStatus(enum.Enum):
    """Schedule status enumeration"""
    PLANNING = "Planning"
    PRE_CONSTRAINT = "Pre-Constraint"
    POST_CONSTRAINT = "Post-Constraint"
    COMPLETED = "Completed"


class Schedule(BaseModel):
    """Schedule model - time unit-sized bundle of work items"""
    __tablename__ = "schedules"
    
    # Basic schedule information
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    board_config_id = Column(String(36), ForeignKey('board_configs.id'), nullable=False)
    capability_channel_id = Column(String(36), ForeignKey('ccrs.id'), nullable=False)
    
    # Schedule status and positioning
    status = Column(Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.PLANNING)
    time_unit_position = Column(Integer, nullable=False, default=0)  # Position relative to CCR
    
    # Work items and capacity
    work_item_ids = Column(JSON, nullable=False, default=list)  # Ordered list of work item IDs
    total_ccr_hours = Column(Float, nullable=False, default=0.0)
    
    # Lifecycle dates
    released_date = Column(DateTime, nullable=True)  # When moved to pre-constraint
    completed_date = Column(DateTime, nullable=True)  # When marked as complete
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="schedules")
    # board_config = relationship("BoardConfig", back_populates="schedules")
    # ccr = relationship("CCR", back_populates="schedules")
    
    def get_work_items(self, session: Session) -> List:
        """Get all work items in this schedule"""
        from dbr.models.work_item import WorkItem
        
        if not self.work_item_ids:
            return []
        
        work_items = []
        for work_item_id in self.work_item_ids:
            work_item = session.query(WorkItem).filter_by(id=work_item_id).first()
            if work_item:
                work_items.append(work_item)
        
        return work_items
    
    def add_work_item(self, session: Session, work_item_id: str) -> bool:
        """Add a work item to this schedule"""
        from dbr.models.work_item import WorkItem
        
        work_item = session.query(WorkItem).filter_by(id=work_item_id).first()
        if not work_item or work_item.organization_id != self.organization_id:
            return False
        
        if work_item_id not in self.work_item_ids:
            # Create a new list to trigger SQLAlchemy change detection
            new_work_item_ids = self.work_item_ids.copy()
            new_work_item_ids.append(work_item_id)
            self.work_item_ids = new_work_item_ids
            self.recalculate_total_hours(session)
            session.commit()
            return True
        
        return False
    
    def remove_work_item(self, session: Session, work_item_id: str) -> bool:
        """Remove a work item from this schedule"""
        if work_item_id in self.work_item_ids:
            # Create a new list to trigger SQLAlchemy change detection
            new_work_item_ids = self.work_item_ids.copy()
            new_work_item_ids.remove(work_item_id)
            self.work_item_ids = new_work_item_ids
            self.recalculate_total_hours(session)
            session.commit()
            return True
        
        return False
    
    def reorder_work_items(self, new_order: List[str]) -> None:
        """Reorder work items in the schedule"""
        # Validate that new_order contains the same items
        if set(new_order) == set(self.work_item_ids):
            self.work_item_ids = new_order
    
    def clear_work_items(self, session: Session) -> None:
        """Remove all work items from this schedule"""
        self.work_item_ids = []
        self.total_ccr_hours = 0.0
        session.commit()
    
    def calculate_total_ccr_hours(self, session: Session) -> float:
        """Calculate total CCR hours for all work items in this schedule"""
        work_items = self.get_work_items(session)
        
        total_hours = 0.0
        for work_item in work_items:
            if work_item.ccr_hours_required:
                # Sum all CCR hours for this work item (handles multi-CCR scenarios)
                work_item_ccr_hours = sum(work_item.ccr_hours_required.values())
                total_hours += work_item_ccr_hours
        
        return total_hours
    
    def recalculate_total_hours(self, session: Session) -> None:
        """Recalculate and update total CCR hours"""
        self.total_ccr_hours = self.calculate_total_ccr_hours(session)
    
    def validate_work_items(self, session: Session) -> bool:
        """Validate that all work items are in Ready status"""
        from dbr.models.work_item import WorkItem, WorkItemStatus
        from dbr.core.scheduling import ScheduleValidationError
        
        work_items = self.get_work_items(session)
        
        for work_item in work_items:
            if work_item.status != WorkItemStatus.READY:
                raise ScheduleValidationError(f"Work item {work_item.title} is not in Ready status")
        
        return True
    
    def validate_capacity(self, session: Session) -> bool:
        """Validate that schedule doesn't exceed CCR capacity"""
        from dbr.models.ccr import CCR
        from dbr.core.scheduling import ScheduleValidationError
        
        ccr = session.query(CCR).filter_by(id=self.capability_channel_id).first()
        if not ccr:
            raise ScheduleValidationError("CCR not found")
        
        if self.total_ccr_hours > ccr.capacity_per_time_unit:
            raise ScheduleValidationError(
                f"Schedule requires {self.total_ccr_hours} hours but CCR capacity is {ccr.capacity_per_time_unit} hours"
            )
        
        return True
    
    def validate(self, session: Session) -> bool:
        """Validate the entire schedule"""
        self.validate_work_items(session)
        self.validate_capacity(session)
        return True
    
    def advance_position(self) -> None:
        """Advance the schedule position by one time unit"""
        self.time_unit_position += 1
    
    def get_buffer_zone(self, session: Session) -> str:
        """Get the buffer zone this schedule is currently in"""
        from dbr.models.board_config import BoardConfig
        
        board_config = session.query(BoardConfig).filter_by(id=self.board_config_id).first()
        if not board_config:
            return "unknown"
        
        return board_config.get_position_zone(self.time_unit_position)
    
    def is_at_ccr(self) -> bool:
        """Check if schedule is at the CCR position"""
        return self.time_unit_position == 0
    
    def is_in_pre_constraint_buffer(self, session: Session) -> bool:
        """Check if schedule is in pre-constraint buffer"""
        return self.get_buffer_zone(session) == "pre_constraint"
    
    def is_in_post_constraint_buffer(self, session: Session) -> bool:
        """Check if schedule is in post-constraint buffer"""
        return self.get_buffer_zone(session) == "post_constraint"
    
    def release_to_pre_constraint(self) -> None:
        """Release schedule to pre-constraint buffer"""
        self.status = ScheduleStatus.PRE_CONSTRAINT
        self.released_date = datetime.now(timezone.utc)
    
    def move_to_post_constraint(self) -> None:
        """Move schedule to post-constraint buffer"""
        self.status = ScheduleStatus.POST_CONSTRAINT
    
    def mark_completed(self) -> None:
        """Mark schedule as completed"""
        self.status = ScheduleStatus.COMPLETED
        self.completed_date = datetime.now(timezone.utc)
    
    def get_analytics(self, session: Session) -> dict:
        """Get analytics for this schedule"""
        work_items = self.get_work_items(session)
        
        return {
            "schedule_id": self.id,
            "status": self.status.value,
            "position": self.time_unit_position,
            "buffer_zone": self.get_buffer_zone(session),
            "work_items_count": len(work_items),
            "total_ccr_hours": self.total_ccr_hours,
            "created_date": self.created_date,
            "released_date": self.released_date,
            "completed_date": self.completed_date,
        }
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, status='{self.status.value}', position={self.time_unit_position}, items={len(self.work_item_ids)})>"