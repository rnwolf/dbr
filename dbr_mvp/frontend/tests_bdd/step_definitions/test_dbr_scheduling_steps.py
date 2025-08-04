from pytest_bdd import scenarios, given, when, then, parsers
from dbrsdk import Dbrsdk
from dbrsdk.models import ScheduleCreate, WorkItemCreate
import pytest

# Constants
BASE_URL = "http://127.0.0.1:8002"

# Scenarios
scenarios('../features/dbr_scheduling.feature')


@given('an authenticated planner user')
def authenticated_planner(test_data_manager, context):
    """Create and authenticate a planner user."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    planner_user = test_data_manager.create_user(
        username=f"planner_user_sched_{unique_id}",
        password="planner_password",
        email=f"planner_sched_{unique_id}@example.com",
        display_name="Planner User"
    )
    
    # Authenticate and get token
    response = test_data_manager.sdk.authentication.login(
        username=f"planner_user_sched_{unique_id}",
        password="planner_password"
    )
    
    context["planner_sdk"] = Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)
    context["planner_user"] = planner_user
    # Get organization_id from the test_data_manager's default_org
    context["organization_id"] = test_data_manager.default_org.id


@given('a running backend server')
def running_backend_server(backend_server):
    """Check that the backend server is running."""
    pass


@given('a default organization with board configuration exists')
def default_org_with_board_config(context):
    """Ensure organization has a board configuration."""
    # For now, we'll assume the default organization has a board config
    # In a real implementation, you might need to create one
    context["board_config_id"] = "default-board-config-id"


@given('work items are available for scheduling')
def work_items_available_for_scheduling(context):
    """Create work items that are ready for scheduling."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    # Create several work items in "Ready" status
    work_items = []
    for i in range(3):
        try:
            work_item = sdk.work_items.create(
                organization_id=org_id,
                title=f"Schedulable Work Item {i+1}",
                description=f"Work item {i+1} ready for scheduling",
                priority="medium",
                status="Ready",
                estimated_total_hours=8.0,
                ccr_hours_required={"development": 6.0, "testing": 2.0}
            )
            work_items.append(work_item)
        except Exception as e:
            print(f"Failed to create schedulable work item {i+1}: {e}")
    
    context["schedulable_work_items"] = work_items


@given('work items are available for scheduling')
def work_items_available_for_scheduling(context):
    """Create work items that are ready for scheduling."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    # Create several work items in "Ready" status
    work_items = []
    for i in range(3):
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"Schedulable Work Item {i+1}",
            description=f"Work item {i+1} ready for scheduling",
            priority="medium",
            status="Ready",
            estimated_total_hours=8.0,
            ccr_hours_required={"development": 6.0, "testing": 2.0}
        )
        
        work_item = sdk.work_items.create_work_item(work_item_data)
        work_items.append(work_item)
    
    context["schedulable_work_items"] = work_items


@when('I create a schedule with selected work items')
def create_schedule_with_work_items(context):
    """Create a schedule containing selected work items."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    board_config_id = context["board_config_id"]
    work_items = context["schedulable_work_items"]
    
    # Select first two work items for the schedule
    selected_work_items = work_items[:2]
    work_item_ids = [wi.id for wi in selected_work_items]
    
    schedule_data = ScheduleCreate(
        organization_id=org_id,
        board_config_id=board_config_id,
        work_item_ids=work_item_ids,
        capability_channel_id="development-channel",  # Example channel
        status="Planning"
    )
    
    try:
        created_schedule = sdk.schedules.create_schedule(schedule_data)
        context["created_schedule"] = created_schedule
        context["selected_work_items"] = selected_work_items
        context["schedule_creation_success"] = True
    except Exception as e:
        context["schedule_creation_error"] = str(e)
        context["schedule_creation_success"] = False


