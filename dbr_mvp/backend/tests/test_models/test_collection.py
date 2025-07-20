# tests/test_models/test_collection.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_collection_creation():
    """Test collection with all attributes"""
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
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
                subscription_level="basic"
            )
            session.add(org)
            session.commit()
            
            # Create test role and user
            role = Role(name=RoleName.PLANNER, description="Test Planner")
            session.add(role)
            session.commit()
            
            user = User(
                username="testuser",
                email="test@example.com",
                display_name="Test User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=role.id
            )
            session.add(user)
            session.commit()
            
            # Test: Project and MOVE types
            for collection_type in [CollectionType.PROJECT, CollectionType.MOVE, CollectionType.EPIC, CollectionType.RELEASE]:
                collection = Collection(
                    organization_id=org.id,
                    name=f"Test {collection_type.value}",
                    description=f"Test {collection_type.value} description",
                    type=collection_type,
                    status=CollectionStatus.ACTIVE,
                    owner_user_id=user.id,
                    target_completion_date=datetime.now(timezone.utc),
                    target_completion_date_timezone="UTC",
                    estimated_sales_price=10000.0,
                    estimated_variable_cost=2000.0,
                    url="https://example.com/project"
                )
                session.add(collection)
                session.commit()
                
                # Test: Collection-WorkItem relationships
                assert collection.id is not None
                assert collection.organization_id == org.id
                assert collection.owner_user_id == user.id
                assert collection.type == collection_type
                assert collection.status == CollectionStatus.ACTIVE
                assert isinstance(uuid.UUID(collection.id), uuid.UUID)
                
                # Test: Financial calculations
                expected_throughput = collection.estimated_sales_price - collection.estimated_variable_cost
                assert collection.calculate_throughput() == expected_throughput
                assert collection.calculate_throughput() == 8000.0
                
                session.delete(collection)
                session.commit()
    finally:
        engine.dispose()


def test_collection_work_items():
    """Test work item management in collections"""
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
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
                subscription_level="basic"
            )
            session.add(org)
            session.commit()
            
            role = Role(name=RoleName.PLANNER, description="Test Planner")
            session.add(role)
            session.commit()
            
            user = User(
                username="testuser",
                email="test@example.com",
                display_name="Test User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=role.id
            )
            session.add(user)
            session.commit()
            
            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=user.id,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Test: Add work items to collections
            work_items = []
            for i in range(3):
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i+1}",
                    description=f"Description for work item {i+1}",
                    status=WorkItemStatus.BACKLOG if i < 2 else WorkItemStatus.DONE,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"dev": 8.0},
                    estimated_sales_price=1000.0,
                    estimated_variable_cost=200.0
                )
                work_items.append(work_item)
                session.add(work_item)
            
            session.commit()
            
            # Test: Get work items for collection
            collection_work_items = collection.get_work_items(session)
            assert len(collection_work_items) == 3
            
            # Test: Remove work items from collections
            collection.remove_work_item(session, work_items[0].id)
            remaining_items = collection.get_work_items(session)
            assert len(remaining_items) == 2
            
            # Test: Collection completion based on work items
            completion_percentage = collection.calculate_completion_percentage(session)
            # 1 out of 2 remaining items is done (50%)
            assert completion_percentage == 0.5
            
            # Test: Collection-level financial calculations
            total_sales = collection.calculate_total_sales_price(session)
            total_costs = collection.calculate_total_variable_cost(session)
            total_throughput = collection.calculate_total_throughput(session)
            
            # 2 remaining items * 1000 each = 2000
            assert total_sales == 2000.0
            # 2 remaining items * 200 each = 400
            assert total_costs == 400.0
            # 2000 - 400 = 1600
            assert total_throughput == 1600.0
    finally:
        engine.dispose()


