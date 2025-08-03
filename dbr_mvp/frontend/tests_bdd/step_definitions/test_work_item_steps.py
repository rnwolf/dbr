from pytest_bdd import scenarios, given, when, then, parsers
from dbrsdk import Dbrsdk
from dbrsdk.models import WorkItemCreate, WorkItemUpdate, TaskCreate
import pytest

# Constants
BASE_URL = "http://127.0.0.1:8002"

# Scenarios
scenarios('../features/work_item_management.feature')


@given('a running backend server')
def running_backend_server(backend_server):
    """Check that the backend server is running."""
    pass


@given('an authenticated planner user')
def authenticated_planner(test_data_manager, context):
    """Create and authenticate a planner user."""
    planner_user = test_data_manager.create_user(
        username="planner_user_bdd",
        password="planner_password",
        email="planner@example.com",
        display_name="Planner User"
    )
    
    # Authenticate and get token
    response = test_data_manager.sdk.authentication.login(
        username="planner_user_bdd",
        password="planner_password"
    )
    
    context["planner_sdk"] = Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)
    context["planner_user"] = planner_user
    context["organization_id"] = planner_user.organization_id


@given('a default organization exists')
def default_organization_exists(context):
    """Ensure default organization exists (should be set up by test_data_manager)."""
    assert context.get("organization_id") is not None, "Organization ID should be available"


@when(parsers.parse('I create a work item with title "{title}", description "{description}", priority "{priority}"'))
def create_work_item(context, title, description, priority):
    """Create a work item through the SDK."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    work_item_data = WorkItemCreate(
        organization_id=org_id,
        title=title,
        description=description,
        priority=priority,
        status="Backlog",  # Default status
        estimated_total_hours=8.0,  # Default estimate
        ccr_hours_required={"development": 6.0, "testing": 2.0}  # Example CCR hours
    )
    
    try:
        created_work_item = sdk.work_items.create_work_item(work_item_data)
        context["created_work_item"] = created_work_item
        context["work_item_creation_success"] = True
    except Exception as e:
        context["work_item_creation_error"] = str(e)
        context["work_item_creation_success"] = False


@then('the work item should be created successfully')
def work_item_created_successfully(context):
    """Verify work item was created successfully."""
    assert context.get("work_item_creation_success", False), f"Work item creation failed: {context.get('work_item_creation_error', 'Unknown error')}"
    assert context.get("created_work_item") is not None


@then(parsers.parse('the work item should have status "{status}"'))
def work_item_has_status(context, status):
    """Verify work item has the expected status."""
    work_item = context["created_work_item"]
    assert work_item.status == status, f"Expected status {status}, got {work_item.status}"


@then('the work item should be assigned to my organization')
def work_item_assigned_to_org(context):
    """Verify work item is assigned to the correct organization."""
    work_item = context["created_work_item"]
    org_id = context["organization_id"]
    assert work_item.organization_id == org_id, "Work item should be assigned to the correct organization"


@given('there are work items with various statuses')
def work_items_with_various_statuses(test_data_manager, context):
    """Create work items with different statuses."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    statuses = ["Backlog", "Ready", "In-Progress", "Done"]
    created_items = []
    
    for i, status in enumerate(statuses):
        work_item = sdk.work_items.create(
            organization_id=org_id,
            title=f"Work Item {i+1}",
            description=f"Description for work item {i+1}",
            priority=priority,
            status=status,
            estimated_total_hours=4.0,
            ccr_hours_required={"development": 3.0, "testing": 1.0}
        )
        created_items.append(work_item)
    
    context["test_work_items"] = created_items


