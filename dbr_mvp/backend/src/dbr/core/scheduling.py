# src/dbr/core/scheduling.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.ccr import CCR
from dbr.models.board_config import BoardConfig


class ScheduleValidationError(Exception):
    """Raised when schedule validation fails"""
    pass


class SchedulingEngine:
    """Core scheduling engine for DBR operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_schedule(
        self, 
        organization_id: str, 
        board_config_id: str, 
        work_item_ids: List[str],
        validate: bool = True
    ) -> Schedule:
        """Create a new schedule with validation"""
        
        # Get board config and CCR
        board_config = self.session.query(BoardConfig).filter_by(id=board_config_id).first()
        if not board_config:
            raise ScheduleValidationError("Board configuration not found")
        
        ccr = self.session.query(CCR).filter_by(id=board_config.ccr_id).first()
        if not ccr:
            raise ScheduleValidationError("CCR not found")
        
        # Create schedule
        schedule = Schedule(
            organization_id=organization_id,
            board_config_id=board_config_id,
            capability_channel_id=ccr.id,
            status=ScheduleStatus.PLANNING,
            work_item_ids=work_item_ids,
            time_unit_position=-board_config.pre_constraint_buffer_size  # Start at beginning of buffer
        )
        
        # Calculate total hours
        schedule.recalculate_total_hours(self.session)
        
        # Validate if requested
        if validate:
            schedule.validate(self.session)
        
        self.session.add(schedule)
        self.session.commit()
        
        return schedule
    
    def advance_all_schedules(self, organization_id: str) -> Dict[str, Any]:
        """Advance all schedules by one time unit"""
        schedules = self.session.query(Schedule).filter_by(
            organization_id=organization_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        advanced_count = 0
        completed_count = 0
        
        for schedule in schedules:
            # Advance position
            schedule.advance_position()
            
            # Update status based on new position
            buffer_zone = schedule.get_buffer_zone(self.session)
            
            if buffer_zone == "pre_constraint" and schedule.status == ScheduleStatus.PLANNING:
                schedule.release_to_pre_constraint()
            elif buffer_zone == "post_constraint" and schedule.status == ScheduleStatus.PRE_CONSTRAINT:
                schedule.move_to_post_constraint()
            elif schedule.time_unit_position > 3:  # Completed after post-constraint buffer
                schedule.mark_completed()
                completed_count += 1
            
            advanced_count += 1
        
        self.session.commit()
        
        return {
            "advanced_schedules_count": advanced_count,
            "completed_schedules_count": completed_count,
            "remaining_schedules_count": advanced_count - completed_count
        }
    
    def get_schedules_by_status(self, organization_id: str, status: ScheduleStatus) -> List[Schedule]:
        """Get all schedules with a specific status"""
        return self.session.query(Schedule).filter_by(
            organization_id=organization_id,
            status=status
        ).all()
    
    def get_schedules_in_buffer_zone(self, organization_id: str, zone: str) -> List[Schedule]:
        """Get all schedules in a specific buffer zone"""
        schedules = self.session.query(Schedule).filter_by(organization_id=organization_id).all()
        
        zone_schedules = []
        for schedule in schedules:
            if schedule.get_buffer_zone(self.session) == zone:
                zone_schedules.append(schedule)
        
        return zone_schedules
    
    def get_board_analytics(self, organization_id: str, board_config_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a DBR board"""
        schedules = self.session.query(Schedule).filter_by(
            organization_id=organization_id,
            board_config_id=board_config_id
        ).all()
        
        # Count schedules by status
        status_counts = {}
        for status in ScheduleStatus:
            status_counts[status.value] = len([s for s in schedules if s.status == status])
        
        # Count schedules by buffer zone
        zone_counts = {
            "pre_constraint": len(self.get_schedules_in_buffer_zone(organization_id, "pre_constraint")),
            "constraint": len(self.get_schedules_in_buffer_zone(organization_id, "constraint")),
            "post_constraint": len(self.get_schedules_in_buffer_zone(organization_id, "post_constraint"))
        }
        
        # Calculate total work items and hours
        total_work_items = sum(len(s.work_item_ids) for s in schedules)
        total_hours = sum(s.total_ccr_hours for s in schedules)
        
        return {
            "board_config_id": board_config_id,
            "total_schedules": len(schedules),
            "status_counts": status_counts,
            "zone_counts": zone_counts,
            "total_work_items": total_work_items,
            "total_ccr_hours": total_hours,
            "schedules": [s.get_analytics(self.session) for s in schedules]
        }


def validate_schedule_creation(session: Session, work_item_ids: List[str], ccr_id: str) -> bool:
    """Validate that a schedule can be created with the given work items"""
    
    # Check that all work items exist and are Ready
    for work_item_id in work_item_ids:
        work_item = session.query(WorkItem).filter_by(id=work_item_id).first()
        if not work_item:
            raise ScheduleValidationError(f"Work item {work_item_id} not found")
        if work_item.status != WorkItemStatus.READY:
            raise ScheduleValidationError(f"Work item {work_item.title} is not in Ready status")
    
    # Check CCR capacity
    ccr = session.query(CCR).filter_by(id=ccr_id).first()
    if not ccr:
        raise ScheduleValidationError("CCR not found")
    
    # Calculate total hours required
    ccr_key = ccr.name.lower().replace(" ", "_")
    total_hours = 0.0
    
    for work_item_id in work_item_ids:
        work_item = session.query(WorkItem).filter_by(id=work_item_id).first()
        if work_item and work_item.ccr_hours_required:
            hours = work_item.ccr_hours_required.get(ccr_key, 0.0)
            total_hours += hours
    
    if total_hours > ccr.capacity_per_time_unit:
        raise ScheduleValidationError(
            f"Total hours ({total_hours}) exceeds CCR capacity ({ccr.capacity_per_time_unit})"
        )
    
    return True