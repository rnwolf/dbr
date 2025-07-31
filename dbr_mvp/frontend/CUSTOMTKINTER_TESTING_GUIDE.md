# CustomTkinter Testing Guide for DBR Application

## Overview

This comprehensive guide covers testing strategies, patterns, and best practices for CustomTkinter applications in the DBR (Drum Buffer Rope) system. The guide addresses the unique challenges of testing GUI applications and provides practical solutions for maintaining high test coverage while avoiding GUI-related issues.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Core Testing Challenges](#core-testing-challenges)
3. [Mocking Strategies](#mocking-strategies)
4. [Test Structure Patterns](#test-structure-patterns)
5. [Component Testing](#component-testing)
6. [Integration Testing](#integration-testing)
7. [Authentication Testing](#authentication-testing)
8. [Role-Based Navigation Testing](#role-based-navigation-testing)
9. [Event-Driven Testing](#event-driven-testing)
10. [Common Issues and Solutions](#common-issues-and-solutions)
11. [Best Practices](#best-practices)
12. [Test Fixtures and Utilities](#test-fixtures-and-utilities)

## Testing Philosophy

### Core Principles

1. **No GUI Rendering**: Tests should never create actual GUI windows
2. **Comprehensive Mocking**: Mock all CustomTkinter components to isolate business logic
3. **Behavior Testing**: Focus on testing component behavior, not GUI appearance
4. **Fast Execution**: Tests should run quickly without GUI overhead
5. **Isolated Testing**: Each test should be independent and not affect others

### Test-Driven Development (TDD) Approach

The DBR application follows TDD principles:
- Write tests first to define expected behavior
- Implement minimal code to pass tests
- Refactor while maintaining test coverage
- Maintain high test coverage (>90%)

## Core Testing Challenges

### 1. GUI Component Initialization

**Challenge**: CustomTkinter components require a parent widget and can trigger GUI creation.

**Solution**: Mock all CustomTkinter classes and their initialization.

```python
@patch('customtkinter.CTk')
@patch('customtkinter.CTkFrame')
@patch('customtkinter.CTkLabel')
def test_component_creation(mock_label, mock_frame, mock_ctk):
    # Test component logic without GUI
    pass
```

### 2. Widget Interaction Testing

**Challenge**: Testing user interactions without actual GUI events.

**Solution**: Test the underlying callback methods directly.

```python
def test_button_click_behavior(self, mocked_component):
    component, mocks = mocked_component
    
    # Test the callback method directly
    component._on_button_click()
    
    # Assert expected behavior
    assert component.click_count == 1
```

### 3. State Management

**Challenge**: Testing component state changes without visual feedback.

**Solution**: Test internal data structures and state variables.

```python
def test_state_change(self, component):
    initial_state = component.get_state()
    component.update_state({"key": "new_value"})
    
    assert component.get_state() != initial_state
    assert component.get_state()["key"] == "new_value"
```

## Mocking Strategies

### 1. Global Mocking (conftest.py)

Use global fixtures to mock common dependencies:

```python
# conftest.py
@pytest.fixture(autouse=True)
def mock_dbrsdk():
    """Mock the entire dbrsdk to prevent import errors."""
    with patch.dict('sys.modules', {
        'dbrsdk': MagicMock(),
        'dbrsdk.models': MagicMock(),
    }) as mock:
        yield mock

@pytest.fixture
def mock_tk():
    """Mock tkinter to avoid GUI during tests."""
    with patch("tkinter.Tk"), patch("customtkinter.CTk"):
        yield
```

### 2. Comprehensive Component Mocking

For complex components, mock all CustomTkinter elements:

```python
@pytest.fixture
def mocked_main_window(mock_dbr_service):
    """Create a fully mocked MainWindow instance."""
    with patch('frontend.dbr_service.Dbrsdk'):
        with patch('frontend.main_window.ctk.CTk') as mock_ctk:
            with patch('frontend.main_window.MenuBar') as mock_menu:
                with patch('frontend.main_window.TabNavigation') as mock_tab_nav:
                    with patch('frontend.main_window.UserContextWidget') as mock_user_widget:
                        with patch('frontend.main_window.ctk.CTkFrame') as mock_frame:
                            with patch('frontend.main_window.ctk.CTkLabel') as mock_label:
                                with patch('frontend.main_window.ctk.CTkButton') as mock_button:
                                    
                                    # Setup mock instances
                                    mock_ctk_instance = Mock()
                                    mock_ctk.return_value = mock_ctk_instance
                                    
                                    # Import and create component
                                    from frontend.main_window import MainWindow
                                    window = MainWindow(mock_dbr_service)
                                    
                                    return window, {
                                        "ctk_instance": mock_ctk_instance,
                                        "menu": mock_menu.return_value,
                                        "tab_nav": mock_tab_nav.return_value,
                                        "user_widget": mock_user_widget.return_value,
                                    }
```

### 3. Targeted Mocking

For specific functionality, use targeted mocking:

```python
@patch("customtkinter.CTkComboBox")
@patch("customtkinter.CTkButton")
def test_specific_widget_behavior(mock_button, mock_combo):
    # Test specific widget interactions
    pass
```

## Test Structure Patterns

### 1. Component Test Class Structure

```python
class TestComponentName:
    """Test cases for ComponentName."""
    
    def test_initialization(self, mocked_component):
        """Test component initializes correctly."""
        component, mocks = mocked_component
        
        # Test initialization
        assert component is not None
        assert hasattr(component, 'expected_attribute')
    
    def test_user_interaction(self, mocked_component):
        """Test user interaction handling."""
        component, mocks = mocked_component
        
        # Simulate user action
        component._handle_user_action()
        
        # Assert expected behavior
        assert component.state_changed
    
    def test_data_management(self, mocked_component):
        """Test data get/set operations."""
        component, mocks = mocked_component
        
        # Test data operations
        test_data = {"key": "value"}
        component.set_data(test_data)
        
        assert component.get_data() == test_data
```

### 2. Integration Test Structure

```python
class TestComponentIntegration:
    """Integration tests for component interactions."""
    
    def test_component_communication(self, mocked_app):
        """Test communication between components."""
        app, mocks = mocked_app
        
        # Test component interaction
        app.component_a.trigger_event()
        
        # Verify component_b received the event
        assert app.component_b.event_received
```

## Component Testing

### 1. Base Component Testing

Test abstract base components:

```python
class TestBaseComponent:
    """Test the BaseComponent abstract class."""
    
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_base_component_interface(self, mock_frame_init):
        """Test base component provides required interface."""
        
        # Create concrete implementation for testing
        class TestComponent(BaseComponent):
            def _setup_component(self): pass
            def _create_widgets(self): pass
            def _setup_layout(self): pass
            def _update_display(self): pass
        
        parent = Mock()
        component = TestComponent(parent)
        
        # Test interface methods
        assert hasattr(component, 'get_data')
        assert hasattr(component, 'set_data')
        assert hasattr(component, 'validate')
        assert hasattr(component, 'reset')
```

### 2. Widget Component Testing

Test custom widgets with comprehensive mocking:

```python
class TestGridCellWidget:
    """Test cases for GridCellWidget."""
    
    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_widget_initialization(self, mock_frame_init, mock_button, 
                                 mock_label, mock_combo, mock_font):
        """Test widget initialization."""
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        widget = GridCellWidget(parent, row=5, col=3)
        
        assert widget.row == 5
        assert widget.col == 3
        assert widget._data["row"] == 5
        assert widget._data["col"] == 3
```

### 3. Event Handling Testing

Test event-driven components:

```python
def test_event_handling(self, mocked_widget):
    """Test event handling in widgets."""
    widget, mocks = mocked_widget
    
    # Mock event bus
    event_bus = Mock()
    widget.event_bus = event_bus
    
    # Trigger event
    widget._on_combo_change("new_value")
    
    # Verify event was published
    event_bus.publish.assert_called_once_with(
        "grid_value_changed",
        data={"old_value": "old_value", "new_value": "new_value"}
    )
```

## Integration Testing

### 1. Service Integration

Test integration with backend services:

```python
class TestServiceIntegration:
    """Test integration with DBR services."""
    
    def test_authentication_service_integration(self, mock_dbr_service):
        """Test authentication service integration."""
        # Setup service mock
        mock_dbr_service.login.return_value = True
        mock_dbr_service.get_user_info.return_value = {
            "username": "testuser",
            "role": "Planner"
        }
        
        # Test service integration
        with patch('frontend.authentication_ui.DBRService'):
            from frontend.authentication_ui import LoginDialog
            dialog = LoginDialog(None, "http://localhost:8000")
            
            result = dialog._attempt_login("testuser", "password")
            
            assert result is True
```

### 2. Component Communication

Test communication between components:

```python
def test_component_communication(self, mocked_main_window):
    """Test communication between main window components."""
    window, mocks = mocked_main_window
    
    # Test menu bar communicates with main window
    window.menu_bar.trigger_action("logout")
    
    # Verify main window responds
    assert window.logout_requested
```

## Authentication Testing

### 1. Login Dialog Testing

```python
class TestLoginDialog:
    """Test authentication dialog functionality."""
    
    @patch('frontend.authentication_ui.DBRService')
    def test_successful_login(self, mock_dbr_service):
        """Test successful login flow."""
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = True
        mock_service_instance.get_user_info.return_value = {
            "username": "admin", "role": "Super Admin"
        }
        
        from frontend.authentication_ui import LoginDialog
        dialog = LoginDialog(None, "http://localhost:8000")
        
        result = dialog._attempt_login("admin", "admin123")
        
        assert result is True
        mock_service_instance.login.assert_called_once_with("admin", "admin123")
    
    @patch('frontend.authentication_ui.DBRService')
    def test_failed_login(self, mock_dbr_service):
        """Test failed login handling."""
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = False
        
        from frontend.authentication_ui import LoginDialog
        dialog = LoginDialog(None, "http://localhost:8000")
        
        result = dialog._attempt_login("invalid", "invalid")
        
        assert result is False
```

### 2. User Context Testing

```python
def test_user_context_widget(self, mock_dbr_service):
    """Test user context widget functionality."""
    mock_dbr_service.get_user_info.return_value = {
        "username": "testuser",
        "display_name": "Test User"
    }
    mock_dbr_service.get_current_organization.return_value = {
        "name": "Test Organization"
    }
    
    with patch('frontend.authentication_ui.ctk.CTkFrame'):
        from frontend.authentication_ui import UserContextWidget
        widget = UserContextWidget(None, mock_dbr_service)
        
        assert widget.user_info["username"] == "testuser"
        assert widget.organization_info["name"] == "Test Organization"
```

## Role-Based Navigation Testing

### 1. Role Permission Testing

```python
class TestRoleBasedNavigation:
    """Test role-based navigation system."""
    
    def test_super_admin_navigation(self, mock_dbr_service):
        """Test Super Admin gets all navigation tabs."""
        mock_dbr_service.get_user_role.return_value = "Super Admin"
        mock_dbr_service.has_permission.return_value = True
        
        with comprehensive_mocking():
            from frontend.main_window import MainWindow
            window = MainWindow(mock_dbr_service)
            
            # Verify Super Admin gets all tabs
            expected_tabs = [
                "Organizations", "Users", "System", "Setup", 
                "Work Items", "Collections", "Planning", 
                "Buffer Boards", "Reports"
            ]
            
            for tab in expected_tabs:
                assert tab in window.available_tabs
    
    def test_viewer_navigation(self, mock_dbr_service):
        """Test Viewer gets limited navigation tabs."""
        mock_dbr_service.get_user_role.return_value = "Viewer"
        mock_dbr_service.has_permission.side_effect = lambda perm: perm in [
            "view_buffer_boards", "view_reports"
        ]
        
        with comprehensive_mocking():
            from frontend.main_window import MainWindow
            window = MainWindow(mock_dbr_service)
            
            # Verify Viewer gets only allowed tabs
            expected_tabs = ["Buffer Boards", "Reports"]
            
            assert len(window.available_tabs) == len(expected_tabs)
            for tab in expected_tabs:
                assert tab in window.available_tabs
```

### 2. Permission Checking

```python
def test_permission_checking(self, mock_dbr_service):
    """Test permission checking for navigation."""
    mock_dbr_service.has_permission.side_effect = lambda perm: perm == "manage_work_items"
    
    with comprehensive_mocking():
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        # Test permission checking
        assert window._check_tab_permission("Work Items") is True
        assert window._check_tab_permission("Organizations") is False
```

## Event-Driven Testing

### 1. Event Bus Testing

```python
class TestEventBus:
    """Test event bus functionality."""
    
    def test_event_publishing(self):
        """Test event publishing and subscription."""
        from frontend.utils.event_bus import EventBus
        
        event_bus = EventBus()
        callback = Mock()
        
        # Subscribe to event
        event_bus.subscribe("test_event", callback)
        
        # Publish event
        event_data = {"key": "value"}
        event_bus.publish("test_event", data=event_data)
        
        # Verify callback was called
        callback.assert_called_once_with(data=event_data)
    
    def test_event_unsubscription(self):
        """Test event unsubscription."""
        from frontend.utils.event_bus import EventBus
        
        event_bus = EventBus()
        callback = Mock()
        
        # Subscribe and unsubscribe
        event_bus.subscribe("test_event", callback)
        event_bus.unsubscribe("test_event", callback)
        
        # Publish event
        event_bus.publish("test_event", data={})
        
        # Verify callback was not called
        callback.assert_not_called()
```

### 2. Component Event Integration

```python
def test_component_event_integration(self, mocked_grid_widget):
    """Test component integration with event bus."""
    widget, mocks = mocked_grid_widget
    
    # Mock event bus
    event_bus = Mock()
    widget.event_bus = event_bus
    
    # Trigger component event
    widget._on_combo_change("Option 2")
    
    # Verify event was published with correct data
    event_bus.publish.assert_called_once_with(
        "grid_value_changed",
        data={"old_value": "Option 1", "new_value": "Option 2"}
    )
```

## Common Issues and Solutions

### 1. White TK Window Issue

**Problem**: A white tkinter window appears during test runs.

**Cause**: Incomplete mocking of tkinter/CustomTkinter components.

**Solution**: Use comprehensive mocking and avoid global tkinter mocking.

```python
# Instead of global mocking, use targeted mocking
@patch('frontend.main_window.ctk.CTk')
@patch('frontend.main_window.ctk.CTkFrame')
def test_without_window_creation(mock_frame, mock_ctk):
    # Test implementation
    pass
```

### 2. Import Errors

**Problem**: Import errors when importing GUI components in tests.

**Cause**: Missing dependencies or circular imports.

**Solution**: Mock dependencies before importing.

```python
@patch('frontend.authentication_ui.DBRService')
def test_with_mocked_dependencies(mock_service):
    # Import after mocking
    from frontend.authentication_ui import LoginDialog
    # Test implementation
```

### 3. Mock Configuration Issues

**Problem**: Mocks not behaving as expected.

**Cause**: Incorrect mock setup or missing attributes.

**Solution**: Properly configure mock objects.

```python
def setup_proper_mock():
    parent = Mock()
    parent._last_child_ids = {}
    parent.tk = Mock()
    parent.children = {}
    return parent
```

### 4. Test Isolation Issues

**Problem**: Tests affecting each other.

**Cause**: Shared state or incomplete cleanup.

**Solution**: Use proper fixtures and cleanup.

```python
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup and cleanup test environment."""
    os.environ["TESTING"] = "1"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
```

## Best Practices

### 1. Test Organization

- Group related tests in classes
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Keep tests focused and atomic

### 2. Mocking Guidelines

- Mock at the boundary (external dependencies)
- Use the minimum necessary mocking
- Verify mock interactions when relevant
- Reset mocks between tests

### 3. Fixture Design

- Create reusable fixtures for common setups
- Use parametrized fixtures for variations
- Keep fixtures focused and single-purpose
- Document fixture behavior

### 4. Test Data Management

- Use factories for test data creation
- Avoid hardcoded values in tests
- Create realistic test scenarios
- Use constants for repeated values

### 5. Error Testing

- Test both success and failure paths
- Test edge cases and boundary conditions
- Verify error handling and user feedback
- Test recovery scenarios

## Test Fixtures and Utilities

### 1. Common Fixtures

```python
# conftest.py
@pytest.fixture
def mock_dbr_service():
    """Create a mock DBR service with common methods."""
    service = Mock()
    service.get_user_info.return_value = {
        "username": "testuser", 
        "display_name": "Test User"
    }
    service.get_user_role.return_value = "Planner"
    service.get_current_organization.return_value = {
        "name": "Test Organization"
    }
    service.is_authenticated.return_value = True
    service.has_permission.return_value = True
    return service

@pytest.fixture
def mock_parent_widget():
    """Create a properly configured mock parent widget."""
    parent = Mock()
    parent._last_child_ids = {}
    parent.tk = Mock()
    parent.children = {}
    return parent
```

### 2. Test Utilities

```python
# test_utils.py
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
    )

def create_test_user_data(role="Planner"):
    """Create test user data for different roles."""
    return {
        "username": f"test_{role.lower()}",
        "display_name": f"Test {role}",
        "role": role,
        "organization": "Test Organization"
    }
```

### 3. Custom Assertions

```python
def assert_tab_created(mock_tab_nav, tab_name):
    """Assert that a specific tab was created."""
    tab_calls = [call[0][0] for call in mock_tab_nav.add_tab.call_args_list]
    assert tab_name in tab_calls, f"Tab '{tab_name}' was not created"

def assert_permission_checked(mock_service, permission):
    """Assert that a specific permission was checked."""
    mock_service.has_permission.assert_any_call(permission)
```

## Running Tests

### 1. Test Execution Commands

```bash
# Run all frontend tests
cd dbr_mvp/frontend
uv run pytest tests -v

# Run specific test file
uv run pytest tests/test_authentication_ui.py -v

# Run with coverage
uv run pytest tests --cov=src --cov-report=html

# Run tests matching pattern
uv run pytest tests -k "test_login" -v
```

### 2. Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
```

### 3. Coverage Configuration

```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Conclusion

This guide provides comprehensive coverage of testing strategies for CustomTkinter applications. By following these patterns and practices, you can maintain high test coverage while avoiding GUI-related issues and ensuring reliable, maintainable tests.

Key takeaways:
- Always mock GUI components to avoid window creation
- Test behavior, not appearance
- Use comprehensive mocking for complex components
- Follow TDD principles for new features
- Maintain test isolation and independence
- Focus on business logic and user interactions

For specific implementation examples, refer to the existing test files in the `tests/` directory, which demonstrate these patterns in practice.