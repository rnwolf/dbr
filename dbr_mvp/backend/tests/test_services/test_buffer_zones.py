# tests/test_services/test_buffer_zones.py
import pytest
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from dbr.services.buffer_zone_manager import BufferZoneManager, BufferZoneStatus, BufferAlert
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.schedule import Schedule, ScheduleStatus
from dbr.models.work_item import WorkItem, WorkItemStatus
from dbr.models.ccr import CCR, CCRType
from dbr.models.board_config import BoardConfig
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
        description="Test org for buffer zone testing",
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
    for i in range(6):
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


def test_buffer_zone_configuration(session, test_organization, test_board_config):
    """Test buffer zone setup"""
    # Test: Pre-constraint buffer size (e.g., 5 time units)
    # Test: Post-constraint buffer size (e.g., 3 time units) 
    # Test: Zone color calculations (red/yellow/green)
    
    buffer_manager = BufferZoneManager(session)
    config = buffer_manager.get_buffer_configuration(test_board_config.id)
    
    # Test buffer sizes
    assert config["pre_constraint_buffer_size"] == 5
    assert config["post_constraint_buffer_size"] == 3
    assert config["total_board_size"] == 9  # 5 + 1 (CCR) + 3
    
    # Test zone boundaries
    assert config["pre_constraint_start"] == -5
    assert config["pre_constraint_end"] == -1
    assert config["ccr_position"] == 0
    assert config["post_constraint_start"] == 1
    assert config["post_constraint_end"] == 3
    
    # Test zone color thresholds
    zone_colors = buffer_manager.get_zone_color_thresholds(test_board_config.id)
    
    # Pre-constraint buffer colors (red = full, yellow = warning, green = healthy)
    assert zone_colors["pre_constraint"]["red_threshold"] == 5  # 100% full
    assert zone_colors["pre_constraint"]["yellow_threshold"] == 3  # 60% full
    assert zone_colors["pre_constraint"]["green_threshold"] == 2  # 40% or less
    
    # Post-constraint buffer colors
    assert zone_colors["post_constraint"]["red_threshold"] == 3  # 100% full
    assert zone_colors["post_constraint"]["yellow_threshold"] == 1  # 60% full (1.8 rounded down to 1)
    assert zone_colors["post_constraint"]["green_threshold"] == 1  # 40% or less (1.2 rounded down to 1)


def test_buffer_zone_status(session, test_organization, test_board_config, test_work_items):
    """Test buffer zone status calculation"""
    # Test: Zone penetration detection
    # Test: Alert generation for zone violations
    # Test: Buffer health metrics
    
    buffer_manager = BufferZoneManager(session)
    
    # Create schedules to fill different zones
    schedules = []
    
    # Fill pre-constraint buffer (positions -5 to -1)
    for i in range(5):
        schedule = Schedule(
            organization_id=test_organization.id,
            board_config_id=test_board_config.id,
            capability_channel_id=test_board_config.ccr_id,
            status=ScheduleStatus.PLANNING,
            work_item_ids=[test_work_items[i].id],
            time_unit_position=-(5-i),  # -5, -4, -3, -2, -1
            total_ccr_hours=8.0
        )
        schedules.append(schedule)
    
    # Add one in post-constraint buffer
    schedule = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.POST_CONSTRAINT,
        work_item_ids=[test_work_items[5].id],
        time_unit_position=2,
        total_ccr_hours=8.0
    )
    schedules.append(schedule)
    
    session.add_all(schedules)
    session.commit()
    
    # Test zone status calculation
    zone_status = buffer_manager.calculate_zone_status(test_board_config.id)
    
    # Pre-constraint buffer should be RED (100% full)
    assert zone_status["pre_constraint"]["status"] == BufferZoneStatus.RED
    assert zone_status["pre_constraint"]["occupancy_count"] == 5
    assert zone_status["pre_constraint"]["occupancy_percentage"] == 100.0
    assert zone_status["pre_constraint"]["available_slots"] == 0
    
    # Post-constraint buffer should be YELLOW (33% full, but threshold is 1 slot)
    assert zone_status["post_constraint"]["status"] == BufferZoneStatus.YELLOW
    assert zone_status["post_constraint"]["occupancy_count"] == 1
    assert zone_status["post_constraint"]["occupancy_percentage"] == 33.33
    assert zone_status["post_constraint"]["available_slots"] == 2
    
    # Test alert generation
    alerts = buffer_manager.generate_buffer_alerts(test_board_config.id)
    
    # Should have a RED alert for pre-constraint buffer
    red_alerts = [alert for alert in alerts if alert.severity == "RED"]
    assert len(red_alerts) == 1
    assert red_alerts[0].zone == "pre_constraint"
    assert "buffer is full" in red_alerts[0].message.lower()
    
    # Should have a YELLOW alert for post-constraint buffer (now at threshold)
    yellow_alerts = [alert for alert in alerts if alert.severity == "YELLOW"]
    post_alerts = [alert for alert in alerts if alert.zone == "post_constraint"]
    assert len(post_alerts) == 1
    assert post_alerts[0].severity == "YELLOW"


