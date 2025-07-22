# CustomTkinter Application Development Plan

## Overview

This tk-template app provides a complete blueprint for building a modern, scalable Python GUI applications using CustomTkinter.
The plan is specifically designed for AI agents to use as a reference and follows industry best practices for:

- **Modern dependency management** with Astral's UV tool
- **Test-driven development (TDD)** with pytest
- **Object-oriented architecture** with reusable components
- **Professional project structure** that scales with complexity
- **CustomTkinter GUI framework** for modern, cross-platform interfaces

The directory includes complete code examples. The document includes testing strategies and development workflows that enable rapid development while maintaining code quality and testability.

## Project Structure

The project follows a modular architecture with clear separation of concerns:

```
project_name/
├── src/                        # Source code directory
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── app/                    # Main application modules
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window
│   │   ├── menu_bar.py         # Menu bar component
│   │   ├── tab_navigation.py   # Tab navigation component
│   │   ├── pages/              # Application pages
│   │   │   ├── __init__.py
│   │   │   ├── page1.py        # Grid canvas page
│   │   │   └── page2.py        # Settings page
│   │   └── components/         # Reusable UI components
│   │       ├── __init__.py
│   │       ├── base_component.py
│   │       ├── scrollable_canvas_frame.py
│   │       ├── stats_display_frame.py
│   │       └── widgets/        # Custom widgets
│   │           ├── __init__.py
│   │           ├── grid_cell_widget.py
│   │           ├── custom_button.py
│   │           └── custom_entry.py
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   ├── constants.py        # Application constants
│   │   └── helpers.py          # Helper functions
│   └── resources/              # Static resources
│       ├── themes/             # Custom themes
│       ├── icons/              # Application icons
│       └── fonts/              # Custom fonts
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration and fixtures
│   ├── test_main_window.py     # Main window tests
│   ├── test_menu_bar.py        # Menu bar tests
│   ├── test_tab_navigation.py  # Tab navigation tests
│   ├── test_pages/             # Page component tests
│   │   ├── __init__.py
│   │   ├── test_page1.py       # Grid page tests
│   │   └── test_page2.py       # Settings page tests
│   └── test_components/        # Component tests
│       ├── __init__.py
│       ├── test_base_component.py
│       ├── test_scrollable_canvas_frame.py
│       ├── test_stats_display_frame.py
│       └── test_widgets/       # Widget tests
│           ├── __init__.py
│           └── test_grid_cell_widget.py
├── pyproject.toml              # UV project configuration
├── uv.lock                     # UV lock file (auto-generated)
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

## Setup Instructions

### 1. Environment Setup with UV
```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Initialize project with UV
uv init my-tkinter-app
cd my-tkinter-app

# Add dependencies
uv add customtkinter
uv add --dev pytest pytest-mock pytest-cov

# Create virtual environment and install dependencies
uv sync
```

### 2. Project Configuration (pyproject.toml)
```toml
[project]
name = "my-tkinter-app"
version = "0.1.0"
description = "A modern CustomTkinter application with best practices"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "customtkinter>=5.2.0",
    "pillow>=10.0.0",
]

[build-system]
requires = ["uv_build>=0.8.0,<0.9"]
build-backend = "uv_build"

