# tests/test_models/test_work_item_dependencies.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_work_item_dependencies():
    """Test dependency relationships"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.work_item_dependency import WorkItemDependency, DependencyType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.user import User
    from dbr.models.role import Role
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
            
            # Create test collection
            collection = Collection(
                organization_id=org.id,
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Test: Add dependencies between work items
            # Create prerequisite work item
            prerequisite_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Database Schema Design",
                description="Design the database schema",
                status=WorkItemStatus.DONE,  # Already completed
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=8.0,
                ccr_hours_required={"architect": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            # Create dependent work item
            dependent_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="API Implementation",
                description="Implement the REST API",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=16.0,
                ccr_hours_required={"developer": 16.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0
            )
            
            session.add_all([prerequisite_item, dependent_item])
            session.commit()
            
            # Create dependency relationship
            dependency = WorkItemDependency(
                dependent_work_item_id=dependent_item.id,
                prerequisite_work_item_id=prerequisite_item.id,
                dependency_type=DependencyType.FINISH_TO_START,
                description="API implementation depends on database schema"
            )
            session.add(dependency)
            session.commit()
            
            # Test: Dependency created successfully
            assert dependency.id is not None
            assert dependency.dependent_work_item_id == dependent_item.id
            assert dependency.prerequisite_work_item_id == prerequisite_item.id
            assert dependency.dependency_type == DependencyType.FINISH_TO_START
            assert isinstance(uuid.UUID(dependency.id), uuid.UUID)
            
            # Test: Can retrieve dependencies
            retrieved_dependency = session.query(WorkItemDependency).filter_by(
                dependent_work_item_id=dependent_item.id
            ).first()
            assert retrieved_dependency is not None
            assert retrieved_dependency.prerequisite_work_item_id == prerequisite_item.id
    finally:
        engine.dispose()


def test_prevent_circular_dependencies():
    """Test circular dependency prevention"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.work_item_dependency import WorkItemDependency, DependencyType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.base import Base
    from dbr.core.dependencies import validate_dependency, CircularDependencyError
    
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
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Create three work items for circular dependency test
            item_a = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Work Item A",
                description="First work item",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            item_b = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Work Item B",
                description="Second work item",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            item_c = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Work Item C",
                description="Third work item",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            session.add_all([item_a, item_b, item_c])
            session.commit()
            
            # Create valid dependencies: A -> B -> C
            dep_a_b = WorkItemDependency(
                dependent_work_item_id=item_b.id,
                prerequisite_work_item_id=item_a.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            dep_b_c = WorkItemDependency(
                dependent_work_item_id=item_c.id,
                prerequisite_work_item_id=item_b.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            session.add_all([dep_a_b, dep_b_c])
            session.commit()
            
            # Test: Prevent circular dependencies
            # Try to create C -> A dependency (would create cycle: A -> B -> C -> A)
            circular_dependency = WorkItemDependency(
                dependent_work_item_id=item_a.id,
                prerequisite_work_item_id=item_c.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            # Test: Validation should detect circular dependency
            with pytest.raises(CircularDependencyError):
                validate_dependency(session, circular_dependency)
            
            # Test: Self-dependency should also be prevented
            self_dependency = WorkItemDependency(
                dependent_work_item_id=item_a.id,
                prerequisite_work_item_id=item_a.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            with pytest.raises(CircularDependencyError):
                validate_dependency(session, self_dependency)
    finally:
        engine.dispose()


def test_dependency_impact_on_ready_status():
    """Test dependency impact on Ready status"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.work_item_dependency import WorkItemDependency, DependencyType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.base import Base
    from dbr.core.dependencies import can_work_item_be_ready, get_work_item_dependencies
    
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
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Create work items with dependencies
            prerequisite1 = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Prerequisite 1",
                description="First prerequisite",
                status=WorkItemStatus.DONE,  # Completed
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            prerequisite2 = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Prerequisite 2",
                description="Second prerequisite",
                status=WorkItemStatus.IN_PROGRESS,  # Not completed yet
                priority=WorkItemPriority.HIGH,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            
            dependent_item = WorkItem(
                organization_id=org.id,
                collection_id=collection.id,
                title="Dependent Item",
                description="Item with dependencies",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=16.0,
                ccr_hours_required={"dev": 16.0},
                estimated_sales_price=1000.0,
                estimated_variable_cost=200.0
            )
            
            session.add_all([prerequisite1, prerequisite2, dependent_item])
            session.commit()
            
            # Create dependencies
            dep1 = WorkItemDependency(
                dependent_work_item_id=dependent_item.id,
                prerequisite_work_item_id=prerequisite1.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            dep2 = WorkItemDependency(
                dependent_work_item_id=dependent_item.id,
                prerequisite_work_item_id=prerequisite2.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            session.add_all([dep1, dep2])
            session.commit()
            
            # Test: Cannot be Ready if dependencies incomplete
            assert not can_work_item_be_ready(session, dependent_item.id)
            
            # Test: Can be Ready after all dependencies complete
            prerequisite2.status = WorkItemStatus.DONE
            session.commit()
            
            assert can_work_item_be_ready(session, dependent_item.id)
            
            # Test: Get work item dependencies
            dependencies = get_work_item_dependencies(session, dependent_item.id)
            assert len(dependencies) == 2
            
            prerequisite_ids = [dep.prerequisite_work_item_id for dep in dependencies]
            assert prerequisite1.id in prerequisite_ids
            assert prerequisite2.id in prerequisite_ids
    finally:
        engine.dispose()


def test_dependency_validation():
    """Test dependency business rules"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.work_item_dependency import WorkItemDependency, DependencyType
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.collection import Collection, CollectionType, CollectionStatus
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.base import Base
    from dbr.core.dependencies import validate_dependency, get_dependency_chain
    
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
                name="Test Project",
                description="Test project description",
                type=CollectionType.PROJECT,
                status=CollectionStatus.ACTIVE,
                owner_user_id=None,
                estimated_sales_price=10000.0,
                estimated_variable_cost=2000.0
            )
            session.add(collection)
            session.commit()
            
            # Create work items for dependency chain testing
            items = []
            for i in range(5):
                item = WorkItem(
                    organization_id=org.id,
                    collection_id=collection.id,
                    title=f"Work Item {i+1}",
                    description=f"Work item number {i+1}",
                    status=WorkItemStatus.BACKLOG,
                    priority=WorkItemPriority.MEDIUM,
                    estimated_total_hours=8.0,
                    ccr_hours_required={"dev": 8.0},
                    estimated_sales_price=500.0,
                    estimated_variable_cost=100.0
                )
                items.append(item)
            
            session.add_all(items)
            session.commit()
            
            # Test: Cannot depend on items from different organizations
            other_org = Organization(
                name="Other Organization",
                description="Different org",
                status=OrganizationStatus.ACTIVE,
                contact_email="other@org.com",
                country="US",
                subscription_level="basic"
            )
            session.add(other_org)
            session.commit()
            
            other_item = WorkItem(
                organization_id=other_org.id,
                collection_id=None,
                title="Other Org Item",
                description="Item from different organization",
                status=WorkItemStatus.BACKLOG,
                priority=WorkItemPriority.MEDIUM,
                estimated_total_hours=8.0,
                ccr_hours_required={"dev": 8.0},
                estimated_sales_price=500.0,
                estimated_variable_cost=100.0
            )
            session.add(other_item)
            session.commit()
            
            # Test: Cross-organization dependency should be invalid
            cross_org_dependency = WorkItemDependency(
                dependent_work_item_id=items[0].id,
                prerequisite_work_item_id=other_item.id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            with pytest.raises(ValueError, match="different organizations"):
                validate_dependency(session, cross_org_dependency)
            
            # Test: Dependency chains work correctly
            # Create chain: item[0] -> item[1] -> item[2]
            dep1 = WorkItemDependency(
                dependent_work_item_id=items[1].id,
                prerequisite_work_item_id=items[0].id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            dep2 = WorkItemDependency(
                dependent_work_item_id=items[2].id,
                prerequisite_work_item_id=items[1].id,
                dependency_type=DependencyType.FINISH_TO_START
            )
            
            session.add_all([dep1, dep2])
            session.commit()
            
            # Test: Get full dependency chain
            chain = get_dependency_chain(session, items[2].id)
            assert len(chain) >= 2  # Should include items[1] and items[0]
            
            # Test: Validate dependency types
            assert dep1.dependency_type == DependencyType.FINISH_TO_START
            assert dep2.dependency_type == DependencyType.FINISH_TO_START
    finally:
        engine.dispose()