@when(parsers.parse('I request work items with status "{status}"'))
def request_work_items_by_status(context, status):
    """Request work items filtered by status."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    try:
        work_items = sdk.work_items.get(
            organization_id=org_id,
            status=[status]
        )
        context["filtered_work_items"] = work_items
        context["filter_success"] = True
    except Exception as e:
        context["filter_error"] = str(e)
        context["filter_success"] = False


@then(parsers.parse('I should receive only work items with "{status}" status'))
def received_filtered_work_items(context, status):
    """Verify only work items with the specified status were returned."""
    assert context.get("filter_success", False), f"Work item filtering failed: {context.get('filter_error', 'Unknown error')}"
    
    work_items = context["filtered_work_items"]
    assert len(work_items) > 0, f"Should have at least one work item with status {status}"
    
    for work_item in work_items:
        assert work_item.status == status, f"All work items should have status {status}, found {work_item.status}"


@then('all work items should belong to my organization')
def work_items_belong_to_org(context):
    """Verify all work items belong to the correct organization."""
    work_items = context["filtered_work_items"]
    org_id = context["organization_id"]
    
    for work_item in work_items:
        assert work_item.organization_id == org_id, f"Work item {work_item.id} does not belong to the correct organization"


@given('a work item exists with status "Ready"')
def work_item_exists_ready_status(context):
    """Create a work item with Ready status."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    work_item = sdk.work_items.create(
        organization_id=org_id,
        title="Ready Work Item",
        description="A work item ready for processing",
        priority="medium",
        status="Ready",
        estimated_total_hours=6.0,
        ccr_hours_required={"development": 4.0, "testing": 2.0}
    )
    context["target_work_item"] = work_item


@when(parsers.parse('I update the work item status to "{new_status}"'))
def update_work_item_status(context, new_status):
    """Update work item status."""
    sdk = context["planner_sdk"]
    work_item = context["target_work_item"]
    
    update_data = WorkItemUpdate(status=new_status)
    
    try:
        updated_work_item = sdk.work_items.update_work_item(work_item.id, update_data)
        context["updated_work_item"] = updated_work_item
        context["status_update_success"] = True
    except Exception as e:
        context["status_update_error"] = str(e)
        context["status_update_success"] = False


@then('the work item status should be updated successfully')
def work_item_status_updated(context):
    """Verify work item status was updated successfully."""
    assert context.get("status_update_success", False), f"Status update failed: {context.get('status_update_error', 'Unknown error')}"
    assert context.get("updated_work_item") is not None


@then(parsers.parse('the work item should appear in "{status}" lists'))
def work_item_appears_in_status_lists(context, status):
    """Verify work item appears in the correct status lists."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    updated_work_item = context["updated_work_item"]
    
    # Get work items with the new status
    work_items = sdk.work_items.get(
        organization_id=org_id,
        status=[status]
    )
    
    work_item_ids = [wi.id for wi in work_items]
    assert updated_work_item.id in work_item_ids, f"Updated work item should appear in {status} lists"


@given('a work item exists')
def work_item_exists(context):
    """Create a basic work item."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    work_item_data = WorkItemCreate(
        organization_id=org_id,
        title="Base Work Item",
        description="A basic work item for testing",
        priority="medium",
        status="Backlog",
        estimated_total_hours=8.0,
        ccr_hours_required={"development": 6.0, "testing": 2.0}
    )
    
    work_item = sdk.work_items.create_work_item(work_item_data)
    context["base_work_item"] = work_item


@when(parsers.parse('I add a task "{task_title}" with estimated hours {hours:d}'))
def add_task_to_work_item(context, task_title, hours):
    """Add a task to a work item."""
    sdk = context["planner_sdk"]
    work_item = context["base_work_item"]
    
    task_data = TaskCreate(
        title=task_title,
        description=f"Task: {task_title}",
        estimated_hours=float(hours),
        status="Not Started"
    )
    
    try:
        # This assumes your API supports adding tasks to work items
        # Adjust based on your actual API structure
        updated_work_item = sdk.work_items.add_task_to_work_item(work_item.id, task_data)
        context["work_item_with_task"] = updated_work_item
        context["task_addition_success"] = True
    except Exception as e:
        context["task_addition_error"] = str(e)
        context["task_addition_success"] = False


@then('the task should be added to the work item')
def task_added_to_work_item(context):
    """Verify task was added to work item."""
    assert context.get("task_addition_success", False), f"Task addition failed: {context.get('task_addition_error', 'Unknown error')}"
    assert context.get("work_item_with_task") is not None


