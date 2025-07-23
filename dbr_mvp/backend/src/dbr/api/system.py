# src/dbr/api/system.py
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from dbr.core.database import get_db
from dbr.services.dbr_engine import DBREngine
from dbr.models.organization import Organization
from dbr.models.user import User
from dbr.core.time_manager import TimeManager
import uuid

# Import auth dependency
try:
    from dbr.api.auth import get_current_user
except ImportError:
    # Handle circular import during testing
    def get_current_user():
        from dbr.api.auth import get_current_user as _get_current_user
        return _get_current_user


router = APIRouter(prefix="/system", tags=["System"])


class AdvanceTimeResponse(BaseModel):
    """Response model for advance_time_unit endpoint"""
    message: str = Field(..., description="Success message")
    advanced_schedules_count: int = Field(..., description="Number of schedules that were advanced")


@router.post("/advance_time_unit", response_model=AdvanceTimeResponse)
def advance_time_unit(
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    board_config_id: Optional[str] = Query(None, description="Optional board config ID to filter schedules"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> AdvanceTimeResponse:
    """
    Advance all schedules one time unit left (Manual/Fast-Forward)
    
    This operation simulates the passage of time, moving all active schedules 
    one time slot to the left on the DBR board. This can be triggered manually 
    (e.g., "Fast-Forward" button) or automatically by the system.
    """
    
    # Validate UUID format
    try:
        uuid.UUID(organization_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid organization_id format. Must be a valid UUID.")
    
    if board_config_id:
        try:
            uuid.UUID(board_config_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid board_config_id format. Must be a valid UUID.")
    
    # Validate organization exists
    organization = session.query(Organization).filter_by(id=organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Initialize DBR Engine with time manager
    time_manager = TimeManager()
    dbr_engine = DBREngine(session=session, time_manager=time_manager)
    
    try:
        # Call the existing DBREngine.advance_time_unit method
        result = dbr_engine.advance_time_unit(organization_id)
        
        return AdvanceTimeResponse(
            message="All active schedules advanced one time unit.",
            advanced_schedules_count=result["advanced_schedules_count"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error advancing time: {str(e)}")


@router.get("/time")
def get_current_time(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the current system time"""
    time_manager = TimeManager()
    current_time = time_manager.get_current_time()
    
    return {
        "current_time": current_time.isoformat(),
        "timezone": "UTC"
    }


@router.post("/time")
def set_system_time(
    time_iso: str = Query(..., description="ISO format datetime to set as system time"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Set the system time (for testing purposes)"""
    time_manager = TimeManager()
    
    try:
        # Parse and set the time
        from datetime import datetime
        new_time = datetime.fromisoformat(time_iso.replace('Z', '+00:00'))
        time_manager.set_time(new_time)
        
        return {
            "message": "System time updated successfully",
            "new_time": time_manager.get_current_time().isoformat(),
            "timezone": "UTC"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting time: {str(e)}")