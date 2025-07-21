# src/dbr/api/schedules.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from dbr.core.database import get_db
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.organization import Organization
from dbr.models.board_config import BoardConfig
from dbr.models.ccr import CCR
from dbr.services.dbr_engine import DBREngine


router = APIRouter(prefix="/schedules", tags=["Schedules"])


# Pydantic schemas for request/response
class ScheduleCreate(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    board_config_id: str = Field(..., description="Board configuration ID")
    work_item_ids: List[str] = Field(..., description="List of work item IDs")
    timezone: str = Field(default="UTC", description="Timezone for schedule dates")


class ScheduleUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Schedule status")
    work_item_ids: Optional[List[str]] = Field(None, description="Updated work item IDs")
    time_unit_position: Optional[int] = Field(None, description="Time unit position")
    released_date: Optional[datetime] = Field(None, description="Released date")
    completion_date: Optional[datetime] = Field(None, description="Completion date")


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    organization_id: str
    board_config_id: str
    capability_channel_id: str
    status: str
    work_item_ids: List[str]
    time_unit_position: int
    total_ccr_time: float
    timezone: str
    created_date: str
    released_date: Optional[str]
    completion_date: Optional[str]


class ScheduleAnalytics(BaseModel):
    work_item_count: int
    total_ccr_hours: float
    buffer_zone: str
    position_info: Dict[str, Any]
    throughput_metrics: Dict[str, Any]


class BoardAnalytics(BaseModel):
    total_schedules: int
    status_distribution: Dict[str, int]
    zone_occupancy: Dict[str, int]
    capacity_utilization: Dict[str, float]


def _validate_organization_access(session: Session, organization_id: str) -> Organization:
    """Validate that the organization exists and user has access"""
    org = session.query(Organization).filter_by(id=organization_id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Access denied to organization")
    return org


def _convert_schedule_to_response(schedule: Schedule) -> Dict[str, Any]:
    """Convert Schedule model to response dictionary"""
    
    return {
        "id": schedule.id,
        "organization_id": schedule.organization_id,
        "board_config_id": schedule.board_config_id,
        "capability_channel_id": schedule.capability_channel_id,
        "status": schedule.status.value,
        "work_item_ids": schedule.work_item_ids or [],
        "time_unit_position": schedule.time_unit_position,
        "total_ccr_time": schedule.total_ccr_hours,
        "timezone": "UTC",  # TODO: Add timezone field to Schedule model
        "created_date": schedule.created_date.isoformat(),
        "released_date": schedule.released_date.isoformat() if schedule.released_date else None,
        "completion_date": schedule.completed_date.isoformat() if schedule.completed_date else None
    }


@router.get("", response_model=List[ScheduleResponse])
def get_schedules(
    organization_id: str = Query(..., description="Organization ID to filter by"),
    board_config_id: Optional[str] = Query(None, description="Board configuration ID to filter by"),
    status: Optional[List[str]] = Query(None, description="Status to filter by"),
    session: Session = Depends(get_db)
):
    """Get all schedules with optional filtering"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Build query
    query = session.query(Schedule).filter_by(organization_id=organization_id)
    
    # Apply filters
    if board_config_id:
        query = query.filter_by(board_config_id=board_config_id)
    
    if status:
        # Convert string statuses to enum values
        status_enums = []
        for s in status:
            try:
                # Find enum by value (e.g., "Planning" -> ScheduleStatus.PLANNING)
                found_status = None
                for status_enum in ScheduleStatus:
                    if status_enum.value == s:
                        found_status = status_enum
                        break
                
                if found_status:
                    status_enums.append(found_status)
                else:
                    raise ValueError(f"Status '{s}' not found")
                    
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {s}")
        query = query.filter(Schedule.status.in_(status_enums))
    
    # Order by creation date
    query = query.order_by(Schedule.created_date.desc())
    
    schedules = query.all()
    
    # Convert to response format
    return [_convert_schedule_to_response(schedule) for schedule in schedules]


@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    schedule_data: ScheduleCreate,
    session: Session = Depends(get_db)
):
    """Create a new schedule"""
    
    # Validate organization access
    _validate_organization_access(session, schedule_data.organization_id)
    
    # Validate board configuration exists
    board_config = session.query(BoardConfig).filter_by(id=schedule_data.board_config_id).first()
    if not board_config:
        raise HTTPException(status_code=400, detail="Board configuration not found")
    
    # Validate work items exist and are ready
    if not schedule_data.work_item_ids:
        raise HTTPException(status_code=422, detail="Work item list cannot be empty")
    
    work_items = session.query(WorkItem).filter(
        WorkItem.id.in_(schedule_data.work_item_ids),
        WorkItem.organization_id == schedule_data.organization_id
    ).all()
    
    if len(work_items) != len(schedule_data.work_item_ids):
        raise HTTPException(status_code=400, detail="One or more work items not found")
    
    # Check that all work items are in Ready status
    non_ready_items = [wi for wi in work_items if wi.status != WorkItemStatus.READY]
    if non_ready_items:
        raise HTTPException(
            status_code=400, 
            detail=f"Work items must be in Ready status. Found {len(non_ready_items)} non-ready items"
        )
    
    # Get CCR for capacity validation
    ccr = session.query(CCR).filter_by(id=board_config.ccr_id).first()
    if not ccr:
        raise HTTPException(status_code=400, detail="CCR not found for board configuration")
    
    # Calculate total CCR hours and validate capacity
    total_ccr_hours = 0.0
    
    for work_item in work_items:
        if work_item.ccr_hours_required:
            # Sum all CCR hours for this work item (since we don't know the exact key structure)
            work_item_ccr_hours = sum(work_item.ccr_hours_required.values())
            total_ccr_hours += work_item_ccr_hours
    
    if total_ccr_hours > ccr.capacity_per_time_unit:
        raise HTTPException(
            status_code=400,
            detail=f"Total CCR hours ({total_ccr_hours}) exceeds capacity ({ccr.capacity_per_time_unit})"
        )
    
    # Create schedule using DBREngine
    try:
        dbr_engine = DBREngine(session)
        schedule = dbr_engine.create_schedule(
            organization_id=schedule_data.organization_id,
            board_config_id=schedule_data.board_config_id,
            work_item_ids=schedule_data.work_item_ids
        )
        
        return _convert_schedule_to_response(schedule)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Get a specific schedule by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get schedule
    schedule = session.query(Schedule).filter_by(
        id=schedule_id,
        organization_id=organization_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return _convert_schedule_to_response(schedule)


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: str,
    schedule_data: ScheduleUpdate,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Update a schedule by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get schedule
    schedule = session.query(Schedule).filter_by(
        id=schedule_id,
        organization_id=organization_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update fields
    update_data = schedule_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value is not None:
            try:
                # Find enum by value (e.g., "Pre-Constraint" -> ScheduleStatus.PRE_CONSTRAINT)
                found_status = None
                for status_enum in ScheduleStatus:
                    if status_enum.value == value:
                        found_status = status_enum
                        break
                
                if found_status:
                    schedule.status = found_status
                    
                    # Set completion date if marking as completed
                    if found_status == ScheduleStatus.COMPLETED and not schedule.completed_date:
                        schedule.completed_date = datetime.now(timezone.utc)
                else:
                    raise ValueError(f"Status '{value}' not found")
                    
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {value}")
                
        elif field == "work_item_ids" and value is not None:
            # Validate work items and recalculate CCR hours
            work_items = session.query(WorkItem).filter(
                WorkItem.id.in_(value),
                WorkItem.organization_id == organization_id
            ).all()
            
            if len(work_items) != len(value):
                raise HTTPException(status_code=400, detail="One or more work items not found")
            
            schedule.work_item_ids = value
            schedule.recalculate_total_hours(session)
            
        else:
            setattr(schedule, field, value)
    
    session.commit()
    session.refresh(schedule)
    
    return _convert_schedule_to_response(schedule)


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Delete a schedule by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get schedule
    schedule = session.query(Schedule).filter_by(
        id=schedule_id,
        organization_id=organization_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    session.delete(schedule)
    session.commit()


@router.get("/{schedule_id}/analytics", response_model=ScheduleAnalytics)
def get_schedule_analytics(
    schedule_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Get analytics for a specific schedule"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get schedule
    schedule = session.query(Schedule).filter_by(
        id=schedule_id,
        organization_id=organization_id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Get schedule analytics
    analytics = schedule.get_analytics(session)
    
    # Calculate buffer zone
    buffer_zone = schedule.get_buffer_zone(session)
    
    # Calculate throughput metrics
    work_items = schedule.get_work_items(session)
    total_throughput = sum(item.calculate_throughput() for item in work_items)
    
    return {
        "work_item_count": len(schedule.work_item_ids),
        "total_ccr_hours": schedule.total_ccr_hours,
        "buffer_zone": buffer_zone,
        "position_info": {
            "current_position": schedule.time_unit_position,
            "zone": buffer_zone,
            "status": schedule.status.value
        },
        "throughput_metrics": {
            "total_throughput": total_throughput,
            "average_throughput_per_item": total_throughput / len(work_items) if work_items else 0,
            "ccr_utilization": analytics.get("ccr_utilization", 0.0)
        }
    }


@router.get("/board/{board_config_id}/analytics", response_model=BoardAnalytics)
def get_board_analytics(
    board_config_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Get analytics for all schedules on a specific board"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get all schedules for the board
    schedules = session.query(Schedule).filter_by(
        organization_id=organization_id,
        board_config_id=board_config_id
    ).all()
    
    # Calculate status distribution
    status_distribution = {}
    for status in ScheduleStatus:
        status_distribution[status.value] = len([s for s in schedules if s.status == status])
    
    # Calculate zone occupancy
    zone_occupancy = {
        "pre_constraint": 0,
        "constraint": 0,
        "post_constraint": 0
    }
    
    for schedule in schedules:
        zone = schedule.get_buffer_zone(session)
        if zone in zone_occupancy:
            zone_occupancy[zone] += 1
    
    # Calculate capacity utilization
    board_config = session.query(BoardConfig).filter_by(id=board_config_id).first()
    ccr = session.query(CCR).filter_by(id=board_config.ccr_id).first() if board_config else None
    
    total_ccr_hours = sum(s.total_ccr_hours for s in schedules)
    max_capacity = ccr.capacity_per_time_unit if ccr else 1.0
    
    capacity_utilization = {
        "total_hours_scheduled": total_ccr_hours,
        "max_capacity": max_capacity,
        "utilization_percentage": (total_ccr_hours / max_capacity) * 100 if max_capacity > 0 else 0
    }
    
    return {
        "total_schedules": len(schedules),
        "status_distribution": status_distribution,
        "zone_occupancy": zone_occupancy,
        "capacity_utilization": capacity_utilization
    }