@then('the work item should include the new task in its task list')
def work_item_includes_new_task(context):
    """Verify work item includes the new task."""
    work_item = context["work_item_with_task"]
    assert hasattr(work_item, 'tasks'), "Work item should have a tasks attribute"
    assert len(work_item.tasks) > 0, "Work item should have at least one task"


@given('multiple work items exist with different priorities')
def multiple_work_items_different_priorities(context):
    """Create multiple work items with different priorities."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    priorities = ["low", "medium", "high", "critical"]
    created_items = []
    
    for i, priority in enumerate(priorities):
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"Priority {priority.title()} Item",
            description=f"Work item with {priority} priority",
            priority=priority,
            status="Backlog",
            estimated_total_hours=4.0,
            ccr_hours_required={"development": 3.0, "testing": 1.0}
        )
        
        work_item = sdk.work_items.create_work_item(work_item_data)
        created_items.append(work_item)
    
    context["priority_work_items"] = created_items


@when('I request work items sorted by priority')
def request_work_items_sorted_by_priority(context):
    """Request work items sorted by priority."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    try:
        work_items = sdk.work_items.get(
            organization_id=org_id,
            sort="priority"  # Assuming your API supports priority sorting
        )
        context["sorted_work_items"] = work_items
        context["sort_success"] = True
    except Exception as e:
        context["sort_error"] = str(e)
        context["sort_success"] = False


@then('work items should be returned in priority order')
def work_items_in_priority_order(context):
    """Verify work items are returned in priority order."""
    assert context.get("sort_success", False), f"Work item sorting failed: {context.get('sort_error', 'Unknown error')}"
    
    work_items = context["sorted_work_items"]
    assert len(work_items) > 0, "Should have work items returned"
    
    # Define priority order (highest to lowest)
    priority_order = ["critical", "high", "medium", "low"]
    
    # Check that items are in correct priority order
    for i in range(len(work_items) - 1):
        current_priority_index = priority_order.index(work_items[i].priority)
        next_priority_index = priority_order.index(work_items[i + 1].priority)
        assert current_priority_index <= next_priority_index, "Work items should be sorted by priority (highest first)"


@then('critical priority items should appear first')
def critical_items_appear_first(context):
    """Verify critical priority items appear first."""
    work_items = context["sorted_work_items"]
    
    # Find first critical item
    first_critical_index = None
    for i, work_item in enumerate(work_items):
        if work_item.priority == "critical":
            first_critical_index = i
            break
    
    if first_critical_index is not None:
        # Ensure no higher priority items appear before critical items
        for i in range(first_critical_index):
            assert work_items[i].priority == "critical", "Only critical items should appear before other critical items"


# Additional step definitions for role-based scenarios

@given('a collection exists in the organization')
def collection_exists_in_org(context):
    """Create a collection in the organization."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    try:
        collection = sdk.collections.create(
            organization_id=org_id,
            name="Test Collection",
            description="Collection for work item testing",
            type="Project",
            status="active"
        )
        context["test_collection"] = collection
    except Exception as e:
        print(f"Failed to create test collection: {e}")


@when(parsers.parse('I create a work item with title "{title}", collection assignment, estimated hours {hours:d}'))
def create_work_item_with_collection(context, title, hours):
    """Create a work item with collection assignment."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    collection = context.get("test_collection")
    
    try:
        work_item = sdk.work_items.create(
            organization_id=org_id,
            title=title,
            description="Work item with collection assignment",
            collection_id=collection.id if collection else None,
            priority="medium",
            status="Backlog",
            estimated_total_hours=float(hours)
        )
        context["created_work_item"] = work_item
        context["work_item_creation_success"] = True
    except Exception as e:
        context["work_item_creation_error"] = str(e)
        context["work_item_creation_success"] = False


@then('the work item should be assigned to the collection')
def work_item_assigned_to_collection(context):
    """Verify work item is assigned to the collection."""
    work_item = context["created_work_item"]
    collection = context["test_collection"]
    assert work_item.collection_id == collection.id, "Work item should be assigned to the collection"


