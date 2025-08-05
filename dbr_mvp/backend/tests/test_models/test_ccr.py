# tests/test_models/test_ccr.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_ccr_creation():
    """Test CCR with capacity settings"""
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password

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

            # Test: Skill-based, Team-based, Equipment-based types
            ccr_types = [
                (
                    CCRType.SKILL_BASED,
                    "Senior Developers",
                    "Experienced software developers",
                    40.0,
                ),
                (CCRType.TEAM_BASED, "QA Team", "Quality assurance team", 80.0),
                (
                    CCRType.EQUIPMENT_BASED,
                    "Build Servers",
                    "CI/CD build infrastructure",
                    168.0,
                ),
            ]

            for ccr_type, name, description, capacity in ccr_types:
                ccr = CCR(
                    organization_id=org.id,
                    name=name,
                    description=description,
                    ccr_type=ccr_type,
                    capacity_per_time_unit=capacity,
                    time_unit="week",
                    is_active=True,
                )
                session.add(ccr)
                session.commit()

                # Test: Capacity per time unit calculations
                assert ccr.id is not None
                assert ccr.organization_id == org.id
                assert ccr.name == name
                assert ccr.ccr_type == ccr_type
                assert ccr.capacity_per_time_unit == capacity
                assert ccr.time_unit == "week"
                assert ccr.is_active is True
                assert isinstance(uuid.UUID(ccr.id), uuid.UUID)

                # Test: Capacity calculations
                daily_capacity = ccr.get_daily_capacity()
                weekly_capacity = ccr.get_weekly_capacity()
                monthly_capacity = ccr.get_monthly_capacity()

                if ccr.time_unit == "week":
                    assert weekly_capacity == capacity
                    assert daily_capacity == capacity / 7
                    assert (
                        monthly_capacity == capacity * 4.33
                    )  # Approximate weeks per month

                session.delete(ccr)
                session.commit()
    finally:
        engine.dispose()


def test_ccr_capacity_validation():
    """Test capacity constraint validation"""
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
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

            # Test: Schedule cannot exceed CCR capacity
            ccr = CCR(
                organization_id=org.id,
                name="Senior Developers",
                description="Senior development team",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=40.0,  # 40 hours per week
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            # Create work items that require CCR hours
            work_items = []
            for i in range(3):
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i + 1}",
                    description=f"Work item requiring senior dev time",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=20.0,
                    ccr_hours_required={"senior_developers": 15.0},  # 15 hours each
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                work_items.append(work_item)
                session.add(work_item)

            session.commit()

            # Test: Multiple CCRs can exist
            qa_ccr = CCR(
                organization_id=org.id,
                name="QA Engineers",
                description="Quality assurance engineers",
                ccr_type=CCRType.SKILL_BASED,
                capacity_per_time_unit=30.0,
                time_unit="week",
                is_active=True,
            )
            session.add(qa_ccr)
            session.commit()

            # Test: CCR utilization tracking
            total_demand = ccr.calculate_total_demand(session, work_items)
            utilization = ccr.calculate_utilization(session, work_items)

            # 3 items * 15 hours each = 45 hours demand vs 40 hours capacity
            assert total_demand == 45.0
            assert utilization > 1.0  # Over capacity

            # Test: Available capacity calculation
            available_capacity = ccr.get_available_capacity(session, work_items)
            assert available_capacity == -5.0  # 40 - 45 = -5 (over capacity)

            # Test: Can schedule validation
            assert not ccr.can_schedule_work_items(session, work_items)

            # Test: Remove one work item and check again
            work_items_subset = work_items[:2]  # Only 2 items = 30 hours
            assert ccr.can_schedule_work_items(session, work_items_subset)
    finally:
        engine.dispose()


