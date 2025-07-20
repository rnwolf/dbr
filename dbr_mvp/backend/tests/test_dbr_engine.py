# tests/test_dbr_engine.py
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dbr.services.dbr_engine import DBREngine
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.ccr import CCR, CCRType
from dbr.models.board_config import BoardConfig
from dbr.models.role import Role, RoleName
from dbr.models.user import User
from dbr.core.database import SessionLocal, create_tables


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
        description="Test org for DBR engine testing",
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
        name="Test CCR",
        description="Test capacity constrained resource",
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
        name="Test Board",
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
    """Create test work items"""
    work_items = []
    for i in range(3):
        work_item = WorkItem(
            organization_id=test_organization.id,
            title=f"Test Work Item {i+1}",
            description=f"Test work item {i+1} description",
            status=WorkItemStatus.READY,
            estimated_total_hours=8.0,
            ccr_hours_required={"test_ccr": 8.0}
        )
        session.add(work_item)
        work_items.append(work_item)
    
    session.commit()
    return work_items


@pytest.fixture
def test_schedules(session, test_organization, test_board_config, test_work_items):
    """Create test schedules at different positions"""
    schedules = []
    
    # Schedule 1: At pre-constraint buffer start (-5)
    schedule1 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PLANNING,
        work_item_ids=[test_work_items[0].id],
        time_unit_position=-5,
        total_ccr_hours=8.0
    )
    
    # Schedule 2: At CCR (0)
    schedule2 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PRE_CONSTRAINT,
        work_item_ids=[test_work_items[1].id],
        time_unit_position=0,
        total_ccr_hours=8.0
    )
    
    # Schedule 3: At post-constraint buffer (+2)
    schedule3 = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.POST_CONSTRAINT,
        work_item_ids=[test_work_items[2].id],
        time_unit_position=2,
        total_ccr_hours=8.0
    )
    
    schedules.extend([schedule1, schedule2, schedule3])
    session.add_all(schedules)
    session.commit()
    return schedules


def test_advance_time_unit(session, test_organization, test_schedules):
    """Test core time progression functionality"""
    # Test: All schedules move one position left
    # Test: Completed schedules removed from board
    # Test: Schedule count tracking
    
    engine = DBREngine(session)
    result = engine.advance_time_unit(test_organization.id)
    
    # Should advance all 3 schedules
    assert result["advanced_schedules_count"] == 3
    assert result["completed_schedules_count"] == 0  # None should complete in one step
    assert result["remaining_schedules_count"] == 3
    
    # Check that positions were advanced (moved left = position increased)
    session.refresh(test_schedules[0])  # Was at -5, should be at -4
    session.refresh(test_schedules[1])  # Was at 0, should be at +1
    session.refresh(test_schedules[2])  # Was at +2, should be at +3
    
    assert test_schedules[0].time_unit_position == -4
    assert test_schedules[1].time_unit_position == 1
    assert test_schedules[2].time_unit_position == 3


def test_time_progression_with_multiple_schedules(session, test_organization, test_board_config, test_work_items):
    """Test complex time progression scenarios"""
    # Test: Multiple schedules at different positions
    # Test: Some complete, some continue
    # Test: Buffer zone transitions
    
    # Create schedules at various positions
    schedules = []
    
    # Schedule at end of post-constraint buffer (will complete)
    completing_schedule = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.POST_CONSTRAINT,
        work_item_ids=[test_work_items[0].id],
        time_unit_position=3,  # At end of 3-unit post-constraint buffer
        total_ccr_hours=8.0
    )
    
    # Schedule transitioning from pre-constraint to CCR
    transitioning_schedule = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PLANNING,
        work_item_ids=[test_work_items[1].id],
        time_unit_position=-1,  # Will move to CCR (position 0)
        total_ccr_hours=8.0
    )
    
    schedules.extend([completing_schedule, transitioning_schedule])
    session.add_all(schedules)
    session.commit()
    
    engine = DBREngine(session)
    result = engine.advance_time_unit(test_organization.id)
    
    # Should advance 2 schedules, complete 1
    assert result["advanced_schedules_count"] == 2
    assert result["completed_schedules_count"] == 1
    assert result["remaining_schedules_count"] == 1
    
    # Check status transitions
    session.refresh(completing_schedule)
    session.refresh(transitioning_schedule)
    
    assert completing_schedule.status == ScheduleStatus.COMPLETED
    assert transitioning_schedule.time_unit_position == 0  # Now at CCR
    assert transitioning_schedule.status == ScheduleStatus.PRE_CONSTRAINT  # Status should update