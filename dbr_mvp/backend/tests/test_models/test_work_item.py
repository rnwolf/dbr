# tests/test_models/test_work_item.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import json


def test_work_item_creation():
    """Test work item with all attributes"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
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
            from dbr.models.collection import CollectionStatus

            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,  # Will be set later when we have users
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0,
            )
            session.add(collection)
            session.commit()

            # Test: Required fields validation
            work_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Test Work Item",
                description="Detailed specification of the work",
                due_date=datetime.now(timezone.utc),
                due_date_timezone="UTC",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=16.0,
                ccr_hours_required={"senior_dev": 8.0, "qa": 4.0, "design": 4.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0,
            )
            session.add(work_item)
            session.commit()

            # Test: CCR hours calculation
            assert work_item.ccr_hours_required is not None
            ccr_hours = work_item.ccr_hours_required
            assert ccr_hours["senior_dev"] == 8.0
            assert ccr_hours["qa"] == 4.0
            assert ccr_hours["design"] == 4.0

            # Test: Throughput calculation (sales_price - variable_cost)
            expected_throughput = (
                work_item.estimated_sales_price - work_item.estimated_variable_cost
            )
            assert work_item.calculate_throughput() == expected_throughput
            assert work_item.calculate_throughput() == 800.0

            # Test: Status transitions
            assert work_item.status == WorkItemStatus.BACKLOG
            work_item.status = WorkItemStatus.READY
            session.commit()
            assert work_item.status == WorkItemStatus.READY

            # Test: All required attributes exist
            assert work_item.id is not None
            assert work_item.organization_id == org.id
            assert work_item.collection_id == collection.id
            assert work_item.title == "Test Work Item"
            assert work_item.description is not None
            assert work_item.due_date is not None
            assert work_item.priority == WorkItemPriority.MEDIUM
            assert work_item.estimated_total_hours == 16.0
    finally:
        engine.dispose()


def test_work_item_tasks():
    """Test task management within work items"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
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
            session.commit()  # Commit org first to get ID

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

            # Create work item with tasks
            initial_tasks = [
                {"id": 1, "title": "Design UI mockups", "completed": False},
                {"id": 2, "title": "Implement backend API", "completed": False},
                {"id": 3, "title": "Write unit tests", "completed": False},
                {"id": 4, "title": "Integration testing", "completed": False},
            ]

            work_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Feature Development",
                description="Complete feature development",
                status=WorkItemStatus.IN_PROGRESS,
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=32.0,
                ccr_hours_required={"senior_dev": 20.0, "qa": 8.0, "design": 4.0},
                estimated_sales_price=2000.0,
                estimated_variable_cost=400.0,
                tasks=initial_tasks,
            )
            session.add(work_item)
            session.commit()

            # Test: Add/remove tasks
            work_item.add_task("Code review", 5)
            assert len(work_item.tasks) == 5
            assert work_item.tasks[4]["title"] == "Code review"
            assert work_item.tasks[4]["id"] == 5

            # Test: Mark tasks complete
            work_item.complete_task(1)
            work_item.complete_task(2)

            completed_tasks = [task for task in work_item.tasks if task["completed"]]
            assert len(completed_tasks) == 2

            # Test: Progress calculation from completed tasks
            progress = work_item.calculate_progress()
            assert progress == 0.4  # 2 out of 5 tasks completed

            # Test: Task validation
            assert work_item.get_task_by_id(1)["completed"] is True
            assert work_item.get_task_by_id(3)["completed"] is False
    finally:
        engine.dispose()


def test_work_item_status_validation():
    """Test work item status transitions and validation"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
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
            session.commit()  # Commit org first to get ID

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

            # Test: All valid status values
            valid_statuses = [
                WorkItemStatus.BACKLOG,
                WorkItemStatus.READY,
                WorkItemStatus.STANDBY,
                WorkItemStatus.IN_PROGRESS,
                WorkItemStatus.DONE,
            ]

            for status in valid_statuses:
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {status.value}",
                    description="Test work item",
                    status=status,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"dev": 8.0},
                    estimated_sales_price=500.0,
                    estimated_variable_cost=100.0,
                )
                session.add(work_item)
                session.commit()

                assert work_item.status == status
                session.delete(work_item)
                session.commit()

            # Test: Priority validation
            valid_priorities = [
                WorkItemPriority.LOW,
                WorkItemPriority.MEDIUM,
                WorkItemPriority.HIGH,
                WorkItemPriority.CRITICAL,
            ]

            for priority in valid_priorities:
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {priority.value}",
                    description="Test work item",
                    status=WorkItemStatus.BACKLOG,
                    priority=priority,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"dev": 8.0},
                    estimated_sales_price=500.0,
                    estimated_variable_cost=100.0,
                )
                session.add(work_item)
                session.commit()

                assert work_item.priority == priority
                session.delete(work_item)
                session.commit()
    finally:
        engine.dispose()


def test_work_item_ccr_hours_json():
    """Test CCR hours JSON field handling"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.user import User  # Import to ensure table is created
    from dbr.models.role import Role  # Import to ensure table is created
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
            session.commit()  # Commit org first to get ID

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

            # Test: Complex CCR hours structure
            ccr_hours = {
                "senior_developer": 12.0,
                "junior_developer": 8.0,
                "qa_engineer": 4.0,
                "ui_designer": 6.0,
                "devops": 2.0,
            }

            work_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Complex Feature",
                description="Feature requiring multiple CCRs",
                status=WorkItemStatus.READY,
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=32.0,
                ccr_hours_required=ccr_hours,
                estimated_sales_price=3000.0,
                estimated_variable_cost=600.0,
            )
            session.add(work_item)
            session.commit()

            # Test: JSON serialization/deserialization
            retrieved_item = session.query(WorkItem).filter_by(id=work_item.id).first()
            assert retrieved_item.ccr_hours_required == ccr_hours

            # Test: Calculate total CCR hours
            total_ccr_hours = retrieved_item.calculate_total_ccr_hours()
            expected_total = sum(ccr_hours.values())
            assert total_ccr_hours == expected_total
            assert total_ccr_hours == 32.0

            # Test: Update CCR hours
            retrieved_item.update_ccr_hours("senior_developer", 16.0)
            assert retrieved_item.ccr_hours_required["senior_developer"] == 16.0

            # Test: Add new CCR
            retrieved_item.add_ccr_hours("product_manager", 4.0)
            assert "product_manager" in retrieved_item.ccr_hours_required
            assert retrieved_item.ccr_hours_required["product_manager"] == 4.0
    finally:
        engine.dispose()