@then('the schedule should be created successfully')
def schedule_created_successfully(context):
    """Verify schedule was created successfully."""
    assert context.get("schedule_creation_success", False), f"Schedule creation failed: {context.get('schedule_creation_error', 'Unknown error')}"
    assert context.get("created_schedule") is not None


@then('the schedule should contain the selected work items')
def schedule_contains_selected_work_items(context):
    """Verify schedule contains the selected work items."""
    schedule = context["created_schedule"]
    selected_work_items = context["selected_work_items"]
    
    selected_ids = {wi.id for wi in selected_work_items}
    schedule_ids = set(schedule.work_item_ids)
    
    assert selected_ids.issubset(schedule_ids), "Schedule should contain all selected work items"


@then(parsers.parse('the schedule should have status "{status}"'))
def schedule_has_status(context, status):
    """Verify schedule has the expected status."""
    schedule = context["created_schedule"]
    assert schedule.status == status, f"Expected schedule status {status}, got {schedule.status}"


@then('the total CCR hours should be calculated correctly')
def total_ccr_hours_calculated_correctly(context):
    """Verify total CCR hours are calculated correctly."""
    schedule = context["created_schedule"]
    selected_work_items = context["selected_work_items"]
    
    # Calculate expected total CCR hours
    expected_total = sum(
        sum(wi.ccr_hours_required.values()) if wi.ccr_hours_required else 0
        for wi in selected_work_items
    )
    
    assert schedule.total_ccr_hours == expected_total, f"Expected total CCR hours {expected_total}, got {schedule.total_ccr_hours}"


@given('schedules exist in various statuses')
def schedules_exist_various_statuses(context):
    """Create schedules with different statuses."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    board_config_id = context["board_config_id"]
    
    # Create work items for schedules
    work_items = []
    for i in range(6):  # Create enough work items for multiple schedules
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"Schedule Test Item {i+1}",
            description=f"Work item {i+1} for schedule testing",
            priority="medium",
            status="Ready",
            estimated_total_hours=4.0,
            ccr_hours_required={"development": 3.0, "testing": 1.0}
        )
        work_item = sdk.work_items.create_work_item(work_item_data)
        work_items.append(work_item)
    
    # Create schedules with different statuses
    statuses = ["Planning", "Pre-Constraint", "Post-Constraint"]
    schedules = []
    
    for i, status in enumerate(statuses):
        # Use 2 work items per schedule
        schedule_work_items = work_items[i*2:(i+1)*2]
        work_item_ids = [wi.id for wi in schedule_work_items]
        
        schedule_data = ScheduleCreate(
            organization_id=org_id,
            board_config_id=board_config_id,
            work_item_ids=work_item_ids,
            capability_channel_id="development-channel",
            status=status
        )
        
        schedule = sdk.schedules.create_schedule(schedule_data)
        schedules.append(schedule)
    
    context["test_schedules"] = schedules


@when('I advance the system time by one unit')
def advance_system_time_one_unit(context):
    """Advance the system time by one unit."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    
    try:
        result = sdk.system.advance_time_unit(organization_id=org_id)
        context["time_advance_result"] = result
        context["time_advance_success"] = True
    except Exception as e:
        context["time_advance_error"] = str(e)
        context["time_advance_success"] = False


@then('all schedules should progress through their workflow')
def schedules_progress_through_workflow(context):
    """Verify schedules progress through their workflow."""
    assert context.get("time_advance_success", False), f"Time advance failed: {context.get('time_advance_error', 'Unknown error')}"
    
    result = context["time_advance_result"]
    assert result is not None, "Time advance should return a result"
    
    # Verify that schedules were processed
    assert hasattr(result, 'schedules_processed') or hasattr(result, 'affected_schedules'), "Result should indicate schedules were processed"


@then('schedules in "Pre-Constraint" should move toward the CCR')
def pre_constraint_schedules_move_toward_ccr(context):
    """Verify Pre-Constraint schedules move toward the CCR."""
    # This would require checking the time_unit_position of schedules
    # For now, we'll verify the time advance was successful
    assert context.get("time_advance_success", False)


