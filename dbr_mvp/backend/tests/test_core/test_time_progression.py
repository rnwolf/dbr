# tests/test_core/test_time_progression.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from freezegun import freeze_time


def test_time_progression_basic():
    """Test basic time progression functionality"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.work_item_dependency import WorkItemDependency
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.base import Base
    from dbr.core.time_progression import TimeProgressionEngine

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

            # Create test CCR and board config
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
                pre_constraint_buffer_size=3,
                post_constraint_buffer_size=2,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
            session.commit()

            # Create test collection and work items
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

            # Create schedules at different positions
            schedules = []
            for i in range(3):
                schedule = Schedule(
                    organization_id=org.id,
                    board_config_id=board_config.id,
                    capability_channel_id=ccr.id,
                    status=ScheduleStatus.PLANNING,
                    work_item_ids=[work_item.id],
                    total_ccr_hours=8.0,
                    time_unit_position=-3 + i,  # Positions: -3, -2, -1
                )
                schedules.append(schedule)
                session.add(schedule)

            session.commit()

            # Test: Time progression advances all schedules
            time_engine = TimeProgressionEngine(session)
            result = time_engine.advance_time(org.id)

            # Verify all schedules advanced by 1 position
            for i, schedule in enumerate(schedules):
                session.refresh(schedule)
                expected_position = -3 + i + 1  # Original position + 1
                assert schedule.time_unit_position == expected_position

            # Test: Result contains progression statistics
            assert result["advanced_schedules_count"] == 3
            assert result["organization_id"] == org.id
            assert "progression_timestamp" in result
    finally:
        engine.dispose()


def test_buffer_zone_management():
    """Test buffer zone status updates during progression"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.work_item_dependency import WorkItemDependency
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.base import Base
    from dbr.core.time_progression import TimeProgressionEngine

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
                pre_constraint_buffer_size=2,
                post_constraint_buffer_size=2,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
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

            # Test: Schedule transitions through buffer zones
            schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=[work_item.id],
                total_ccr_hours=8.0,
                time_unit_position=-2,  # Start in pre-constraint buffer
            )
            session.add(schedule)
            session.commit()

            time_engine = TimeProgressionEngine(session)

            # Test: Planning -> Pre-Constraint
            assert schedule.status == ScheduleStatus.PLANNING
            time_engine.advance_time(org.id)
            session.refresh(schedule)
            assert schedule.time_unit_position == -1
            assert schedule.status == ScheduleStatus.PRE_CONSTRAINT
            assert schedule.released_date is not None

            # Test: Pre-Constraint -> Constraint (CCR)
            time_engine.advance_time(org.id)
            session.refresh(schedule)
            assert schedule.time_unit_position == 0
            assert schedule.get_buffer_zone(session) == "constraint"

            # Test: Constraint -> Post-Constraint
            time_engine.advance_time(org.id)
            session.refresh(schedule)
            assert schedule.time_unit_position == 1
            assert schedule.status == ScheduleStatus.POST_CONSTRAINT

            # Test: Post-Constraint -> Completed
            time_engine.advance_time(org.id)
            session.refresh(schedule)
            assert schedule.time_unit_position == 2

            time_engine.advance_time(org.id)  # Move beyond post-constraint buffer
            session.refresh(schedule)
            assert schedule.time_unit_position == 3
            assert schedule.status == ScheduleStatus.COMPLETED
            assert schedule.completed_date is not None
    finally:
        engine.dispose()