def test_collection_status_transitions():
    """Test collection status lifecycle"""
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.organization import Organization, OrganizationStatus
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
                subscription_level="basic"
            )
            session.add(org)
            session.commit()
            
            # Test: Collection status lifecycle
            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.PLANNING,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Test: Planning -> Active
            assert collection.status == CollectionStatus.PLANNING
            collection.status = CollectionStatus.ACTIVE
            session.commit()
            assert collection.status == CollectionStatus.ACTIVE
            
            # Test: Active -> On-Hold
            collection.status = CollectionStatus.ON_HOLD
            session.commit()
            assert collection.status == CollectionStatus.ON_HOLD
            
            # Test: On-Hold -> Active -> Completed
            collection.status = CollectionStatus.ACTIVE
            session.commit()
            collection.status = CollectionStatus.COMPLETED
            session.commit()
            assert collection.status == CollectionStatus.COMPLETED
            
            # Test: All valid status values
            valid_statuses = [
                CollectionStatus.PLANNING,
                CollectionStatus.ACTIVE,
                CollectionStatus.ON_HOLD,
                CollectionStatus.COMPLETED
            ]
            
            for status in valid_statuses:
                test_collection = Collection(
                    organization_id=org.id,
                    name=f"Test Collection {status.value}",
                    description="Test collection",
                    type=CollectionType.PROJECT,
                    status=status,
                    owner_user_id=None,
                    estimated_sales_price=5000.0,
                    estimated_variable_cost=1000.0
                )
                session.add(test_collection)
                session.commit()
                
                assert test_collection.status == status
                session.delete(test_collection)
                session.commit()
    finally:
        engine.dispose()


def test_collection_analytics():
    """Test collection analytics and reporting"""
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.organization import Organization, OrganizationStatus
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
                subscription_level="basic"
            )
            session.add(org)
            session.commit()
            
            collection = Collection(
                organization_id=org.id,
                name="Analytics Test Project",
                description="Project for testing analytics",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=20000.0,
                estimated_variable_cost=4000.0
            )
            session.add(collection)
            session.commit()
            
            # Create work items with different statuses
            work_item_data = [
                ("Item 1", WorkItemStatus.DONE, 10.0, 2000.0, 400.0),
                ("Item 2", WorkItemStatus.DONE, 8.0, 1500.0, 300.0),
                ("Item 3", WorkItemStatus.IN_PROGRESS, 12.0, 2500.0, 500.0),
                ("Item 4", WorkItemStatus.READY, 6.0, 1000.0, 200.0),
                ("Item 5", WorkItemStatus.BACKLOG, 14.0, 3000.0, 600.0),
            ]
            
            for title, status, hours, sales, cost in work_item_data:
                work_item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=title,
                    description=f"Description for {title}",
                    status=status,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=hours,
                    ccr_hours_required={"dev": hours},
                    estimated_sales_price=sales,
                    estimated_variable_cost=cost
                )
                session.add(work_item)
            
            session.commit()
            
            # Test: Collection analytics
            analytics = collection.get_analytics(session)
            
            # Test: Work item counts by status
            assert analytics["total_work_items"] == 5
            assert analytics["completed_work_items"] == 2
            assert analytics["in_progress_work_items"] == 1
            assert analytics["ready_work_items"] == 1
            assert analytics["backlog_work_items"] == 1
            
            # Test: Progress calculations
            assert analytics["completion_percentage"] == 0.4  # 2 out of 5 completed
            
            # Test: Financial analytics
            assert analytics["total_estimated_sales"] == 10000.0  # Sum of all work items
            assert analytics["total_estimated_costs"] == 2000.0   # Sum of all work items
            assert analytics["total_estimated_throughput"] == 8000.0  # Sales - Costs
            
            # Test: Effort analytics
            assert analytics["total_estimated_hours"] == 50.0  # Sum of all work items
            assert analytics["completed_hours"] == 18.0  # Sum of completed items (10 + 8)
            assert analytics["remaining_hours"] == 32.0   # Sum of non-completed items
            
            # Test: Collection vs work items comparison
            assert analytics["collection_estimated_sales"] == 20000.0
            assert analytics["collection_estimated_costs"] == 4000.0
            assert analytics["collection_throughput"] == 16000.0
            
            # Test: Variance analysis
            sales_variance = analytics["sales_variance"]  # Collection vs work items
            cost_variance = analytics["cost_variance"]
            
            assert sales_variance == 10000.0  # 20000 - 10000
            assert cost_variance == 2000.0    # 4000 - 2000
    finally:
        engine.dispose()