def test_ccr_user_associations():
    """Test CCR-User associations"""
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.ccr_user_association import CCRUserAssociation
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password

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

            role = Role(name=RoleName.WORKER, description="Test Worker")
            session.add(role)
            session.commit()

            # Create test users
            users = []
            for i in range(3):
                user = User(
                    username=f"developer{i + 1}",
                    email=f"dev{i + 1}@example.com",
                    display_name=f"Developer {i + 1}",
                    password_hash=hash_password("password123"),
                    active_status=True,
                    system_role_id=role.id,
                )
                users.append(user)
                session.add(user)

            session.commit()

            # Create CCR
            ccr = CCR(
                organization_id=org.id,
                name="Development Team",
                description="Software development team",
                ccr_type=CCRType.TEAM_BASED,
                capacity_per_time_unit=120.0,  # 3 developers * 40 hours each
                time_unit="week",
                is_active=True,
            )
            session.add(ccr)
            session.commit()

            # Test: Associated users management
            for user in users:
                association = CCRUserAssociation(
                    ccr_id=ccr.id,
                    user_id=user.id,
                    capacity_contribution=40.0,  # Each developer contributes 40 hours/week
                    skill_level="senior",
                    is_active=True,
                )
                session.add(association)

            session.commit()

            # Test: Get associated users
            associated_users = ccr.get_associated_users(session)
            assert len(associated_users) == 3

            # Test: Calculate total capacity from users
            total_user_capacity = ccr.calculate_capacity_from_users(session)
            assert total_user_capacity == 120.0  # 3 users * 40 hours each

            # Test: Get users by skill level
            senior_users = ccr.get_users_by_skill_level(session, "senior")
            assert len(senior_users) == 3

            # Test: CCR capacity validation against user capacity
            assert ccr.validate_capacity_against_users(session)

            # Test: Update CCR capacity to mismatch user capacity
            ccr.capacity_per_time_unit = 100.0  # Less than user total
            session.commit()
            assert not ccr.validate_capacity_against_users(session)
    finally:
        engine.dispose()


def test_ccr_analytics():
    """Test CCR analytics and utilization reporting"""
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
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

            # Create multiple CCRs
            ccrs = [
                ("Senior Developers", CCRType.SKILL_BASED, 40.0),
                ("QA Engineers", CCRType.SKILL_BASED, 30.0),
                ("DevOps Team", CCRType.TEAM_BASED, 20.0),
            ]

            ccr_objects = []
            for name, ccr_type, capacity in ccrs:
                ccr = CCR(
                    organization_id=org.id,
                    name=name,
                    description=f"{name} resource",
                    ccr_type=ccr_type,
                    capacity_per_time_unit=capacity,
                    time_unit="week",
                    is_active=True,
                )
                ccr_objects.append(ccr)
                session.add(ccr)

            session.commit()

            # Create work items with different CCR requirements
            work_item_data = [
                ("Feature A", {"senior_developers": 20.0, "qa_engineers": 10.0}),
                (
                    "Feature B",
                    {
                        "senior_developers": 15.0,
                        "qa_engineers": 8.0,
                        "devops_team": 5.0,
                    },
                ),
                ("Feature C", {"senior_developers": 10.0, "devops_team": 12.0}),
            ]

            work_items = []
            for title, ccr_hours in work_item_data:
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=title,
                    description=f"Description for {title}",
                    status=WorkItemStatus.READY,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=sum(ccr_hours.values()),
                    ccr_hours_required=ccr_hours,
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0,
                )
                work_items.append(work_item)
                session.add(work_item)

            session.commit()

            # Test: CCR analytics
            senior_dev_ccr = ccr_objects[0]  # Senior Developers
            analytics = senior_dev_ccr.get_analytics(session)

            # Test: Demand calculation
            # Feature A: 20, Feature B: 15, Feature C: 10 = 45 total
            assert analytics["total_demand"] == 45.0
            assert analytics["capacity"] == 40.0
            assert analytics["utilization"] == 1.125  # 45/40 = 112.5%
            assert analytics["available_capacity"] == -5.0  # 40 - 45
            assert analytics["is_over_capacity"] is True

            # Test: Work item breakdown
            assert analytics["work_items_count"] == 3
            assert analytics["work_items_requiring_ccr"] == 3

            # Test: Get organization-wide CCR utilization
            org_analytics = CCR.get_organization_ccr_analytics(session, org.id)

            assert len(org_analytics["ccr_utilization"]) == 3
            assert "senior_developers" in org_analytics["ccr_utilization"]
            assert "qa_engineers" in org_analytics["ccr_utilization"]
            assert "devops_team" in org_analytics["ccr_utilization"]

            # Test: Bottleneck identification
            bottlenecks = CCR.identify_bottlenecks(session, org.id)
            assert len(bottlenecks) >= 1  # Senior Developers should be a bottleneck

            bottleneck_names = [ccr.name for ccr in bottlenecks]
            assert "Senior Developers" in bottleneck_names
    finally:
        engine.dispose()
