# tests/conftest.py
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