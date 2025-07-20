# src/dbr/core/time_progression.py
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.board_config import BoardConfig
from dbr.models.ccr import CCR
from dbr.core.time_manager import TimeManager
from dbr.core.dependencies import can_work_item_be_ready


class BufferOverflowError(Exception):
    """Raised when buffer capacity would be exceeded"""
    pass


class TimeProgressionEngine:
    """Core engine for time progression and buffer management in DBR system"""
    
    def __init__(self, session: Session, time_manager: Optional[TimeManager] = None):
        self.session = session
        self.time_manager = time_manager or TimeManager()
    
    def advance_time(self, organization_id: str, check_overflow: bool = False) -> Dict[str, Any]:
        """Advance time by one unit for all schedules in an organization"""
        
        # Get current time before advancement
        previous_time = self.time_manager.get_current_time()
        
        # Get all active schedules
        schedules = self.session.query(Schedule).filter_by(
            organization_id=organization_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        # Check for buffer overflow
        overflow_warnings = self._check_buffer_overflow(organization_id, schedules)
        if check_overflow and overflow_warnings > 0:
            raise BufferOverflowError("Pre-constraint buffer is full")
        
        # Advance each schedule
        advanced_count = 0
        completed_count = 0
        status_changes = []
        
        for schedule in schedules:
            old_status = schedule.status
            old_position = schedule.time_unit_position
            
            # Advance position
            schedule.advance_position()
            
            # Update status based on new position
            self._update_schedule_status(schedule)
            
            # Track changes
            if schedule.status != old_status:
                status_changes.append({
                    "schedule_id": schedule.id,
                    "old_status": old_status.value,
                    "new_status": schedule.status.value,
                    "old_position": old_position,
                    "new_position": schedule.time_unit_position
                })
            
            if schedule.status == ScheduleStatus.COMPLETED:
                completed_count += 1
            
            advanced_count += 1
        
        # Advance time manager
        self.time_manager.advance_time(weeks=1)  # Advance by one time unit
        current_time = self.time_manager.get_current_time()
        
        # Check for dependency updates
        dependency_updates = self._check_dependency_updates(organization_id)
        
        # Commit all changes
        self.session.commit()
        
        return {
            "organization_id": organization_id,
            "advanced_schedules_count": advanced_count,
            "completed_schedules_count": completed_count,
            "remaining_schedules_count": advanced_count - completed_count,
            "status_changes": status_changes,
            "buffer_overflow_warnings": overflow_warnings,
            "dependency_updates": dependency_updates,
            "time_advancement": {
                "previous_time": previous_time,
                "current_time": current_time
            },
            "progression_timestamp": current_time
        }
    
    def advance_time_units(self, organization_id: str, units: int) -> List[Dict[str, Any]]:
        """Advance time by multiple units"""
        results = []
        for _ in range(units):
            result = self.advance_time(organization_id)
            results.append(result)
        return results
    
    def _update_schedule_status(self, schedule: Schedule) -> None:
        """Update schedule status based on its position"""
        buffer_zone = schedule.get_buffer_zone(self.session)
        
        if schedule.status == ScheduleStatus.PLANNING and buffer_zone == "pre_constraint":
            schedule.release_to_pre_constraint()
        elif schedule.status == ScheduleStatus.PRE_CONSTRAINT and buffer_zone == "post_constraint":
            schedule.move_to_post_constraint()
        elif schedule.time_unit_position > 2:  # Beyond post-constraint buffer
            schedule.mark_completed()
    
    def _check_buffer_overflow(self, organization_id: str, schedules: List[Schedule]) -> int:
        """Check for potential buffer overflow issues"""
        warnings = 0
        
        # Get all board configs for the organization
        board_configs = self.session.query(BoardConfig).filter_by(
            organization_id=organization_id,
            is_active=True
        ).all()
        
        for board_config in board_configs:
            buffer_status = self.get_buffer_status(organization_id, board_config.id)
            
            # Check pre-constraint buffer
            if buffer_status["pre_constraint"]["is_full"]:
                # Count schedules that would move into pre-constraint buffer
                incoming_schedules = [
                    s for s in schedules 
                    if s.board_config_id == board_config.id 
                    and s.time_unit_position == -board_config.pre_constraint_buffer_size - 1
                ]
                if incoming_schedules:
                    warnings += len(incoming_schedules)
        
        return warnings
    
    def _check_dependency_updates(self, organization_id: str) -> Dict[str, Any]:
        """Check for work items that can now be marked as Ready due to completed dependencies"""
        from dbr.core.dependencies import get_blocked_work_items
        
        # Get all blocked work items
        blocked_items = get_blocked_work_items(self.session, organization_id)
        resolved_dependencies = 0
        newly_ready_items = []
        
        for item in blocked_items:
            if can_work_item_be_ready(self.session, item.id):
                item.status = WorkItemStatus.READY
                newly_ready_items.append({
                    "work_item_id": item.id,
                    "title": item.title
                })
                resolved_dependencies += 1
        
        return {
            "resolved_dependencies": resolved_dependencies,
            "newly_ready_items": newly_ready_items,
            "total_blocked_items": len(blocked_items)
        }
    
    def get_buffer_status(self, organization_id: str, board_config_id: str) -> Dict[str, Any]:
        """Get current buffer status for a board configuration"""
        board_config = self.session.query(BoardConfig).filter_by(id=board_config_id).first()
        if not board_config:
            return {}
        
        # Get schedules in each buffer zone
        schedules = self.session.query(Schedule).filter_by(
            organization_id=organization_id,
            board_config_id=board_config_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        # Count schedules by buffer zone
        pre_constraint_schedules = []
        constraint_schedules = []
        post_constraint_schedules = []
        
        for schedule in schedules:
            zone = schedule.get_buffer_zone(self.session)
            if zone == "pre_constraint":
                pre_constraint_schedules.append(schedule)
            elif zone == "constraint":
                constraint_schedules.append(schedule)
            elif zone == "post_constraint":
                post_constraint_schedules.append(schedule)
        
        return {
            "board_config_id": board_config_id,
            "pre_constraint": {
                "current_count": len(pre_constraint_schedules),
                "max_capacity": board_config.pre_constraint_buffer_size,
                "is_full": len(pre_constraint_schedules) >= board_config.pre_constraint_buffer_size,
                "schedules": [s.id for s in pre_constraint_schedules]
            },
            "constraint": {
                "current_count": len(constraint_schedules),
                "max_capacity": 1,  # CCR can only handle one schedule at a time
                "is_full": len(constraint_schedules) >= 1,
                "schedules": [s.id for s in constraint_schedules]
            },
            "post_constraint": {
                "current_count": len(post_constraint_schedules),
                "max_capacity": board_config.post_constraint_buffer_size,
                "is_full": len(post_constraint_schedules) >= board_config.post_constraint_buffer_size,
                "schedules": [s.id for s in post_constraint_schedules]
            }
        }
    
    def get_organization_progression_analytics(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for time progression in an organization"""
        
        # Get all board configs
        board_configs = self.session.query(BoardConfig).filter_by(
            organization_id=organization_id,
            is_active=True
        ).all()
        
        total_schedules = 0
        total_work_items = 0
        buffer_analytics = {}
        
        for board_config in board_configs:
            buffer_status = self.get_buffer_status(organization_id, board_config.id)
            buffer_analytics[board_config.id] = buffer_status
            
            # Count schedules and work items
            board_schedules = self.session.query(Schedule).filter_by(
                organization_id=organization_id,
                board_config_id=board_config.id
            ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
            
            total_schedules += len(board_schedules)
            for schedule in board_schedules:
                total_work_items += len(schedule.work_item_ids)
        
        # Get dependency status
        dependency_updates = self._check_dependency_updates(organization_id)
        
        return {
            "organization_id": organization_id,
            "current_time": self.time_manager.get_current_time(),
            "total_active_schedules": total_schedules,
            "total_work_items_in_flow": total_work_items,
            "buffer_analytics": buffer_analytics,
            "dependency_status": dependency_updates,
            "board_count": len(board_configs)
        }
    
    def simulate_time_progression(self, organization_id: str, time_units: int) -> Dict[str, Any]:
        """Simulate time progression without actually advancing time (for planning)"""
        
        # Create a copy of current state for simulation
        simulation_results = []
        
        for unit in range(time_units):
            # Get current state
            current_analytics = self.get_organization_progression_analytics(organization_id)
            simulation_results.append({
                "time_unit": unit,
                "analytics": current_analytics
            })
            
            # Simulate advancement (without committing)
            schedules = self.session.query(Schedule).filter_by(
                organization_id=organization_id
            ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
            
            # Simulate position advancement
            for schedule in schedules:
                schedule.time_unit_position += 1
        
        # Rollback simulation changes
        self.session.rollback()
        
        return {
            "organization_id": organization_id,
            "simulated_time_units": time_units,
            "simulation_results": simulation_results
        }