def test_buffer_overflow_protection():
    """Test buffer overflow protection and capacity management"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.work_item_dependency import WorkItemDependency
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.base import Base
    from dbr.core.time_progression import TimeProgressionEngine, BufferOverflowError

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
                pre_constraint_buffer_size=2,  # Small buffer for testing
                post_constraint_buffer_size=2,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
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

            # Create multiple work items
            work_items = []
            for i in range(3):
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i + 1}",
                    description=f"Work item {i + 1}",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=15.0,  # High hours to test capacity
                    ccr_hours_required={"senior_developers": 15.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                work_items.append(work_item)
                session.add(work_item)

            session.commit()

            # Test: Fill pre-constraint buffer to capacity
            schedules = []
            for i in range(2):  # Fill the 2-slot pre-constraint buffer
                schedule = Schedule(
                    organization_id=org.id,
                    board_config_id=board_config.id,
                    capability_channel_id=ccr.id,
                    status=ScheduleStatus.PRE_CONSTRAINT,
                    work_item_ids=[work_items[i].id],
                    total_ccr_hours=15.0,
                    time_unit_position=-1 - i,  # Positions: -1, -2
                )
                schedules.append(schedule)
                session.add(schedule)

            session.commit()

            time_engine = TimeProgressionEngine(session)

            # Test: Buffer capacity validation
            buffer_status = time_engine.get_buffer_status(org.id, board_config.id)
            assert buffer_status["pre_constraint"]["current_count"] == 2
            assert buffer_status["pre_constraint"]["max_capacity"] == 2
            assert buffer_status["pre_constraint"]["is_full"] is True

            # Test: Attempt to add schedule to full buffer
            overflow_schedule = Schedule(
                organization_id=org.id,
                board_config_id=board_config.id,
                capability_channel_id=ccr.id,
                status=ScheduleStatus.PLANNING,
                work_item_ids=[work_items[2].id],
                total_ccr_hours=15.0,
                time_unit_position=-3,  # Would move to -2 (full buffer)
            )
            session.add(overflow_schedule)
            session.commit()

            # Test: Buffer overflow protection
            with pytest.raises(
                BufferOverflowError, match="Pre-constraint buffer is full"
            ):
                time_engine.advance_time(org.id, check_overflow=True)

            # Test: Force advancement without overflow protection
            result = time_engine.advance_time(org.id, check_overflow=False)
            assert result["buffer_overflow_warnings"] > 0
    finally:
        engine.dispose()


def test_time_progression_with_dependencies():
    """Test time progression with work item dependencies"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.work_item_dependency import WorkItemDependency, DependencyType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.base import Base
    from dbr.core.time_progression import TimeProgressionEngine

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
                pre_constraint_buffer_size=3,
                post_constraint_buffer_size=2,
                time_unit="week",
                is_active=True,
            )
            session.add(board_config)
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

            # Create work items with dependencies
            prerequisite_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Prerequisite Item",
                description="Must be completed first",
                status=WorkItemStatus.BACKLOG,  # Not ready yet
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=8.0,
                ccr_hours_required={"senior_developers": 8.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0,
            )

            dependent_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Dependent Item",
                description="Depends on prerequisite",
                status=WorkItemStatus.BACKLOG,  # Cannot be ready until prerequisite is done
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"senior_developers": 8.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0,
            )

            session.add_all([prerequisite_item, dependent_item])
            session.commit()

            # Create dependency
            dependency = WorkItemDependency(
                dependent_work_item_id=dependent_item.id,
                prerequisite_work_item_id=prerequisite_item.id,
                dependency_type=DependencyType.FINISH_TO_START,
            )
            session.add(dependency)
            session.commit()

            # Test: Complete prerequisite and check dependent item status
            prerequisite_item.status = WorkItemStatus.DONE
            session.commit()

            time_engine = TimeProgressionEngine(session)

            # Test: Dependency resolution during time progression
            result = time_engine.advance_time(org.id)

            # Check if dependent item became ready
            session.refresh(dependent_item)
            from dbr.core.dependencies import can_work_item_be_ready

            assert can_work_item_be_ready(session, dependent_item.id)

            # Test: Dependency tracking in progression results
            assert "dependency_updates" in result
            assert result["dependency_updates"]["resolved_dependencies"] >= 0
    finally:
        engine.dispose()


def test_time_manager_integration():
    """Test integration with TimeManager for manual time control"""
    from dbr.models.schedule import Schedule, ScheduleStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.board_config import BoardConfig
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.work_item_dependency import WorkItemDependency
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.base import Base
    from dbr.core.time_progression import TimeProgressionEngine
    from dbr.core.time_manager import TimeManager

    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)

        with freeze_time("2024-01-15 10:00:00") as frozen_time:
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
                    pre_constraint_buffer_size=2,
                    post_constraint_buffer_size=2,
                    time_unit="week",
                    is_active=True,
                )
                session.add(board_config)
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

                schedule = Schedule(
                    organization_id=org.id,
                    board_config_id=board_config.id,
                    capability_channel_id=ccr.id,
                    status=ScheduleStatus.PLANNING,
                    work_item_ids=[work_item.id],
                    total_ccr_hours=8.0,
                    time_unit_position=-2,
                )
                session.add(schedule)
                session.commit()

                # Test: Time progression with TimeManager integration
                time_manager = TimeManager()
                time_engine = TimeProgressionEngine(session, time_manager)

                # Test: Manual time advancement
                initial_time = time_manager.get_current_time()
                result = time_engine.advance_time(org.id)

                # Verify time was advanced
                current_time = time_manager.get_current_time()
                assert current_time > initial_time

                # Test: Time progression tracking
                assert "time_advancement" in result
                assert result["time_advancement"]["previous_time"] == initial_time
                assert result["time_advancement"]["current_time"] == current_time

                # Test: Multiple time units advancement
                time_engine.advance_time_units(org.id, 3)
                session.refresh(schedule)
                assert schedule.time_unit_position == 2  # -2 + 4 = 2
    finally:
        engine.dispose()
