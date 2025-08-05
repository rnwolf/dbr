# tests/test_models/test_schedule.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_schedule_creation():
    """Test schedule creation with work items"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
    from dbr.models.work_item_dependency import (
        WorkItemDependency,
    )  # Import to ensure table is created
    from dbr.models.ccr_user_association import (
        CCRUserAssociation,
    )  # Import to ensure table is created
    from dbr.models.organization_membership import (
        OrganizationMembership,
    )  # Import to ensure table is created
    from dbr.models.base import Base

    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Create test organization
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic",
            )
            session.add(org)
            session.commit()

            # Create test collection
            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0,
            )
            session.add(collection)
            session.commit()

            # Create test CCR
            ccr = CCR(
                organization_id=org.id,
                name="Senior Developers",
                description="Senior development team",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=40.0,
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            # Create test board config
            board_config = BoardConfig(
                organization_id=org.id,
                name="Default Board",
                description="Default DBR board configuration",
                ccr_id=ccr.id,
                pre_constraint_buffer_size=5,
                post_constraint_buffer_size=3,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
            session.commit()

            # Create test work items
            work_items = []
            for i in range(3):
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i + 1}",
                    description=f"Description for work item {i + 1}",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"senior_developers": 8.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                work_items.append(work_item)
                session.add(work_item)

            session.commit()

            # Test: Create schedule with work item list
            work_item_ids = [item.id for item in work_items]
            schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=work_item_ids,
                total_ccr_hours=24.0,  # 3 items * 8 hours each
                time_unit_position=0,  # Starting position
            )
            session.add(schedule)
            session.commit()

            # Test: Schedule created successfully
            assert schedule.id is not None
            assert schedule.organization_id == org.id
            assert schedule.board_config_id == board_config.id
            assert schedule.capability_channel_id == ccr.id
            assert schedule.status == ScheduleStatus.PLANNING
            assert len(schedule.work_item_ids) == 3
            assert schedule.total_ccr_hours == 24.0
            assert isinstance(uuid.UUID(schedule.id), uuid.UUID)

            # Test: Work item list management
            work_items_in_schedule = schedule.get_work_items(session)
            assert len(work_items_in_schedule) == 3

            # Test: CCR hours calculation
            calculated_hours = schedule.calculate_total_ccr_hours(session)
            assert calculated_hours == 24.0

            # Test: Schedule validation
            assert schedule.validate_work_items(session)
    finally:
        engine.dispose()


def test_schedule_capacity_validation():
    """Test CCR time validation (cannot exceed capacity)"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
    from dbr.models.work_item_dependency import (
        WorkItemDependency,
    )  # Import to ensure table is created
    from dbr.models.ccr_user_association import (
        CCRUserAssociation,
    )  # Import to ensure table is created
    from dbr.models.organization_membership import (
        OrganizationMembership,
    )  # Import to ensure table is created
    from dbr.models.base import Base
    from dbr.core.scheduling import ScheduleValidationError

    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Create test data
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic",
            )
            session.add(org)
            session.commit()

            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0,
            )
            session.add(collection)
            session.commit()

            # Create CCR with limited capacity
            ccr = CCR(
                organization_id=org.id,
                name="Senior Developers",
                description="Senior development team",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=30.0,  # Only 30 hours capacity
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            board_config = BoardConfig(
                organization_id=org.id,
                name="Default Board",
                description="Default DBR board configuration",
                ccr_id=ccr.id,
                pre_constraint_buffer_size=5,
                post_constraint_buffer_size=3,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
            session.commit()

            # Test: Only Ready work items can be scheduled
            ready_items = []
            backlog_items = []

            for i in range(2):
                # Ready items
                ready_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Ready Item {i + 1}",
                    description=f"Ready work item {i + 1}",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=10.0,
                    ccr_hours_required={"senior_developers": 10.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                ready_items.append(ready_item)
                session.add(ready_item)

                # Backlog items (should not be schedulable)
                backlog_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Backlog Item {i + 1}",
                    description=f"Backlog work item {i + 1}",
                    status=WorkItemStatus.BACKLOG,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=10.0,
                    ccr_hours_required={"senior_developers": 10.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                backlog_items.append(backlog_item)
                session.add(backlog_item)

            session.commit()

            # Test: Reject schedules exceeding CCR capacity
            over_capacity_items = ready_items + [
                ready_items[0]
            ]  # 3 items * 10 hours = 30 hours (at capacity)
            over_capacity_item_ids = [item.id for item in over_capacity_items]

            # Add one more item to exceed capacity
            extra_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Extra Item",
                description="Item that exceeds capacity",
                status=WorkItemStatus.READY,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=5.0,
                ccr_hours_required={"senior_developers": 5.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0,
            )
            session.add(extra_item)
            session.commit()

            over_capacity_item_ids.append(extra_item.id)

            # Test: Schedule validation should fail for over-capacity
            over_capacity_schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=over_capacity_item_ids,
                total_ccr_hours=35.0,  # Exceeds 30 hour capacity
                time_unit_position=0,
            )

            with pytest.raises(
                ScheduleValidationError,
                match="Schedule requires .* hours but CCR capacity is",
            ):
                over_capacity_schedule.validate_capacity(session)

            # Test: Multiple work items fit within capacity
            valid_item_ids = [
                item.id for item in ready_items
            ]  # 2 items * 10 hours = 20 hours
            valid_schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=valid_item_ids,
                total_ccr_hours=20.0,
                time_unit_position=0,
            )
            session.add(valid_schedule)
            session.commit()

            # Test: Valid schedule should pass validation
            assert valid_schedule.validate_capacity(session)

            # Test: Cannot schedule backlog items
            backlog_item_ids = [item.id for item in backlog_items]
            backlog_schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=backlog_item_ids,
                total_ccr_hours=20.0,
                time_unit_position=0,
            )

            with pytest.raises(ScheduleValidationError, match="not in Ready status"):
                backlog_schedule.validate_work_items(session)
    finally:
        engine.dispose()


def test_schedule_status_and_positioning():
    """Test schedule status and positioning system"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
    from dbr.models.work_item_dependency import (
        WorkItemDependency,
    )  # Import to ensure table is created
    from dbr.models.ccr_user_association import (
        CCRUserAssociation,
    )  # Import to ensure table is created
    from dbr.models.organization_membership import (
        OrganizationMembership,
    )  # Import to ensure table is created
    from dbr.models.base import Base

    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Create test data
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic",
            )
            session.add(org)
            session.commit()

            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0,
            )
            session.add(collection)
            session.commit()

            ccr = CCR(
                organization_id=org.id,
                name="Senior Developers",
                description="Senior development team",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=40.0,
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            board_config = BoardConfig(
                organization_id=org.id,
                name="Default Board",
                description="Default DBR board configuration",
                ccr_id=ccr.id,
                pre_constraint_buffer_size=5,
                post_constraint_buffer_size=3,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
            session.commit()

            # Create work item
            work_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Test Work Item",
                description="Test work item",
                status=WorkItemStatus.READY,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"senior_developers": 8.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0,
            )
            session.add(work_item)
            session.commit()

            # Test: Time slot offset from CCR (0 = CCR, +1 = right, -1 = left)
            schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=[work_item.id],
                total_ccr_hours=8.0,
                time_unit_position=-3,  # 3 positions to the left of CCR
            )
            session.add(schedule)
            session.commit()

            # Test: Schedule status based on position
            assert schedule.get_buffer_zone(session) == "pre_constraint"

            # Test: Position updates during time progression
            schedule.advance_position()
            assert schedule.time_unit_position == -2

            schedule.advance_position()
            assert schedule.time_unit_position == -1

            schedule.advance_position()
            assert schedule.time_unit_position == 0  # At CCR
            assert schedule.get_buffer_zone(session) == "constraint"

            schedule.advance_position()
            assert schedule.time_unit_position == 1  # Post-constraint
            assert schedule.get_buffer_zone(session) == "post_constraint"

            # Test: Status changes trigger position updates
            schedule.status = ScheduleStatus.PRE_CONSTRAINT
            session.commit()
            assert schedule.status == ScheduleStatus.PRE_CONSTRAINT

            schedule.status = ScheduleStatus.POST_CONSTRAINT
            session.commit()
            assert schedule.status == ScheduleStatus.POST_CONSTRAINT

            schedule.status = ScheduleStatus.COMPLETED
            schedule.completed_date = datetime.now(timezone.utc)
            session.commit()
            assert schedule.status == ScheduleStatus.COMPLETED
            assert schedule.completed_date is not None
    finally:
        engine.dispose()


def test_schedule_work_item_management():
    """Test schedule work item list management"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
    from dbr.models.work_item_dependency import (
        WorkItemDependency,
    )  # Import to ensure table is created
    from dbr.models.ccr_user_association import (
        CCRUserAssociation,
    )  # Import to ensure table is created
    from dbr.models.organization_membership import (
        OrganizationMembership,
    )  # Import to ensure table is created
    from dbr.models.base import Base

    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            # Create test data
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic",
            )
            session.add(org)
            session.commit()

            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0,
            )
            session.add(collection)
            session.commit()

            ccr = CCR(
                organization_id=org.id,
                name="Senior Developers",
                description="Senior development team",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=40.0,
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            board_config = BoardConfig(
                organization_id=org.id,
                name="Default Board",
                description="Default DBR board configuration",
                ccr_id=ccr.id,
                pre_constraint_buffer_size=5,
                post_constraint_buffer_size=3,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
            session.commit()

            # Create work items
            work_items = []
            for i in range(4):
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i + 1}",
                    description=f"Description for work item {i + 1}",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"senior_developers": 8.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                work_items.append(work_item)
                session.add(work_item)

            session.commit()

            # Create schedule with initial work items
            initial_items = work_items[:2]
            schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=[item.id for item in initial_items],
                total_ccr_hours=16.0,
                time_unit_position=0,
            )
            session.add(schedule)
            session.commit()

            # Test: Add work item to schedule
            schedule.add_work_item(session, work_items[2].id)
            assert len(schedule.work_item_ids) == 3
            assert schedule.total_ccr_hours == 24.0

            # Test: Remove work item from schedule
            schedule.remove_work_item(session, work_items[0].id)
            assert len(schedule.work_item_ids) == 2
            assert schedule.total_ccr_hours == 16.0

            # Test: Get work items in schedule
            items_in_schedule = schedule.get_work_items(session)
            assert len(items_in_schedule) == 2

            # Test: Reorder work items in schedule
            original_order = schedule.work_item_ids.copy()
            schedule.reorder_work_items([original_order[1], original_order[0]])
            assert schedule.work_item_ids[0] == original_order[1]
            assert schedule.work_item_ids[1] == original_order[0]

            # Test: Clear all work items
            schedule.clear_work_items(session)
            assert len(schedule.work_item_ids) == 0
            assert schedule.total_ccr_hours == 0.0
    finally:
        engine.dispose()