@then('the work item should have the correct estimated hours')
def work_item_has_correct_estimated_hours(context):
    """Verify work item has correct estimated hours."""
    work_item = context["created_work_item"]
    assert work_item.estimated_total_hours == 16.0, f"Expected 16.0 hours, got {work_item.estimated_total_hours}"


@when(parsers.parse('I update the work item priority to "{new_priority}"'))
def update_work_item_priority(context, new_priority):
    """Update work item priority."""
    sdk = context.get("org_admin_sdk") or context["planner_sdk"]
    work_item = context["created_work_item"]
    
    try:
        updated_work_item = sdk.work_items.update(
            work_item_id=work_item.id,
            priority=new_priority
        )
        context["updated_work_item"] = updated_work_item
        context["priority_update_success"] = True
    except Exception as e:
        context["priority_update_error"] = str(e)
        context["priority_update_success"] = False


@then('the work item should be updated successfully')
def work_item_updated_successfully(context):
    """Verify work item was updated successfully."""
    assert context.get("priority_update_success", False), f"Work item update failed: {context.get('priority_update_error', 'Unknown error')}"


@when('I delete the work item')
def delete_work_item(context):
    """Delete the work item."""
    sdk = context.get("org_admin_sdk") or context["planner_sdk"]
    work_item = context.get("updated_work_item") or context["created_work_item"]
    
    try:
        result = sdk.work_items.delete(work_item_id=work_item.id)
        context["delete_success"] = True
    except Exception as e:
        context["delete_error"] = str(e)
        context["delete_success"] = False


@then('the work item should be deleted successfully')
def work_item_deleted_successfully(context):
    """Verify work item was deleted successfully."""
    assert context.get("delete_success", False), f"Work item deletion failed: {context.get('delete_error', 'Unknown error')}"


@given('I am authenticated as a worker user')
def authenticated_as_worker_user(test_data_manager, context):
    """Authenticate as a worker user."""
    worker_user = test_data_manager.create_user(
        username="worker_user_workitems",
        password="worker_password",
        email="worker_workitems@example.com",
        display_name="Worker User"
    )
    
    # Authenticate and get token
    response = test_data_manager.sdk.authentication.login(
        username="worker_user_workitems",
        password="worker_password"
    )
    
    context["worker_sdk"] = Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)
    context["worker_user"] = worker_user


