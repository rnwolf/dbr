# src/dbr/services/dbr_engine.py
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.board_config import BoardConfig
from dbr.core.time_manager import TimeManager


class DBREngine:
    """Core DBR engine for orchestrating time progression and schedule management"""
    
    def __init__(self, session: Session, time_manager: Optional[TimeManager] = None):
        self.session = session
        self.time_manager = time_manager or TimeManager()
    
    def advance_time_unit(self, organization_id: str) -> Dict[str, Any]:
        """Advance all schedules by one time unit (move left on the board)"""
        
        # Get all active schedules for the organization
        schedules = self.session.query(Schedule).filter_by(
            organization_id=organization_id
        ).filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        advanced_count = 0
        completed_count = 0
        
        for schedule in schedules:
            # Store original position for tracking
            original_position = schedule.time_unit_position
            
            # Advance position (move left = increase position)
            schedule.time_unit_position += 1
            advanced_count += 1
            
            # Get board configuration to determine buffer zones
            board_config = self.session.query(BoardConfig).filter_by(
                id=schedule.board_config_id
            ).first()
            
            if board_config:
                # Update status based on new position
                self._update_schedule_status(schedule, board_config)
                
                # Check if schedule has completed (moved beyond post-constraint buffer)
                if schedule.time_unit_position > board_config.post_constraint_buffer_size:
                    schedule.status = ScheduleStatus.COMPLETED
                    schedule.completion_date = self.time_manager.get_current_time()
                    completed_count += 1
        
        # Advance system time by one time unit
        self.time_manager.advance_time(weeks=1)
        
        # Commit all changes
        self.session.commit()
        
        remaining_count = advanced_count - completed_count
        
        return {
            "advanced_schedules_count": advanced_count,
            "completed_schedules_count": completed_count,
            "remaining_schedules_count": remaining_count,
            "time_advancement": {
                "previous_time": self.time_manager.get_current_time(),
                "current_time": self.time_manager.get_current_time()
            }
        }
    
    def _update_schedule_status(self, schedule: Schedule, board_config: BoardConfig) -> None:
        """Update schedule status based on its position relative to buffer zones"""
        
        position = schedule.time_unit_position
        
        # Determine which zone the schedule is in
        if position < 0:
            # Pre-constraint buffer zone
            if schedule.status == ScheduleStatus.PLANNING:
                schedule.status = ScheduleStatus.PLANNING  # Stay in planning until ready
        elif position == 0:
            # At the CCR (constraint)
            if schedule.status in [ScheduleStatus.PLANNING, ScheduleStatus.PRE_CONSTRAINT]:
                schedule.status = ScheduleStatus.PRE_CONSTRAINT
        elif position > 0:
            # Post-constraint buffer zone
            if schedule.status == ScheduleStatus.PRE_CONSTRAINT:
                schedule.status = ScheduleStatus.POST_CONSTRAINT
                schedule.released_date = self.time_manager.get_current_time()
    
    def get_board_status(self, organization_id: str, board_config_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current status of all schedules on the board"""
        
        query = self.session.query(Schedule).filter_by(organization_id=organization_id)
        if board_config_id:
            query = query.filter_by(board_config_id=board_config_id)
        
        schedules = query.filter(Schedule.status != ScheduleStatus.COMPLETED).all()
        
        # Group schedules by position
        position_map = {}
        for schedule in schedules:
            pos = schedule.time_unit_position
            if pos not in position_map:
                position_map[pos] = []
            position_map[pos].append({
                "id": schedule.id,
                "status": schedule.status.value,
                "work_item_count": len(schedule.work_item_ids),
                "total_ccr_hours": schedule.total_ccr_hours
            })
        
        # Count schedules by status
        status_counts = {}
        for status in ScheduleStatus:
            status_counts[status.value] = len([s for s in schedules if s.status == status])
        
        return {
            "organization_id": organization_id,
            "board_config_id": board_config_id,
            "total_active_schedules": len(schedules),
            "status_counts": status_counts,
            "position_map": position_map,
            "current_time": self.time_manager.get_current_time().isoformat()
        }
    
    def create_schedule(self, organization_id: str, board_config_id: str, work_item_ids: List[str]) -> Schedule:
        """Create a new schedule with the given work items"""
        
        # Get board configuration
        board_config = self.session.query(BoardConfig).filter_by(id=board_config_id).first()
        if not board_config:
            raise ValueError(f"Board configuration {board_config_id} not found")
        
        # Create schedule at the start of pre-constraint buffer
        schedule = Schedule(
            organization_id=organization_id,
            board_config_id=board_config_id,
            capability_channel_id=board_config.ccr_id,
            status=ScheduleStatus.PLANNING,
            work_item_ids=work_item_ids,
            time_unit_position=-board_config.pre_constraint_buffer_size,
            total_ccr_hours=0.0  # Will be calculated
        )
        
        # Calculate total CCR hours
        schedule.recalculate_total_hours(self.session)
        
        # Validate schedule
        schedule.validate(self.session)
        
        self.session.add(schedule)
        self.session.commit()
        
        return schedule