[dependency-groups]
dev = [
    "pytest>=7.4.0",
    "pytest-mock>=3.11.0",
    "pytest-cov>=4.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[project.scripts]
app = "app.main:main"

```

## Development Workflow

### Complex Component Testing
```bash
# Test specific components
uv run pytest tests/test_components/test_widgets/ -v
uv run pytest tests/test_pages/ -v

# Test with specific markers
uv run pytest -m "not slow" -v                    # Skip slow tests
uv run pytest -k "grid" -v                        # Run grid-related tests
uv run pytest tests/test_page1.py::TestPage1::test_widget_addition -v

# Run tests with detailed output
uv run pytest --tb=long -v                        # Long traceback format
uv run pytest --capture=no -v                     # Show print statements
```

### Application Usage Examples
```bash
# Start the application
uv run python src/main.py

# Development mode
uv run python src/main.py --debug    # If debug mode implemented

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test categories
uv run pytest -m unit
uv run pytest -m integration

# Run tests matching a pattern
uv run pytest -k "test_menu" -v

# Run tests in watch mode (if pytest-watch is added)
uv add --dev pytest-watch
uv run ptw                           # Watch tests

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Update all dependencies
uv sync --upgrade

# Show dependency tree
uv tree

# Export requirements (if needed for Docker/deployment)
uv export --format requirements-txt --output-file requirements.txt
```

## Complex Component Development Pattern

When building complex components like the grid system, follow this enhanced pattern:

1. **Design the Component Interface**
   ```python
   # First, define what the component should do
   class GridCanvasInterface:
       def add_widget_at(self, row: int, col: int, widget_type: str) -> None: ...
       def remove_widget_at(self, row: int, col: int) -> None: ...
       def get_widget_data(self, row: int, col: int) -> Dict: ...
       def highlight_cell(self, row: int, col: int, highlight: bool) -> None: ...
   ```

2. **Write Component Tests First**
   ```python
   def test_grid_widget_positioning():
       # Test that widgets are positioned correctly in grid
       pass

   def test_grid_scrolling():
       # Test that scrolling works with large grids
       pass

   def test_widget_interactions():
       # Test that widget events bubble up correctly
       pass
   ```

3. **Implement Base Functionality**
   - Start with the simplest implementation that passes tests
   - Add features incrementally

4. **Add Complex Features**
   - Scrolling, zooming, selection, drag-and-drop
   - Always write tests for new features first

5. **Integration Testing**
   - Test how components work together
   - Test performance with large datasets
   - Test edge cases and error conditions

### 18. Advanced Architecture Patterns

#### Component Communication (Event Bus Pattern)

For real-time updates and decoupled communication between components, the **Event Bus pattern** is employed. This pattern allows components to publish events without knowing which other components are listening, and components can subscribe to events they are interested in.

**Key Principles:**

-   **Decoupling**: Components do not directly interact, reducing dependencies and increasing reusability.
-   **Centralized Communication**: All events flow through a single `EventBus` instance.
-   **Flexibility**: New components can easily be added to publish or subscribe to events without modifying existing code.

**Implementation Details:**

-   The `EventBus` class (located in `src/app/utils/event_bus.py`) provides `subscribe` and `publish` methods.
-   **Publishers**: Components that generate events (e.g., `GridCellWidget`) inject the `EventBus` instance and call `self.event_bus.publish('event_name', data={...})` when a relevant action occurs.
    -   **Example**: In `GridCellWidget`, when a combobox value changes, it publishes a `"grid_value_changed"` event with the `old_value` and `new_value`.
-   **Subscribers**: Components that need to react to events (e.g., `StatsDisplayFrame`) inject the `EventBus` instance and call `self.event_bus.subscribe('event_name', self.handler_method)`.
    -   **Example**: `StatsDisplayFrame` subscribes to `"grid_value_changed"` events and updates its displayed statistics in response.
-   **Initialization**: The `EventBus` instance is typically created in a higher-level component (e.g., `Page1`) and passed down to child components that need to communicate.

**Example Usage:**

```python
# src/app/utils/event_bus.py
from typing import Callable, Dict, Any

class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def publish(self, event_type: str, data: Any) -> None:
        for callback in self._listeners.get(event_type, []):
            callback(data)

# src/app/components/widgets/grid_cell_widget.py (Publisher)
class GridCellWidget(ctk.CTkFrame):
    def __init__(self, parent, row: int, col: int, event_bus: EventBus, **kwargs):
        # ...
        self.event_bus = event_bus
        # ...
        self.option_combo.set("Option 1") # Initial value
        # ...

    def _on_combo_change(self, selected_value: str) -> None:
        old_value = self._data["selected_option"]
        self._data["selected_option"] = selected_value
        if self.event_bus:
            self.event_bus.publish(
                "grid_value_changed",
                data={"old_value": old_value, "new_value": selected_value},
            )
        # ...

# src/app/components/stats_display_frame.py (Subscriber)
from collections import Counter

class StatsDisplayFrame(BaseComponent):
    def __init__(self, parent: ctk.CTk, event_bus: EventBus, **kwargs: Dict) -> None:
        super().__init__(parent, **kwargs)
        self.event_bus = event_bus
        self.stats: Counter = Counter()
        # ...
        self.event_bus.subscribe("grid_value_changed", self.handle_grid_update)

    def handle_grid_update(self, data: Dict) -> None:
        old_value = data.get("old_value")
        new_value = data.get("new_value")

        if old_value:
            self.stats[old_value] -= 1
            if self.stats[old_value] == 0:
                del self.stats[old_value]
        if new_value:
            self.stats[new_value] += 1
        self.stats_label.configure(text=self._format_stats())
        # ...

# src/app/pages/page1.py (Or a higher-level orchestrator)
class Page1(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.event_bus = EventBus() # Initialize the event bus
        # ...
        self.stats_frame = StatsDisplayFrame(self, self.event_bus) # Pass event bus
        # ...
        self._populate_sample_widgets() # Populates grid_widgets
        self._initialize_stats_display() # Publishes initial values

    def _add_grid_widget(self, row: int, col: int) -> None:
        # ...
        widget = GridCellWidget(
            self.canvas_frame.get_canvas(),
            row=row,
            col=col,
            event_bus=self.event_bus, # Pass event bus to grid cells
        )
        # ...

    def _initialize_stats_display(self) -> None:
        # Publish initial combobox values to the stats display
        for widget in self.grid_widgets.values():
            initial_value = widget.get_data().get("selected_option")
            if initial_value:
                self.event_bus.publish("grid_value_changed", data={"old_value": None, "new_value": initial_value})
```

#### Data Management Pattern
```python
# Centralized data store
class AppDataStore:
    def __init__(self):
        self._data = {
            'grid_data': {},
            'settings': {},
            'ui_state': {}
        }
        self._observers = []

    def update_grid_cell(self, row: int, col: int, data: Dict):
        self._data['grid_data'][(row, col)] = data
        self._notify_observers('grid_updated', (row, col), data)

    def subscribe(self, callback: Callable):
        self._observers.append(callback)
```

### 19. Performance Considerations

#### For Large Grids
```python
# Virtual scrolling for large datasets
class VirtualizedGrid:
    def __init__(self, total_rows: int, total_cols: int, visible_rows: int, visible_cols: int):
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.visible_rows = visible_rows
        self.visible_cols = visible_cols
        self._visible_widgets = {}

    def update_visible_area(self, start_row: int, start_col: int):
        # Only create widgets for visible area
        # Reuse widgets when scrolling
        pass
```

#### Memory Management
```python
# Widget pooling for performance
class WidgetPool:
    def __init__(self, widget_class, initial_size: int = 10):
        self.widget_class = widget_class
        self._available = []
        self._in_use = set()

        # Pre-create widgets
        for _ in range(initial_size):
            widget = widget_class()
            widget.place_forget()  # Hide initially
            self._available.append(widget)

    def get_widget(self) -> Any:
        if self._available:
            widget = self._available.pop()
        else:
            widget = self.widget_class()

        self._in_use.add(widget)
        return widget

    def return_widget(self, widget: Any):
        if widget in self._in_use:
            widget.place_forget()  # Hide widget
            self._in_use.remove(widget)
            self._available.append(widget)
```

This enhanced plan now provides comprehensive examples of complex CustomTkinter components including:

- **Tab navigation system** for multi-page applications
- **Scrollable canvas with grid** for large data visualization
- **Custom grid cell widgets** with interactive components
- **Event handling and data management** between components
- **Advanced testing patterns** for complex interactions
- **Performance optimization strategies** for large datasets

The coding agent will now have detailed examples of how to structure complex applications with proper separation of concerns, testable components, and scalable architecture patterns.

1. **Red Phase**: Write a failing test
```bash
# Run specific test
uv run pytest tests/test_main_window.py::TestMainWindow::test_window_initialization -v
```

2. **Green Phase**: Write minimal code to pass the test
```bash
# Run all tests
uv run pytest
```

3. **Refactor Phase**: Improve code while keeping tests green

### Additional UV Development Commands

```bash
# Direct UV commands
uv run pytest -k "test_window" -v    # Run specific test pattern
uv run pytest --lf                   # Run last failed tests
uv run pytest --watch                # Watch mode (if pytest-watch installed)
```

### 13. Component Development Pattern

Each new component should follow this pattern:

1. **Create the test file first** (`tests/test_components/test_new_component.py`)
2. **Define the component interface** in the test
3. **Implement the component** extending `BaseComponent`
4. **Add integration tests** for the component in the main window
5. **Document the component** with docstrings and type hints

### Guidelines for Repeatable Tkinter GUI Component Development

Based on the successful implementation and testing of the initial components, the following guidelines provide a repeatable and robust approach for building new GUI components in this project. Adhering to these principles is crucial for maintaining a scalable, testable, and maintainable codebase.

#### 1. Test-Driven Development (TDD) is Mandatory

Every component must be developed using a strict TDD workflow. This was key to resolving the initial `test_window_initialization` failure and ensures that every part of the GUI is verifiable.

-   **Red-Green-Refactor Cycle**:
    1.  **Red**: Write a test that defines a piece of functionality and watch it fail. For example, a test to assert that a `title()` method is called on the main window.
    2.  **Green**: Write the simplest, most direct code possible to make the test pass. This might not be the most elegant solution, but it fulfills the contract defined by the test.
    3.  **Refactor**: Improve the implementation code's structure and clarity while ensuring all tests remain green.

-   **Test Granularity**: Create specific tests for each distinct behavior: initialization, widget placement, event handling, state changes, and destruction.

#### 2. Component-Based Architecture

Build the UI from small, independent, and reusable components. The `main_window`, `menu_bar`, and `tab_navigation` are examples of this.

-   **Single Responsibility Principle**: Each component should do one thing and do it well. For example, `MenuBar` is only responsible for creating and managing the application's menu.
-   **Inheritance**: Use a `BaseComponent` class for common setup and teardown logic, but avoid deep inheritance hierarchies.
-   **Composition over Inheritance**: Build complex UIs by combining simpler components rather than creating monolithic classes.

#### 3. Isolate Components with Mocking

Unit tests must isolate the component under test from its dependencies. This is the most critical lesson from the initial test failures.

-   **Mock Dependencies**: Use `pytest-mock`'s `mocker` fixture to replace dependencies like parent widgets, other components, or utility modules.
-   **Assert Interactions**: Instead of checking the visual outcome (which is difficult and brittle), write tests that assert the component correctly *interacts* with its dependencies. For example, `mock_parent.title.assert_called_with("My Application")` verifies that the component called the `title` method with the correct argument, not that the window title actually changed.

#### 4. Follow a Strict File and Class Structure

Consistency in structure makes the codebase predictable and easy to navigate.

-   **Component Location**: All reusable GUI components reside in `src/app/components/`.
-   **Test Location**: Corresponding tests must be in `tests/test_components/`.
-   **Naming Conventions**:
    -   Component class: `MyComponent` (PascalCase)
    -   Component file: `my_component.py` (snake_case)
    -   Test class: `TestMyComponent`
    -   Test file: `test_my_component.py`

#### 5. Use Dependency Injection

Pass all external requirements (dependencies) into a component's constructor. This makes the component's dependencies explicit and allows for easy replacement with mocks during testing.

-   **Required Dependencies**: Always pass the `parent` tkinter widget.
-   **Optional Dependencies**: Pass other collaborators like an `event_bus` or a `data_store` if needed.

**Example: Creating a New `StatusBar` Component**

1.  **Write the test (`tests/test_components/test_status_bar.py`)**:
    ```python
    from unittest.mock import Mock
    from app.components.status_bar import StatusBar

    def test_status_bar_initialization(mocker):
        mock_parent = Mock()
        status_bar = StatusBar(parent=mock_parent)
        # Assert it's packed or gridded correctly
        mock_parent.pack.assert_called_once()
        # Assert a default message is set
        assert status_bar.message_label.cget("text") == "Ready"

    def test_set_message(mocker):
        mock_parent = Mock()
        status_bar = StatusBar(parent=mock_parent)
        status_bar.set_message("Loading...")
        assert status_bar.message_label.cget("text") == "Loading..."
    ```

2.  **Create the component (`src/app/components/status_bar.py`)**:
    ```python
    import customtkinter as ctk
    from .base_component import BaseComponent

    class StatusBar(BaseComponent):
        def __init__(self, parent, **kwargs):
            super().__init__(parent, **kwargs)
            self.message_label = ctk.CTkLabel(self, text="Ready")
            self.message_label.pack(side="left", padx=10)
            self.pack(side="bottom", fill="x") # Or however it should be placed

        def set_message(self, message: str):
            self.message_label.configure(text=message)
    ```

By following these guidelines, development becomes a predictable, test-driven process, resulting in a GUI application that is robust, maintainable, and easy to extend.

### 14. Best Practices Checklist

#### Code Quality
- [ ] Use type hints for all function parameters and return values
- [ ] Follow PEP 8 style guidelines
- [ ] Use descriptive variable and function names
- [ ] Add comprehensive docstrings
- [ ] Keep functions small and focused (single responsibility)

#### Testing
- [ ] Write tests before implementing features (TDD)
- [ ] Aim for high test coverage (>90%)
- [ ] Use mocks to isolate unit tests from GUI components
- [ ] Test both happy path and error conditions
- [ ] Use descriptive test names

#### Architecture
- [ ] Separate business logic from GUI code
- [ ] Use dependency injection for testability
- [ ] Keep components loosely coupled
- [ ] Use configuration files for constants
- [ ] Implement proper error handling

#### GUI Development
- [ ] Use CustomTkinter for modern appearance
- [ ] Implement responsive layouts
- [ ] Handle window resizing gracefully
- [ ] Provide visual feedback for user actions
- [ ] Follow platform-specific UI conventions


### Additional UV Benefits for Development

**Fast dependency resolution**: UV resolves and installs dependencies much faster than pip

**Lockfile support**: `uv.lock` ensures reproducible builds across environments

**Script management**: Define and run project scripts easily with `uv run`

**Virtual environment management**: UV automatically manages virtual environments

**Cross-platform support**: Works consistently across Windows, macOS, and Linux

This plan provides a solid foundation for building a scalable, testable CustomTkinter application using UV for modern Python dependency management, following best practices for object-oriented design, test-driven development, and modular architecture.