@given('work items exist in the organization')
def work_items_exist_in_org(context):
    """Ensure work items exist in the organization."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    # Create test work items if none exist
    try:
        work_item = sdk.work_items.create(
            organization_id=org_id,
            title="Test Work Item for Workers",
            description="Work item for testing worker access",
            priority="medium",
            status="Ready"
        )
        context["existing_work_item"] = work_item
    except Exception as e:
        print(f"Failed to create test work item: {e}")


@given('a work item is assigned to me')
def work_item_assigned_to_me(context):
    """Create a work item assigned to the current user."""
    sdk = context["planner_sdk"]  # Use planner to create, then assign to worker
    org_id = context["organization_id"]
    worker_user = context["worker_user"]
    
    try:
        work_item = sdk.work_items.create(
            organization_id=org_id,
            title="Assigned Work Item",
            description="Work item assigned to worker",
            priority="medium",
            status="In-Progress",
            responsible_user_id=worker_user.id
        )
        context["assigned_work_item"] = work_item
    except Exception as e:
        print(f"Failed to create assigned work item: {e}")


@when('I update my assigned work item status to "In-Progress"')
def update_assigned_work_item_status(context):
    """Update the status of assigned work item."""
    sdk = context["worker_sdk"]
    work_item = context["assigned_work_item"]
    
    try:
        updated_work_item = sdk.work_items.update(
            work_item_id=work_item.id,
            status="In-Progress"
        )
        context["worker_updated_work_item"] = updated_work_item
        context["worker_update_success"] = True
    except Exception as e:
        context["worker_update_error"] = str(e)
        context["worker_update_success"] = False


@when('I try to create a new work item')
def try_create_work_item_as_worker(context):
    """Try to create a work item as a worker (should fail)."""
    sdk = context.get("worker_sdk") or context.get("viewer_sdk")
    org_id = context["organization_id"]
    
    try:
        work_item = sdk.work_items.create(
            organization_id=org_id,
            title="Worker Work Item",
            description="This should fail",
            priority="medium",
            status="Backlog"
        )
        context["unauthorized_work_item_creation_success"] = True
    except Exception as e:
        context["unauthorized_work_item_creation_error"] = str(e)
        context["unauthorized_work_item_creation_success"] = False


@when('I try to delete an existing work item')
def try_delete_work_item_as_worker(context):
    """Try to delete a work item as a worker (should fail)."""
    sdk = context.get("worker_sdk") or context.get("viewer_sdk")
    work_item = context.get("existing_work_item")
    
    if not work_item:
        context["unauthorized_work_item_delete_success"] = False
        context["unauthorized_work_item_delete_error"] = "No work item to delete"
        return
    
    try:
        result = sdk.work_items.delete(work_item_id=work_item.id)
        context["unauthorized_work_item_delete_success"] = True
    except Exception as e:
        context["unauthorized_work_item_delete_error"] = str(e)
        context["unauthorized_work_item_delete_success"] = False


@given('I am authenticated as a viewer user')
def authenticated_as_viewer_user(test_data_manager, context):
    """Authenticate as a viewer user."""
    viewer_user = test_data_manager.create_user(
        username="viewer_user_workitems",
        password="viewer_password",
        email="viewer_workitems@example.com",
        display_name="Viewer User"
    )
    
    # Authenticate and get token
    response = test_data_manager.sdk.authentication.login(
        username="viewer_user_workitems",
        password="viewer_password"
    )
    
    context["viewer_sdk"] = Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)
    context["viewer_user"] = viewer_user


@when('I try to update an existing work item')
def try_update_work_item_as_viewer(context):
    """Try to update a work item as a viewer (should fail)."""
    sdk = context.get("viewer_sdk") or context.get("worker_sdk")
    work_item = context.get("existing_work_item")
    
    if not work_item:
        context["unauthorized_work_item_update_success"] = False
        context["unauthorized_work_item_update_error"] = "No work item to update"
        return
    
    try:
        updated_work_item = sdk.work_items.update(
            work_item_id=work_item.id,
            title="Viewer Updated Title"
        )
        context["unauthorized_work_item_update_success"] = True
    except Exception as e:
        context["unauthorized_work_item_update_error"] = str(e)
        context["unauthorized_work_item_update_success"] = False


@given('there are work items in multiple organizations')
def work_items_in_multiple_orgs(context):
    """Create work items in multiple organizations (simulated)."""
    # For this test, we'll just create work items in our organization
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    # Create work items in our organization
    for i in range(2):
        try:
            work_item = sdk.work_items.create(
                organization_id=org_id,
                title=f"Org Work Item {i+1}",
                description=f"Work item {i+1} in our organization",
                priority="medium",
                status="Backlog"
            )
        except Exception as e:
            print(f"Failed to create work item {i+1}: {e}")


@when('I request work items for my organization')
def request_work_items_for_my_org(context):
    """Request work items for my organization."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    try:
        work_items = sdk.work_items.list(organization_id=org_id)
        context["my_org_work_items"] = work_items
        context["my_org_work_items_success"] = True
    except Exception as e:
        context["my_org_work_items_error"] = str(e)
        context["my_org_work_items_success"] = False


@then('I should only see work items from my organization')
def only_see_my_org_work_items(context):
    """Verify only work items from my organization are returned."""
    assert context.get("my_org_work_items_success", False), f"Work item retrieval failed: {context.get('my_org_work_items_error', 'Unknown error')}"
    
    work_items = context["my_org_work_items"]
    org_id = context["organization_id"]
    
    for work_item in work_items:
        assert work_item.organization_id == org_id, f"Work item {work_item.id} does not belong to my organization"


@then('I should not see work items from other organizations')
def not_see_other_org_work_items(context):
    """Verify no work items from other organizations are returned."""
    # This is implicitly tested by the previous step
    pass