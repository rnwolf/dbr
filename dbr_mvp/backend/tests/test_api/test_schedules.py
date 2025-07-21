# tests/test_api/test_schedules.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
from dbr.models.ccr import CCR, CCRType
from dbr.models.board_config import BoardConfig
from dbr.models.role import Role, RoleName
from dbr.models.user import User
from dbr.core.database import SessionLocal, create_tables


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def session():
    """Create a test database session"""
    create_tables()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_organization(session):
    """Create a test organization"""
    org = Organization(
        name="Test Organization",
        description="Test org for schedule API testing",
        status=OrganizationStatus.ACTIVE,
        contact_email="test@example.com",
        country="US"
    )
    session.add(org)
    session.commit()
    return org


@pytest.fixture
def test_ccr(session, test_organization):
    """Create a test CCR"""
    ccr = CCR(
        organization_id=test_organization.id,
        name="Development CCR",
        description="Development capacity constrained resource",
        ccr_type=CCRType.SKILL_BASED,
        capacity_per_time_unit=40.0
    )
    session.add(ccr)
    session.commit()
    return ccr


@pytest.fixture
def test_board_config(session, test_organization, test_ccr):
    """Create a test board configuration"""
    board_config = BoardConfig(
        organization_id=test_organization.id,
        name="Test DBR Board",
        description="Test DBR board configuration",
        ccr_id=test_ccr.id,
        pre_constraint_buffer_size=5,
        post_constraint_buffer_size=3,
        time_unit="week"
    )
    session.add(board_config)
    session.commit()
    return board_config


@pytest.fixture
def test_work_items(session, test_organization):
    """Create test work items for scheduling"""
    work_items = []
    
    for i in range(5):
        work_item = WorkItem(
            organization_id=test_organization.id,
            title=f"Ready Work Item {i+1}",
            description=f"Work item {i+1} ready for scheduling",
            status=WorkItemStatus.READY,
            priority=WorkItemPriority.MEDIUM,
            estimated_total_hours=8.0,
            ccr_hours_required={"development": 6.0, "testing": 2.0},
            estimated_sales_price=2000.0,
            estimated_variable_cost=600.0
        )
        work_items.append(work_item)
    
    session.add_all(work_items)
    session.commit()
    return work_items


@pytest.fixture
def test_schedules(session, test_organization, test_board_config, test_work_items):
    """Create test schedules"""
    schedules = []
    
    # Schedule 1: Planning status
    schedule1 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PLANNING,
        work_item_ids=[test_work_items[0].id, test_work_items[1].id],
        time_unit_position=-5,
        total_ccr_hours=16.0
    )
    
    # Schedule 2: Pre-constraint status
    schedule2 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PRE_CONSTRAINT,
        work_item_ids=[test_work_items[2].id],
        time_unit_position=-2,
        total_ccr_hours=8.0
    )
    
    # Schedule 3: Post-constraint status
    schedule3 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.POST_CONSTRAINT,
        work_item_ids=[test_work_items[3].id],
        time_unit_position=2,
        total_ccr_hours=8.0
    )
    
    schedules.extend([schedule1, schedule2, schedule3])
    session.add_all(schedules)
    session.commit()
    return schedules


