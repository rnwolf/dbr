# tests/test_api/test_system.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.board_config import BoardConfig
from dbr.models.ccr import CCR
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.organization import Organization
from dbr.core.time_manager import TimeManager


client = TestClient(app)


def test_advance_time_unit_api_endpoint_exists():
    """Test that the advance_time_unit API endpoint exists"""
    # This test should FAIL initially since we haven't implemented the endpoint yet
    response = client.post("/api/v1/system/advance_time_unit")
    
    # We expect this to fail with 404 initially, then pass when implemented
    assert response.status_code != 404, "Endpoint should exist"


def test_advance_time_unit_api_requires_organization_id():
    """Test that advance_time_unit API requires organization_id parameter"""
    # This test should FAIL initially
    response = client.post("/api/v1/system/advance_time_unit")
    
    # Should fail with 422 (validation error) when organization_id is missing
    assert response.status_code == 422, "Should require organization_id parameter"


def test_advance_time_unit_api_with_valid_organization(session, test_organization, test_schedules):
    """Test advance_time_unit API with valid organization ID"""
    # This test should FAIL initially since endpoint doesn't exist
    
    # Setup: Create some schedules in different positions
    schedule1, schedule2, schedule3 = test_schedules
    
    # Record initial positions
    initial_positions = {
        schedule1.id: schedule1.time_unit_position,
        schedule2.id: schedule2.time_unit_position,
        schedule3.id: schedule3.time_unit_position
    }
    
    # Make API call
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={test_organization.id}"
    )
    
    # Should succeed when implemented
    assert response.status_code == 200
    
    # Check response format matches OpenAPI spec
    data = response.json()
    assert "message" in data
    assert "advanced_schedules_count" in data
    assert isinstance(data["advanced_schedules_count"], int)
    assert data["advanced_schedules_count"] >= 0


def test_advance_time_unit_api_moves_schedules_left(session, test_organization, test_schedules):
    """Test that advance_time_unit API actually moves schedules one position left"""
    # This test should FAIL initially
    
    schedule1, schedule2, schedule3 = test_schedules
    
    # Record initial positions
    initial_positions = {
        schedule1.id: schedule1.time_unit_position,
        schedule2.id: schedule2.time_unit_position,
        schedule3.id: schedule3.time_unit_position
    }
    
    # Make API call
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={test_organization.id}"
    )
    
    assert response.status_code == 200
    
    # Refresh schedules from database
    session.refresh(schedule1)
    session.refresh(schedule2)
    session.refresh(schedule3)
    
    # Verify each schedule moved one position left (position increased by 1)
    assert schedule1.time_unit_position == initial_positions[schedule1.id] + 1
    assert schedule2.time_unit_position == initial_positions[schedule2.id] + 1
    assert schedule3.time_unit_position == initial_positions[schedule3.id] + 1


def test_advance_time_unit_api_completes_schedules_beyond_buffer(session, test_organization, test_board_config):
    """Test that schedules beyond post-constraint buffer are marked as completed"""
    # This test should FAIL initially
    
    # Create a schedule at the edge of completion
    schedule = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.POST_CONSTRAINT,
        work_item_ids=["WI-001"],
        time_unit_position=test_board_config.post_constraint_buffer_size,  # At the edge
        total_ccr_hours=4.0
    )
    session.add(schedule)
    session.commit()
    
    # Make API call
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={test_organization.id}"
    )
    
    assert response.status_code == 200
    
    # Refresh schedule
    session.refresh(schedule)
    
    # Should be completed now
    assert schedule.status == ScheduleStatus.COMPLETED
    assert schedule.completed_date is not None


def test_advance_time_unit_api_with_invalid_organization():
    """Test advance_time_unit API with invalid organization ID"""
    # This test should FAIL initially
    
    invalid_org_id = "00000000-0000-0000-0000-000000000000"
    
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={invalid_org_id}"
    )
    
    # Should handle invalid org gracefully
    assert response.status_code in [200, 404]  # Either succeeds with 0 schedules or returns 404


def test_advance_time_unit_api_returns_correct_counts(session, test_organization, test_schedules):
    """Test that advance_time_unit API returns accurate schedule counts"""
    # This test should FAIL initially
    
    # Count initial active schedules
    initial_active_count = len([s for s in test_schedules if s.status != ScheduleStatus.COMPLETED])
    
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={test_organization.id}"
    )
    
    assert response.status_code == 200
    
    data = response.json()
    
    # The count should match our expectation
    assert data["advanced_schedules_count"] == initial_active_count


def test_advance_time_unit_api_with_board_config_filter(session, test_organization, test_board_config):
    """Test advance_time_unit API with optional board_config_id filter"""
    # This test should FAIL initially - testing optional parameter from OpenAPI spec
    
    response = client.post(
        f"/api/v1/system/advance_time_unit?organization_id={test_organization.id}&board_config_id={test_board_config.id}"
    )
    
    # Should succeed when implemented
    assert response.status_code == 200
    
    data = response.json()
    assert "advanced_schedules_count" in data


def test_advance_time_unit_api_error_handling():
    """Test advance_time_unit API error handling for malformed requests"""
    # This test should FAIL initially
    
    # Test with malformed UUID
    response = client.post("/api/v1/system/advance_time_unit?organization_id=invalid-uuid")
    
    # Should return validation error
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])