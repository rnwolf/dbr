# tests/test_api/test_work_items.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
from dbr.models.collection import Collection, CollectionType, CollectionStatus
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
        description="Test org for work item API testing",
        status=OrganizationStatus.ACTIVE,
        contact_email="test@example.com",
        country="US"
    )
    session.add(org)
    session.commit()
    return org


@pytest.fixture
def test_collection(session, test_organization):
    """Create a test collection"""
    collection = Collection(
        organization_id=test_organization.id,
        name="Test Collection",
        description="Test collection for work items",
        type=CollectionType.PROJECT,
        status=CollectionStatus.ACTIVE,
        estimated_sales_price=10000.0,
        estimated_variable_cost=3000.0
    )
    session.add(collection)
    session.commit()
    return collection


@pytest.fixture
def test_work_items(session, test_organization, test_collection):
    """Create test work items"""
    work_items = []
    
    # Work item 1: In collection
    work_item1 = WorkItem(
        organization_id=test_organization.id,
        collection_id=test_collection.id,
        title="Test Work Item 1",
        description="First test work item",
        status=WorkItemStatus.BACKLOG,
        priority=WorkItemPriority.HIGH,
        estimated_total_hours=16.0,
        ccr_hours_required={"development": 12.0, "testing": 4.0},
        estimated_sales_price=5000.0,
        estimated_variable_cost=1500.0
    )
    
    # Work item 2: Standalone (no collection)
    work_item2 = WorkItem(
        organization_id=test_organization.id,
        collection_id=None,
        title="Test Work Item 2",
        description="Second test work item",
        status=WorkItemStatus.READY,
        priority=WorkItemPriority.MEDIUM,
        estimated_total_hours=8.0,
        ccr_hours_required={"development": 6.0, "testing": 2.0},
        estimated_sales_price=2500.0,
        estimated_variable_cost=750.0
    )
    
    # Work item 3: Different status
    work_item3 = WorkItem(
        organization_id=test_organization.id,
        collection_id=test_collection.id,
        title="Test Work Item 3",
        description="Third test work item",
        status=WorkItemStatus.IN_PROGRESS,
        priority=WorkItemPriority.LOW,
        estimated_total_hours=12.0,
        ccr_hours_required={"development": 8.0, "testing": 4.0},
        estimated_sales_price=3000.0,
        estimated_variable_cost=900.0
    )
    
    work_items.extend([work_item1, work_item2, work_item3])
    session.add_all(work_items)
    session.commit()
    return work_items


def test_create_work_item_api(client, session, test_organization, test_collection):
    """Test work item creation via API"""
    # Test: POST /workitems creates work item
    # Test: Required fields validation
    # Test: Returns created work item with ID
    
    work_item_data = {
        "organization_id": test_organization.id,
        "collection_id": test_collection.id,
        "title": "New Work Item",
        "description": "A new work item created via API",
        "status": "Backlog",
        "priority": "high",
        "estimated_total_hours": 20.0,
        "ccr_hours_required": {
            "development": 15.0,
            "testing": 5.0
        },
        "estimated_sales_price": 8000.0,
        "estimated_variable_cost": 2400.0
    }
    
    response = client.post("/api/v1/workitems", json=work_item_data)
    
    assert response.status_code == 201
    created_item = response.json()
    
    # Verify response structure
    assert "id" in created_item
    assert created_item["title"] == "New Work Item"
    assert created_item["organization_id"] == test_organization.id
    assert created_item["collection_id"] == test_collection.id
    assert created_item["status"] == "Backlog"
    assert created_item["priority"] == "high"
    assert created_item["estimated_total_hours"] == 20.0
    assert created_item["ccr_hours_required"]["development"] == 15.0
    assert created_item["estimated_sales_price"] == 8000.0
    assert "created_date" in created_item
    assert "throughput" in created_item
    
    # Verify throughput calculation
    expected_throughput = 8000.0 - 2400.0  # sales_price - variable_cost
    assert created_item["throughput"] == expected_throughput


def test_create_work_item_validation(client, session, test_organization):
    """Test work item creation validation"""
    
    # Test missing required fields
    incomplete_data = {
        "organization_id": test_organization.id,
        "title": "Incomplete Item"
        # Missing estimated_total_hours
    }
    
    response = client.post("/api/v1/workitems", json=incomplete_data)
    assert response.status_code == 422  # Validation error
    
    # Test invalid status
    invalid_status_data = {
        "organization_id": test_organization.id,
        "title": "Invalid Status Item",
        "estimated_total_hours": 8.0,
        "status": "InvalidStatus"
    }
    
    response = client.post("/api/v1/workitems", json=invalid_status_data)
    assert response.status_code == 422
    
    # Test invalid priority
    invalid_priority_data = {
        "organization_id": test_organization.id,
        "title": "Invalid Priority Item",
        "estimated_total_hours": 8.0,
        "priority": "invalid_priority"
    }
    
    response = client.post("/api/v1/workitems", json=invalid_priority_data)
    assert response.status_code == 422


