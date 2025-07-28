# CustomTkinter Template Application

## Overview

This is a **modern, scalable Python GUI application template** built with CustomTkinter that demonstrates best practices for building professional desktop applications. The template provides a complete foundation with modular architecture, event-driven communication, and comprehensive testing setup.

### To run

`uv sync`
`uv pip install -e .`
`./venv/bin/app` or `.venv\Scripts\app.exe`
`uv run python src/main.py`

## Key Features

### **Architecture & Design Patterns**
- **Modern dependency management** using UV (Astral's tool)
- **Object-oriented design** with clear separation of concerns
- **Event-driven architecture** using EventBus pattern for decoupled component communication
- **Test-driven development** setup with pytest
- **Modular component system** for maximum reusability
- **Professional project structure** that scales with application complexity

### **Visual Features**
- **Tabbed navigation system** with dynamic page switching
- **Scrollable canvas with colored grid** - each cell has randomly colored backgrounds (light red, green, yellow)
- **Dashed borders** - white and black dashed borders around each grid cell
- **Interactive grid widgets** with buttons, labels, and comboboxes
- **Real-time statistics display** tracking user interactions
- **Theme switching** between light/dark modes
- **Custom menu system** with dropdown functionality

## Application Structure

### **Main Components**

1. **MainWindow** (`src/app/main_window.py`)
   - Central application window with menu bar, tab navigation, and status bar
   - Window centering and configuration management
   - Event handling for tab changes and window closing

2. **MenuBar** (`src/app/menu_bar.py`)
   - Custom menu system using CTkOptionMenu widgets
   - File, Edit, View, and Help menus with placeholder functionality
   - Theme toggling capability

3. **TabNavigation** (`src/app/tab_navigation.py`)
   - Dynamic tab system for switching between pages
   - Visual feedback for active tabs
   - Support for adding/removing tabs programmatically

4. **Page1 - Grid Canvas** (`src/app/pages/page1.py`)
   - **Enhanced Visual Grid**: 20x15 scrollable canvas with randomly colored cell backgrounds
   - **Cell Colors**: Light red (#FFE6E6), light green (#E6FFE6), light yellow (#FFFFE6)
   - **Dashed Borders**: Dual-layer white and black dashed borders around each cell
   - Custom grid cell widgets with interactive elements
   - Real-time statistics display using EventBus
   - Mouse wheel scrolling support (vertical and shift+horizontal)

5. **Page2 - Settings** (`src/app/pages/page2.py`)
   - Configuration interface for grid settings
   - Theme selection dropdown
   - Slider controls for cell size
   - Apply settings functionality

### **Custom Components**

1. **ScrollableCanvasFrame** (`src/app/components/scrollable_canvas_frame.py`)
   - **Modified for direct canvas drawing** - removed canvas_frame overlay
   - Canvas with horizontal/vertical scrollbars
   - Mouse wheel support for smooth scrolling
   - White background to show colored grid cells

2. **StatsDisplayFrame** (`src/app/components/stats_display_frame.py`)
   - Real-time statistics display using EventBus pattern
   - Tracks combobox selections across all grid widgets
   - Live updating counter display

3. **GridCellWidget** (`src/app/components/widgets/grid_cell_widget.py`)
   - Interactive grid cells with:
     - Action buttons with click counters
     - Coordinate labels showing (row, col)
     - Dropdown comboboxes with 5 options
   - EventBus integration for real-time stats
   - Data persistence and retrieval methods

4. **BaseComponent** (`src/app/components/base_component.py`)
   - Base class for consistent component architecture
   - Provides common functionality for all custom components

### **Utility Systems**

1. **EventBus** (`src/app/utils/event_bus.py`)
   - Decoupled communication system between components
   - Subscribe/publish pattern for loose coupling
   - Used for real-time statistics updates

2. **Configuration** (`src/utils/config.py`)
   - Centralized application settings using dataclasses
   - Window dimensions, themes, and paths
   - Easy to modify and extend

## Recent Modifications Made

### **Grid Canvas Visual Enhancements**
1. **Added random colored cell backgrounds**:
   - Each of the 300 grid cells (20×15) gets a random background color
   - Colors: Light red, light green, light yellow for visual variety

2. **Implemented dashed border system**:
   - White outer dashed border (2px width, dash pattern 3,3)
   - Black inner dashed border (1px width, dash pattern 2,2)
   - Creates distinctive visual separation between cells

3. **Modified ScrollableCanvasFrame**:
   - Removed canvas_frame overlay that was blocking colored backgrounds
   - Changed canvas background from gray90 to white
   - Now draws directly on canvas for better visual control

## Technical Implementation Details

### **Dependencies**
- **CustomTkinter** (>=5.2.0) - Modern UI framework
- **Pillow** (>=10.0.0) - Image processing
- **tkinter** - Base GUI framework
- **pytest** - Testing framework with coverage

### **Project Structure**
```
src/
├── main.py                     # Application entry point
├── app/
│   ├── main_window.py          # Main application window
│   ├── menu_bar.py             # Custom menu system
│   ├── tab_navigation.py       # Tab switching component
│   ├── pages/
│   │   ├── page1.py            # Enhanced grid canvas page
│   │   └── page2.py            # Settings page
│   ├── components/
│   │   ├── base_component.py   # Base component class
│   │   ├── scrollable_canvas_frame.py  # Modified scrollable canvas
│   │   ├── stats_display_frame.py      # Real-time statistics
│   │   └── widgets/
│   │       ├── grid_cell_widget.py     # Interactive grid cells
│   │       ├── custom_button.py        # Custom button widget
│   │       └── custom_entry.py         # Custom entry widget
│   └── utils/
│       └── event_bus.py        # Event communication system
├── utils/
│   ├── config.py               # Application configuration
│   ├── constants.py            # Application constants
│   └── helpers.py              # Helper functions
└── tests/                      # Comprehensive test structure
```

## Development Workflow

### **Running the Application**
```bash
python src/main.py
```

### **Running Tests**
```bash
pytest
```

### **Key Design Patterns Used**

1. **Event Bus Pattern**: Decoupled communication between components
2. **Observer Pattern**: Real-time statistics updates
3. **Factory Pattern**: Dynamic widget creation in grid
4. **Template Method Pattern**: Base component structure
5. **Strategy Pattern**: Different page implementations

## Future Development Notes

### **For Building Applications Based on This Template**

1. **Grid System**: The enhanced grid canvas provides an excellent foundation for:
   - Data visualization applications
   - Game boards or puzzle interfaces
   - Interactive dashboards
   - Spreadsheet-like applications

2. **Component Architecture**: Easy to extend with new components:
   - Follow BaseComponent pattern for consistency
   - Use EventBus for component communication
   - Add new pages by extending the tab system

3. **Visual Customization**: The colored grid system can be adapted for:
   - Different color schemes based on data
   - Dynamic color changes based on user interaction
   - Custom border styles for different cell types

4. **Event System**: The EventBus is ready for complex interactions:
   - Add new event types as needed
   - Multiple subscribers per event
   - Easy debugging with event logging

### **Recommended Extensions**

1. **Data Persistence**: Add save/load functionality for grid states
2. **Custom Themes**: Extend the theme system with custom color schemes
3. **Plugin Architecture**: Use the component system for plugin development
4. **Advanced Grid Features**: Cell merging, custom cell types, data binding
5. **Export Functionality**: PDF, image, or data export capabilities

## Configuration

The application uses `AppConfig` dataclass for centralized configuration:
- Window title, size, and minimum dimensions
- Theme settings (dark/light mode, color themes)
- Resource paths for icons, themes, and fonts

## Testing

Comprehensive test structure is provided with pytest:
- Unit tests for all components
- Integration tests for component interactions
- Coverage reporting included
- Mock support for isolated testing

This template provides a solid foundation for building scalable, maintainable GUI applications with modern Python practices and professional architecture patterns.