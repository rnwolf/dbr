# CustomTkinter Testing Patterns Reference

## Quick Reference for Common Testing Patterns

This document provides quick-reference patterns for common testing scenarios in the DBR CustomTkinter application.

## Table of Contents

1. [Basic Component Testing](#basic-component-testing)
2. [Authentication Testing](#authentication-testing)
3. [Role-Based Testing](#role-based-testing)
4. [Event Testing](#event-testing)
5. [Service Integration Testing](#service-integration-testing)
6. [Error Handling Testing](#error-handling-testing)
7. [Mock Setup Patterns](#mock-setup-patterns)

## Basic Component Testing

### Simple Widget Test
```python
@patch("customtkinter.CTkButton")
@patch("customtkinter.CTkFrame.__init__", return_value=None)
def test_simple_widget(mock_frame_init, mock_button):
    """Test a simple widget component."""
    parent = Mock()
    parent._last_child_ids = {}
    parent.tk = Mock()
    parent.children = {}
    
    widget = SimpleWidget(parent)
    
    assert widget is not None
    mock_button.assert_called()
```

### Complex Component Test
```python
@pytest.fixture
def mocked_complex_component():
    """Fixture for complex component with multiple dependencies."""
    with patch('frontend.component.ctk.CTk') as mock_ctk:
        with patch('frontend.component.SubComponent') as mock_sub:
            with patch('frontend.component.ctk.CTkFrame') as mock_frame:
                mock_ctk_instance = Mock()
                mock_ctk.return_value = mock_ctk_instance
                
                from frontend.component import ComplexComponent
                component = ComplexComponent()
                
                return component, {
                    "ctk_instance": mock_ctk_instance,
                    "sub_component": mock_sub.return_value,
                    "frame": mock_frame.return_value
                }

def test_complex_component(mocked_complex_component):
    """Test complex component initialization."""
    component, mocks = mocked_complex_component
    
    assert component is not None
    assert hasattr(component, 'sub_component')
```

## Authentication Testing

### Login Success Pattern
```python
@patch('frontend.authentication_ui.DBRService')
def test_login_success(mock_dbr_service):
    """Test successful login flow."""
    # Setup
    mock_service_instance = mock_dbr_service.return_value
    mock_service_instance.login.return_value = True
    mock_service_instance.get_user_info.return_value = {
        "username": "testuser",
        "role": "Planner"
    }
    
    # Test
    from frontend.authentication_ui import LoginDialog
    dialog = LoginDialog(None, "http://localhost:8000")
    result = dialog._attempt_login("testuser", "password")
    
    # Assert
    assert result is True
    mock_service_instance.login.assert_called_once_with("testuser", "password")
```

### Login Failure Pattern
```python
@patch('frontend.authentication_ui.DBRService')
def test_login_failure(mock_dbr_service):
    """Test login failure handling."""
    # Setup
    mock_service_instance = mock_dbr_service.return_value
    mock_service_instance.login.return_value = False
    
    # Test
    from frontend.authentication_ui import LoginDialog
    dialog = LoginDialog(None, "http://localhost:8000")
    result = dialog._attempt_login("invalid", "invalid")
    
    # Assert
    assert result is False
```

### User Context Pattern
```python
def test_user_context_display(mock_dbr_service):
    """Test user context widget display."""
    # Setup
    mock_dbr_service.get_user_info.return_value = {
        "username": "testuser",
        "display_name": "Test User"
    }
    mock_dbr_service.get_current_organization.return_value = {
        "name": "Test Org"
    }
    
    # Test
    with patch('frontend.authentication_ui.ctk.CTkFrame'):
        from frontend.authentication_ui import UserContextWidget
        widget = UserContextWidget(None, mock_dbr_service)
        
        # Assert
        assert widget.user_info["username"] == "testuser"
        assert widget.organization_info["name"] == "Test Org"
```

## Role-Based Testing

### Role Navigation Pattern
```python
@pytest.mark.parametrize("role,expected_tabs", [
    ("Super Admin", ["Organizations", "Users", "System", "Setup", "Work Items", "Collections", "Planning", "Buffer Boards", "Reports"]),
    ("Org Admin", ["Setup", "Work Items", "Collections", "Planning", "Buffer Boards", "Reports"]),
    ("Planner", ["Work Items", "Collections", "Planning", "Buffer Boards", "Reports"]),
    ("Worker", ["Work Items", "Buffer Boards", "Reports"]),
    ("Viewer", ["Buffer Boards", "Reports"])
])
def test_role_based_navigation(role, expected_tabs, mock_dbr_service):
    """Test navigation tabs for different roles."""
    # Setup
    mock_dbr_service.get_user_role.return_value = role
    mock_dbr_service.has_permission.return_value = True
    
    # Test
    with comprehensive_mocking():
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        # Assert
        for tab in expected_tabs:
            assert tab in window.available_tabs
```

### Permission Checking Pattern
```python
def test_permission_checking(mock_dbr_service):
    """Test permission-based access control."""
    # Setup permission responses
    def permission_side_effect(permission):
        allowed_permissions = ["view_work_items", "edit_work_items"]
        return permission in allowed_permissions
    
    mock_dbr_service.has_permission.side_effect = permission_side_effect
    
    # Test
    with comprehensive_mocking():
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        # Assert
        assert window._check_tab_permission("Work Items") is True
        assert window._check_tab_permission("Organizations") is False
```

## Event Testing

### Event Publishing Pattern
```python
def test_event_publishing(mocked_widget):
    """Test widget publishes events correctly."""
    widget, mocks = mocked_widget
    
    # Setup event bus mock
    event_bus = Mock()
    widget.event_bus = event_bus
    
    # Test
    widget._trigger_event("test_data")
    
    # Assert
    event_bus.publish.assert_called_once_with(
        "widget_event",
        data={"value": "test_data"}
    )
```

### Event Subscription Pattern
```python
def test_event_subscription():
    """Test event subscription and handling."""
    from frontend.utils.event_bus import EventBus
    
    event_bus = EventBus()
    callback = Mock()
    
    # Test
    event_bus.subscribe("test_event", callback)
    event_bus.publish("test_event", data={"key": "value"})
    
    # Assert
    callback.assert_called_once_with(data={"key": "value"})
```

### Component Communication Pattern
```python
def test_component_communication(mocked_main_window):
    """Test communication between components."""
    window, mocks = mocked_main_window
    
    # Setup
    window.component_a = Mock()
    window.component_b = Mock()
    
    # Test
    window.component_a.send_message("test_message")
    
    # Assert
    window.component_b.receive_message.assert_called_with("test_message")
```

## Service Integration Testing

### Service Mock Pattern
```python
@pytest.fixture
def mock_dbr_service():
    """Standard DBR service mock."""
    service = Mock()
    service.get_user_info.return_value = {"username": "testuser", "role": "Planner"}
    service.get_user_role.return_value = "Planner"
    service.get_current_organization.return_value = {"name": "Test Org"}
    service.is_authenticated.return_value = True
    service.has_permission.return_value = True
    service.get_connection_status.return_value = {
        "backend_url": "http://localhost:8000",
        "backend_healthy": True
    }
    return service
```

### API Call Testing Pattern
```python
def test_api_call_handling(mock_dbr_service):
    """Test handling of API calls."""
    # Setup
    mock_dbr_service.get_work_items.return_value = [
        {"id": "1", "title": "Test Item 1"},
        {"id": "2", "title": "Test Item 2"}
    ]
    
    # Test
    with comprehensive_mocking():
        from frontend.pages.work_items import WorkItemsPage
        page = WorkItemsPage(None, mock_dbr_service)
        page.load_work_items()
        
        # Assert
        assert len(page.work_items) == 2
        mock_dbr_service.get_work_items.assert_called_once()
```

### Error Handling Pattern
```python
def test_api_error_handling(mock_dbr_service):
    """Test API error handling."""
    # Setup
    mock_dbr_service.get_work_items.side_effect = Exception("API Error")
    
    # Test
    with comprehensive_mocking():
        from frontend.pages.work_items import WorkItemsPage
        page = WorkItemsPage(None, mock_dbr_service)
        page.load_work_items()
        
        # Assert
        assert page.error_message == "Failed to load work items"
        assert page.work_items == []
```

## Error Handling Testing

### Exception Handling Pattern
```python
def test_exception_handling(mocked_component):
    """Test component handles exceptions gracefully."""
    component, mocks = mocked_component
    
    # Setup
    component.risky_operation = Mock(side_effect=Exception("Test error"))
    
    # Test
    result = component.safe_operation()
    
    # Assert
    assert result is False
    assert component.error_state is True
```

### Validation Error Pattern
```python
def test_validation_error_handling(mocked_form):
    """Test form validation error handling."""
    form, mocks = mocked_form
    
    # Test invalid data
    invalid_data = {"field": ""}
    result = form.validate(invalid_data)
    
    # Assert
    assert result is False
    assert "field" in form.validation_errors
```

### Network Error Pattern
```python
def test_network_error_handling(mock_dbr_service):
    """Test network error handling."""
    # Setup
    mock_dbr_service.get_data.side_effect = ConnectionError("Network error")
    
    # Test
    with comprehensive_mocking():
        from frontend.components.data_loader import DataLoader
        loader = DataLoader(mock_dbr_service)
        result = loader.load_data()
        
        # Assert
        assert result is None
        assert loader.connection_error is True
```

## Mock Setup Patterns

### Comprehensive GUI Mocking
```python
def comprehensive_mocking():
    """Context manager for comprehensive GUI mocking."""
    return patch.multiple(
        'customtkinter',
        CTk=Mock(),
        CTkFrame=Mock(),
        CTkLabel=Mock(),
        CTkButton=Mock(),
        CTkEntry=Mock(),
        CTkComboBox=Mock(),
        CTkTextbox=Mock(),
        CTkScrollableFrame=Mock(),
    )
```

### Parent Widget Mock
```python
def create_mock_parent():
    """Create a properly configured mock parent widget."""
    parent = Mock()
    parent._last_child_ids = {}
    parent.tk = Mock()
    parent.children = {}
    parent.winfo_exists.return_value = True
    return parent
```

### Service Mock with Realistic Data
```python
def create_realistic_service_mock():
    """Create a service mock with realistic test data."""
    service = Mock()
    
    # User data
    service.get_user_info.return_value = {
        "id": "user-123",
        "username": "testuser",
        "display_name": "Test User",
        "email": "test@example.com"
    }
    
    # Organization data
    service.get_current_organization.return_value = {
        "id": "org-456",
        "name": "Test Organization",
        "status": "active"
    }
    
    # Work items data
    service.get_work_items.return_value = [
        {
            "id": "wi-001",
            "title": "Test Work Item 1",
            "status": "active",
            "ccr_hours": 8.0
        },
        {
            "id": "wi-002", 
            "title": "Test Work Item 2",
            "status": "completed",
            "ccr_hours": 4.0
        }
    ]
    
    return service
```

### Event Bus Mock
```python
def create_mock_event_bus():
    """Create a mock event bus for testing."""
    event_bus = Mock()
    event_bus.subscribers = {}
    
    def mock_subscribe(event_type, callback):
        if event_type not in event_bus.subscribers:
            event_bus.subscribers[event_type] = []
        event_bus.subscribers[event_type].append(callback)
    
    def mock_publish(event_type, **kwargs):
        if event_type in event_bus.subscribers:
            for callback in event_bus.subscribers[event_type]:
                callback(**kwargs)
    
    event_bus.subscribe.side_effect = mock_subscribe
    event_bus.publish.side_effect = mock_publish
    
    return event_bus
```

## Test Data Factories

### User Data Factory
```python
def create_test_user(role="Planner", username=None):
    """Create test user data for different roles."""
    if username is None:
        username = f"test_{role.lower().replace(' ', '_')}"
    
    return {
        "id": f"user-{username}",
        "username": username,
        "display_name": f"Test {role}",
        "email": f"{username}@test.com",
        "role": role,
        "organization_id": "org-test"
    }
```

### Work Item Data Factory
```python
def create_test_work_item(title=None, status="active"):
    """Create test work item data."""
    if title is None:
        title = f"Test Work Item {random.randint(1, 1000)}"
    
    return {
        "id": f"wi-{uuid.uuid4().hex[:8]}",
        "title": title,
        "status": status,
        "ccr_hours": random.uniform(1.0, 40.0),
        "created_at": datetime.now().isoformat(),
        "organization_id": "org-test"
    }
```

### Organization Data Factory
```python
def create_test_organization(name=None):
    """Create test organization data."""
    if name is None:
        name = f"Test Organization {random.randint(1, 100)}"
    
    return {
        "id": f"org-{uuid.uuid4().hex[:8]}",
        "name": name,
        "status": "active",
        "created_at": datetime.now().isoformat()
    }
```

## Common Test Assertions

### Component State Assertions
```python
def assert_component_initialized(component):
    """Assert component is properly initialized."""
    assert component is not None
    assert hasattr(component, '_data')
    assert hasattr(component, 'parent')

def assert_component_has_widgets(component, widget_names):
    """Assert component has expected widgets."""
    for widget_name in widget_names:
        assert hasattr(component, widget_name)

def assert_component_data_valid(component, expected_keys):
    """Assert component data contains expected keys."""
    data = component.get_data()
    for key in expected_keys:
        assert key in data
```

### Service Interaction Assertions
```python
def assert_service_called(mock_service, method_name, *args, **kwargs):
    """Assert service method was called with expected arguments."""
    method = getattr(mock_service, method_name)
    if args or kwargs:
        method.assert_called_with(*args, **kwargs)
    else:
        method.assert_called()

def assert_service_not_called(mock_service, method_name):
    """Assert service method was not called."""
    method = getattr(mock_service, method_name)
    method.assert_not_called()
```

### Event Assertions
```python
def assert_event_published(mock_event_bus, event_type, expected_data=None):
    """Assert event was published with expected data."""
    mock_event_bus.publish.assert_called()
    
    # Check if the specific event was published
    calls = mock_event_bus.publish.call_args_list
    event_found = False
    
    for call in calls:
        args, kwargs = call
        if args[0] == event_type:
            event_found = True
            if expected_data:
                assert kwargs.get('data') == expected_data
            break
    
    assert event_found, f"Event '{event_type}' was not published"
```

This reference guide provides quick access to common testing patterns used throughout the DBR CustomTkinter application. Use these patterns as starting points for writing new tests or as reference when maintaining existing tests.