def test_work_item_crud_api(client, session, test_organization, test_work_items):
    """Test complete work item CRUD"""
    # Test: GET /workitems (list with filters)
    # Test: GET /workitems/{id} (single item)
    # Test: PUT /workitems/{id} (update)
    # Test: DELETE /workitems/{id} (delete)
    
    # Test GET /workitems (list all)
    response = client.get(f"/api/v1/workitems?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    work_items = response.json()
    assert len(work_items) == 3
    assert all("id" in item for item in work_items)
    assert all("title" in item for item in work_items)
    
    # Test GET /workitems with status filter
    response = client.get(f"/api/v1/workitems?organization_id={test_organization.id}&status=Ready")
    assert response.status_code == 200
    
    ready_items = response.json()
    assert len(ready_items) == 1
    assert ready_items[0]["status"] == "Ready"
    
    # Test GET /workitems with collection filter
    collection_id = test_work_items[0].collection_id
    response = client.get(f"/api/v1/workitems?organization_id={test_organization.id}&collection_id={collection_id}")
    assert response.status_code == 200
    
    collection_items = response.json()
    assert len(collection_items) == 2  # Items 1 and 3 are in collection
    
    # Test GET /workitems/{id} (single item)
    work_item_id = test_work_items[0].id
    response = client.get(f"/api/v1/workitems/{work_item_id}?organization_id={test_organization.id}")
    assert response.status_code == 200
    
    single_item = response.json()
    assert single_item["id"] == work_item_id
    assert single_item["title"] == "Test Work Item 1"
    assert "tasks" in single_item
    assert "progress_percentage" in single_item
    
    # Test PUT /workitems/{id} (update)
    update_data = {
        "title": "Updated Work Item 1",
        "status": "In-Progress",
        "priority": "critical",
        "estimated_total_hours": 18.0
    }
    
    response = client.put(
        f"/api/v1/workitems/{work_item_id}?organization_id={test_organization.id}",
        json=update_data
    )
    assert response.status_code == 200
    
    updated_item = response.json()
    assert updated_item["title"] == "Updated Work Item 1"
    assert updated_item["status"] == "In-Progress"
    assert updated_item["priority"] == "critical"
    assert updated_item["estimated_total_hours"] == 18.0
    
    # Test DELETE /workitems/{id}
    work_item_to_delete = test_work_items[1].id  # Standalone item
    response = client.delete(f"/api/v1/workitems/{work_item_to_delete}?organization_id={test_organization.id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/api/v1/workitems/{work_item_to_delete}?organization_id={test_organization.id}")
    assert response.status_code == 404


def test_work_item_tasks_api(client, session, test_organization, test_work_items):
    """Test work item task management via API"""
    
    work_item_id = test_work_items[0].id
    
    # Add tasks to work item
    update_data = {
        "tasks": [
            {"title": "Task 1", "completed": False},
            {"title": "Task 2", "completed": True},
            {"title": "Task 3", "completed": False}
        ]
    }
    
    response = client.put(
        f"/api/v1/workitems/{work_item_id}?organization_id={test_organization.id}",
        json=update_data
    )
    assert response.status_code == 200
    
    updated_item = response.json()
    assert len(updated_item["tasks"]) == 3
    assert updated_item["progress_percentage"] == 33.33  # 1 out of 3 completed
    
    # Test task update via specific endpoint
    task_id = updated_item["tasks"][0]["id"]
    task_update = {
        "title": "Updated Task 1",
        "completed": True
    }
    
    response = client.put(
        f"/api/v1/workitems/{work_item_id}/tasks/{task_id}?organization_id={test_organization.id}",
        json=task_update
    )
    assert response.status_code == 200
    
    updated_work_item = response.json()
    assert updated_work_item["progress_percentage"] == 66.67  # 2 out of 3 completed
    
    # Find the updated task
    updated_task = next(task for task in updated_work_item["tasks"] if task["id"] == task_id)
    assert updated_task["title"] == "Updated Task 1"
    assert updated_task["completed"] == True


def test_work_item_error_handling(client, session, test_organization):
    """Test error handling for work item API"""
    
    # Test 404 for non-existent work item
    response = client.get(f"/api/v1/workitems/non-existent-id?organization_id={test_organization.id}")
    assert response.status_code == 404
    
    # Test 403 for wrong organization
    fake_org_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/workitems?organization_id={fake_org_id}")
    assert response.status_code == 403
    
    # Test 400 for missing organization_id
    response = client.get("/api/v1/workitems")
    assert response.status_code == 422  # Missing required query parameter


def test_work_item_filtering_and_sorting(client, session, test_organization, test_work_items):
    """Test advanced filtering and sorting for work items"""
    
    # Test multiple status filter
    response = client.get(
        f"/api/v1/workitems?organization_id={test_organization.id}&status=Backlog&status=Ready"
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    
    # Test priority filter
    response = client.get(
        f"/api/v1/workitems?organization_id={test_organization.id}&priority=high"
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["priority"] == "high"
    
    # Test sorting (if implemented)
    response = client.get(
        f"/api/v1/workitems?organization_id={test_organization.id}&sort=title"
    )
    assert response.status_code == 200
    items = response.json()
    titles = [item["title"] for item in items]
    assert titles == sorted(titles)  # Should be sorted alphabetically