def test_create_schedule_api(client, session, test_organization, test_board_config, test_work_items):
    """Test schedule creation via API"""
    # Test: POST /schedules creates schedule
    # Test: Work item list validation
    # Test: Capacity constraint enforcement
    
    schedule_data = {
        "organization_id": test_organization.id,
        "board_config_id": test_board_config.id,
        "work_item_ids": [test_work_items[0].id, test_work_items[1].id],
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/schedules", json=schedule_data)
    
    assert response.status_code == 201
    created_schedule = response.json()
    
    # Verify response structure
    assert "id" in created_schedule
    assert created_schedule["organization_id"] == test_organization.id
    assert created_schedule["board_config_id"] == test_board_config.id
    assert created_schedule["capability_channel_id"] == test_board_config.ccr_id
    assert created_schedule["status"] == "Planning"
    assert len(created_schedule["work_item_ids"]) == 2
    assert created_schedule["work_item_ids"] == [test_work_items[0].id, test_work_items[1].id]
    assert created_schedule["timezone"] == "UTC"
    assert created_schedule["time_unit_position"] == -5  # Start of pre-constraint buffer
    assert "total_ccr_time" in created_schedule
    assert "created_date" in created_schedule
    
    # Verify CCR time calculation
    assert created_schedule["total_ccr_time"] == 16.0  # 2 work items * 8 hours each (6 dev + 2 test)


def test_create_schedule_validation(client, session, test_organization, test_board_config, test_work_items):
    """Test schedule creation validation"""
    
    # Test missing required fields
    incomplete_data = {
        "organization_id": test_organization.id,
        "work_item_ids": [test_work_items[0].id]
        # Missing board_config_id
    }
    
    response = client.post("/api/v1/schedules", json=incomplete_data)
    assert response.status_code == 422  # Validation error
    
    # Test empty work item list
    empty_work_items_data = {
        "organization_id": test_organization.id,
        "board_config_id": test_board_config.id,
        "work_item_ids": [],
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/schedules", json=empty_work_items_data)
    assert response.status_code == 422
    
    # Test non-existent work items
    invalid_work_items_data = {
        "organization_id": test_organization.id,
        "board_config_id": test_board_config.id,
        "work_item_ids": ["non-existent-id"],
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/schedules", json=invalid_work_items_data)
    assert response.status_code == 400  # Bad request
    
    # Test capacity constraint violation
    # Create work items that exceed CCR capacity (40 hours)
    high_capacity_work_items = []
    for i in range(3):
        work_item = WorkItem(
            organization_id=test_organization.id,
            title=f"High Capacity Item {i+1}",
            status=WorkItemStatus.READY,
            estimated_total_hours=20.0,
            ccr_hours_required={"development": 18.0}  # 3 * 18 = 54 hours > 40 capacity
        )
        session.add(work_item)
        high_capacity_work_items.append(work_item)
    
    session.commit()
    
    over_capacity_data = {
        "organization_id": test_organization.id,
        "board_config_id": test_board_config.id,
        "work_item_ids": [item.id for item in high_capacity_work_items],
        "timezone": "UTC"
    }
    
    response = client.post("/api/v1/schedules", json=over_capacity_data)
    assert response.status_code == 400
    assert "capacity" in response.json()["detail"].lower()


def test_schedule_management_api(client, session, test_organization, test_schedules):
    """Test schedule lifecycle management"""
    # Test: GET /schedules (list with status filters)
    # Test: PUT /schedules/{id} (update status)
    # Test: Schedule completion marking
    
    # Test GET /schedules (list all)
    response = client.get(f"/api/v1/schedules?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    schedules = response.json()
    assert len(schedules) == 3
    assert all("id" in schedule for schedule in schedules)
    assert all("status" in schedule for schedule in schedules)
    
    # Test GET /schedules with status filter
    response = client.get(f"/api/v1/schedules?organization_id={test_organization.id}&status=Planning")
    assert response.status_code == 200
    
    planning_schedules = response.json()
    assert len(planning_schedules) == 1
    assert planning_schedules[0]["status"] == "Planning"
    
    # Test GET /schedules with multiple status filters
    response = client.get(f"/api/v1/schedules?organization_id={test_organization.id}&status=Planning&status=Pre-Constraint")
    assert response.status_code == 200
    
    filtered_schedules = response.json()
    assert len(filtered_schedules) == 2
    
    # Test GET /schedules with board config filter
    board_config_id = test_schedules[0].board_config_id
    response = client.get(f"/api/v1/schedules?organization_id={test_organization.id}&board_config_id={board_config_id}")
    assert response.status_code == 200
    
    board_schedules = response.json()
    assert len(board_schedules) == 3  # All schedules are on the same board
    
    # Test GET /schedules/{id} (single schedule)
    schedule_id = test_schedules[0].id
    response = client.get(f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    single_schedule = response.json()
    assert single_schedule["id"] == schedule_id
    assert single_schedule["status"] == "Planning"
    assert "work_item_ids" in single_schedule
    assert "time_unit_position" in single_schedule
    
    # Test PUT /schedules/{id} (update status)
    update_data = {
        "status": "Pre-Constraint",
        "time_unit_position": -3
    }
    
    response = client.put(
        f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}",
        json=update_data
    )
    assert response.status_code == 200
    
    updated_schedule = response.json()
    assert updated_schedule["status"] == "Pre-Constraint"
    assert updated_schedule["time_unit_position"] == -3
    
    # Test schedule completion
    completion_data = {
        "status": "Completed"
    }
    
    response = client.put(
        f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}",
        json=completion_data
    )
    assert response.status_code == 200
    
    completed_schedule = response.json()
    assert completed_schedule["status"] == "Completed"
    assert "completion_date" in completed_schedule
    assert completed_schedule["completion_date"] is not None


def test_schedule_work_item_management(client, session, test_organization, test_board_config, test_work_items, test_schedules):
    """Test work item management within schedules"""
    
    schedule_id = test_schedules[0].id
    
    # Test adding work items to schedule
    add_work_items_data = {
        "work_item_ids": [test_work_items[0].id, test_work_items[1].id, test_work_items[4].id]  # Add one more
    }
    
    response = client.put(
        f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}",
        json=add_work_items_data
    )
    assert response.status_code == 200
    
    updated_schedule = response.json()
    assert len(updated_schedule["work_item_ids"]) == 3
    assert test_work_items[4].id in updated_schedule["work_item_ids"]
    
    # Verify CCR time recalculation
    assert updated_schedule["total_ccr_time"] == 24.0  # 3 work items * 8 hours each (6 dev + 2 test)
    
    # Test removing work items from schedule
    remove_work_items_data = {
        "work_item_ids": [test_work_items[0].id]  # Keep only one
    }
    
    response = client.put(
        f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}",
        json=remove_work_items_data
    )
    assert response.status_code == 200
    
    updated_schedule = response.json()
    assert len(updated_schedule["work_item_ids"]) == 1
    assert updated_schedule["work_item_ids"][0] == test_work_items[0].id
    assert updated_schedule["total_ccr_time"] == 8.0  # 1 work item * 8 hours (6 dev + 2 test)


def test_schedule_error_handling(client, session, test_organization):
    """Test error handling for schedule API"""
    
    # Test 404 for non-existent schedule
    response = client.get(f"/api/v1/schedules/non-existent-id?organization_id={test_organization.id}")
    assert response.status_code == 404
    
    # Test 403 for wrong organization
    fake_org_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/schedules?organization_id={fake_org_id}")
    assert response.status_code == 403
    
    # Test 422 for missing organization_id
    response = client.get("/api/v1/schedules")
    assert response.status_code == 422  # Missing required query parameter


def test_schedule_analytics_and_metrics(client, session, test_organization, test_schedules):
    """Test schedule analytics and metrics"""
    
    # Test schedule analytics endpoint
    schedule_id = test_schedules[0].id
    response = client.get(f"/api/v1/schedules/{schedule_id}/analytics?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    analytics = response.json()
    assert "work_item_count" in analytics
    assert "total_ccr_hours" in analytics
    assert "buffer_zone" in analytics
    assert "position_info" in analytics
    assert "throughput_metrics" in analytics
    
    # Test board-level analytics
    board_config_id = test_schedules[0].board_config_id
    response = client.get(f"/api/v1/schedules/board/{board_config_id}/analytics?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    board_analytics = response.json()
    assert "total_schedules" in board_analytics
    assert "status_distribution" in board_analytics
    assert "zone_occupancy" in board_analytics
    assert "capacity_utilization" in board_analytics


def test_schedule_deletion(client, session, test_organization, test_schedules):
    """Test schedule deletion"""
    
    schedule_id = test_schedules[0].id
    
    # Test DELETE /schedules/{id}
    response = client.delete(f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/api/v1/schedules/{schedule_id}?organization_id={test_organization.id}")
    assert response.status_code == 404
    
    # Verify other schedules still exist
    response = client.get(f"/api/v1/schedules?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    remaining_schedules = response.json()
    assert len(remaining_schedules) == 2  # 3 - 1 deleted