def test_buffer_health_metrics(session, test_organization, test_board_config, test_work_items):
    """Test comprehensive buffer health monitoring"""
    
    buffer_manager = BufferZoneManager(session)
    
    # Create a mixed scenario with different zone occupancies
    schedules = []
    
    # Partially fill pre-constraint buffer (3 out of 5 slots = YELLOW)
    for i in range(3):
        schedule = Schedule(
            organization_id=test_organization.id,
            board_config_id=test_board_config.id,
            capability_channel_id=test_board_config.ccr_id,
            status=ScheduleStatus.PLANNING,
            work_item_ids=[test_work_items[i].id],
            time_unit_position=-(3-i),  # -3, -2, -1
            total_ccr_hours=8.0
        )
        schedules.append(schedule)
    
    # Add one at CCR
    schedule = Schedule(
        organization_id=test_organization.id,
        board_config_id=test_board_config.id,
        capability_channel_id=test_board_config.ccr_id,
        status=ScheduleStatus.PRE_CONSTRAINT,
        work_item_ids=[test_work_items[3].id],
        time_unit_position=0,
        total_ccr_hours=8.0
    )
    schedules.append(schedule)
    
    # Partially fill post-constraint buffer (2 out of 3 slots = YELLOW)
    for i in range(2):
        schedule = Schedule(
            organization_id=test_organization.id,
            board_config_id=test_board_config.id,
            capability_channel_id=test_board_config.ccr_id,
            status=ScheduleStatus.POST_CONSTRAINT,
            work_item_ids=[test_work_items[4+i].id],
            time_unit_position=i+1,  # 1, 2
            total_ccr_hours=8.0
        )
        schedules.append(schedule)
    
    session.add_all(schedules)
    session.commit()
    
    # Test comprehensive health metrics
    health_metrics = buffer_manager.get_buffer_health_metrics(test_board_config.id)
    
    # Overall board health
    assert health_metrics["overall_status"] == BufferZoneStatus.YELLOW
    assert health_metrics["total_schedules"] == 6
    assert health_metrics["ccr_occupied"] == True
    
    # Pre-constraint metrics
    pre_metrics = health_metrics["pre_constraint"]
    assert pre_metrics["status"] == BufferZoneStatus.YELLOW  # 60% full
    assert pre_metrics["occupancy_count"] == 3
    assert pre_metrics["occupancy_percentage"] == 60.0
    
    # Post-constraint metrics
    post_metrics = health_metrics["post_constraint"]
    assert post_metrics["status"] == BufferZoneStatus.YELLOW  # 67% full
    assert post_metrics["occupancy_count"] == 2
    assert post_metrics["occupancy_percentage"] == 66.67
    
    # Flow metrics
    flow_metrics = health_metrics["flow_metrics"]
    assert flow_metrics["throughput_rate"] >= 0
    assert "bottleneck_risk" in flow_metrics
    assert "buffer_penetration" in flow_metrics


def test_buffer_zone_penetration_detection(session, test_organization, test_board_config, test_work_items):
    """Test detection of buffer zone penetration (overflow scenarios)"""
    
    buffer_manager = BufferZoneManager(session)
    
    # Test scenario: Try to add more schedules than buffer capacity
    schedules = []
    
    # Fill pre-constraint buffer beyond capacity (6 schedules in 5-slot buffer)
    for i in range(6):
        schedule = Schedule(
            organization_id=test_organization.id,
            board_config_id=test_board_config.id,
            capability_channel_id=test_board_config.ccr_id,
            status=ScheduleStatus.PLANNING,
            work_item_ids=[test_work_items[i].id],
            time_unit_position=-(6-i),  # -6, -5, -4, -3, -2, -1 (first one at -6 is overflow)
            total_ccr_hours=8.0
        )
        schedules.append(schedule)
    
    session.add_all(schedules)
    session.commit()
    
    # Test penetration detection
    penetration_status = buffer_manager.detect_buffer_penetration(test_board_config.id)
    
    assert penetration_status["has_penetration"] == True
    assert penetration_status["penetrated_zones"] == ["pre_constraint"]
    assert penetration_status["overflow_count"] == 1
    assert penetration_status["overflow_positions"] == [-6]
    
    # Test alerts for penetration
    alerts = buffer_manager.generate_buffer_alerts(test_board_config.id)
    penetration_alerts = [alert for alert in alerts if "penetration" in alert.message.lower()]
    assert len(penetration_alerts) >= 1
    assert penetration_alerts[0].severity == "CRITICAL"