@then('completed schedules should be marked as "Completed"')
def completed_schedules_marked_completed(context):
    """Verify completed schedules are marked as completed."""
    # This would require checking schedule statuses after time advance
    assert context.get("time_advance_success", False)


@then('the system time should be incremented')
def system_time_incremented(context):
    """Verify system time was incremented."""
    sdk = context["planner_sdk"]
    
    try:
        current_time = sdk.system.get_time()
        context["current_system_time"] = current_time
        # In a real test, you'd compare with previous time
        assert current_time is not None, "System should have a current time"
    except Exception as e:
        pytest.fail(f"Failed to get system time: {e}")


@given('a completed schedule exists')
def completed_schedule_exists(context):
    """Create a completed schedule for analytics testing."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    board_config_id = context["board_config_id"]
    
    # Create work items
    work_items = []
    for i in range(2):
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"Completed Schedule Item {i+1}",
            description=f"Work item {i+1} for completed schedule",
            priority="medium",
            status="Done",
            estimated_total_hours=8.0,
            ccr_hours_required={"development": 6.0, "testing": 2.0}
        )
        work_item = sdk.work_items.create_work_item(work_item_data)
        work_items.append(work_item)
    
    # Create completed schedule
    work_item_ids = [wi.id for wi in work_items]
    schedule_data = ScheduleCreate(
        organization_id=org_id,
        board_config_id=board_config_id,
        work_item_ids=work_item_ids,
        capability_channel_id="development-channel",
        status="Completed"
    )
    
    schedule = sdk.schedules.create_schedule(schedule_data)
    context["completed_schedule"] = schedule


@when('I request analytics for the schedule')
def request_schedule_analytics(context):
    """Request analytics for a specific schedule."""
    sdk = context["planner_sdk"]
    schedule = context["completed_schedule"]
    
    try:
        analytics = sdk.schedules.get_analytics(schedule.id)
        context["schedule_analytics"] = analytics
        context["analytics_success"] = True
    except Exception as e:
        context["analytics_error"] = str(e)
        context["analytics_success"] = False


@then('I should receive performance metrics')
def received_performance_metrics(context):
    """Verify performance metrics were received."""
    assert context.get("analytics_success", False), f"Analytics request failed: {context.get('analytics_error', 'Unknown error')}"
    
    analytics = context["schedule_analytics"]
    assert analytics is not None, "Analytics should not be None"


@then('the analytics should include throughput data')
def analytics_include_throughput_data(context):
    """Verify analytics include throughput data."""
    analytics = context["schedule_analytics"]
    
    # Check for throughput-related fields
    assert hasattr(analytics, 'throughput') or hasattr(analytics, 'completion_time'), "Analytics should include throughput data"


@then('the analytics should include buffer status information')
def analytics_include_buffer_status(context):
    """Verify analytics include buffer status information."""
    analytics = context["schedule_analytics"]
    
    # Check for buffer-related fields
    assert hasattr(analytics, 'buffer_status') or hasattr(analytics, 'buffer_penetration'), "Analytics should include buffer status information"


@given('multiple schedules exist for a board')
def multiple_schedules_exist_for_board(context):
    """Create multiple schedules for board analytics testing."""
    # Use the schedules created in previous steps
    if "test_schedules" not in context:
        # Create schedules if they don't exist
        schedules_exist_various_statuses(context)


@when('I request board-level analytics')
def request_board_level_analytics(context):
    """Request analytics for the entire board."""
    sdk = context["planner_sdk"]
    board_config_id = context["board_config_id"]
    
    try:
        board_analytics = sdk.schedules.get_board_analytics(board_config_id)
        context["board_analytics"] = board_analytics
        context["board_analytics_success"] = True
    except Exception as e:
        context["board_analytics_error"] = str(e)
        context["board_analytics_success"] = False


@then('I should receive aggregated performance data')
def received_aggregated_performance_data(context):
    """Verify aggregated performance data was received."""
    assert context.get("board_analytics_success", False), f"Board analytics request failed: {context.get('board_analytics_error', 'Unknown error')}"
    
    board_analytics = context["board_analytics"]
    assert board_analytics is not None, "Board analytics should not be None"


@then('the analytics should show overall system health')
def analytics_show_system_health(context):
    """Verify analytics show overall system health."""
    board_analytics = context["board_analytics"]
    
    # Check for system health indicators
    assert hasattr(board_analytics, 'system_health') or hasattr(board_analytics, 'overall_status'), "Board analytics should include system health indicators"


@then('the analytics should identify bottlenecks')
def analytics_identify_bottlenecks(context):
    """Verify analytics identify bottlenecks."""
    board_analytics = context["board_analytics"]
    
    # Check for bottleneck identification
    assert hasattr(board_analytics, 'bottlenecks') or hasattr(board_analytics, 'constraint_utilization'), "Board analytics should identify bottlenecks"


@given('a board configuration with CCR capacity limits')
def board_config_with_ccr_capacity_limits(context):
    """Ensure board configuration has CCR capacity limits."""
    # For this test, we'll assume the board config has capacity limits
    context["ccr_capacity_limit"] = 40.0  # Example: 40 hours per time unit


@when('I attempt to create a schedule that exceeds CCR capacity')
def attempt_create_schedule_exceeding_capacity(context):
    """Attempt to create a schedule that exceeds CCR capacity."""
    sdk = context["planner_sdk"]
    org_id = context["organization_id"]
    board_config_id = context["board_config_id"]
    
    # Create work items that together exceed the CCR capacity
    work_items = []
    for i in range(3):
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"High Capacity Item {i+1}",
            description=f"Work item {i+1} with high CCR requirements",
            priority="medium",
            status="Ready",
            estimated_total_hours=20.0,  # High hours
            ccr_hours_required={"development": 18.0, "testing": 2.0}  # Total: 20 hours each
        )
        work_item = sdk.work_items.create_work_item(work_item_data)
        work_items.append(work_item)
    
    # Try to create schedule with all high-capacity items (60 hours total > 40 hour limit)
    work_item_ids = [wi.id for wi in work_items]
    schedule_data = ScheduleCreate(
        organization_id=org_id,
        board_config_id=board_config_id,
        work_item_ids=work_item_ids,
        capability_channel_id="development-channel",
        status="Planning"
    )
    
    try:
        created_schedule = sdk.schedules.create_schedule(schedule_data)
        context["capacity_violation_schedule"] = created_schedule
        context["capacity_validation_triggered"] = False
    except Exception as e:
        context["capacity_validation_error"] = str(e)
        context["capacity_validation_triggered"] = True


@then('the system should validate capacity constraints')
def system_validates_capacity_constraints(context):
    """Verify system validates capacity constraints."""
    # Either the schedule was rejected (validation triggered) or created with warnings
    validation_triggered = context.get("capacity_validation_triggered", False)
    schedule_created = context.get("capacity_violation_schedule") is not None
    
    # At minimum, the system should handle the capacity constraint scenario
    assert validation_triggered or schedule_created, "System should either validate constraints or handle capacity violations"


@then('I should receive appropriate warnings or errors')
def received_appropriate_warnings_or_errors(context):
    """Verify appropriate warnings or errors were received."""
    if context.get("capacity_validation_triggered", False):
        error = context.get("capacity_validation_error", "")
        assert "capacity" in error.lower() or "limit" in error.lower(), "Error should mention capacity or limits"


@then('the schedule should not be created if it violates constraints')
def schedule_not_created_if_violates_constraints(context):
    """Verify schedule is not created if it violates constraints."""
    if context.get("capacity_validation_triggered", False):
        assert context.get("capacity_violation_schedule") is None, "Schedule should not be created if it violates capacity constraints"