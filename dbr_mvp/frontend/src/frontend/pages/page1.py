"""Page 1 - Grid canvas with scrollable viewport and custom widgets."""

import customtkinter as ctk
import random
from typing import Dict, Tuple
from ..components.scrollable_canvas_frame import ScrollableCanvasFrame
from ..components.widgets.grid_cell_widget import GridCellWidget
from ..components.stats_display_frame import StatsDisplayFrame
from ..utils.event_bus import EventBus


class Page1(ctk.CTkFrame):
    """Page 1 containing a scrollable canvas with grid and custom widgets."""

    def __init__(self, parent):
        super().__init__(parent)

        # Grid configuration
        self.grid_rows = 20
        self.grid_cols = 15
        self.cell_size = 100
        self.grid_widgets: Dict[Tuple[int, int], GridCellWidget] = {}
        self.event_bus = EventBus()

        self._setup_page()
        self._create_grid()
        self._populate_sample_widgets()
        self._initialize_stats_display()

    def _setup_page(self) -> None:
        """Setup the page layout."""
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Grid Canvas View", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(10, 10))

        # Stats Display
        self.stats_frame = StatsDisplayFrame(self, self.event_bus)
        self.stats_frame.pack(pady=5, fill="x", padx=10)

        # Scrollable canvas frame
        self.canvas_frame = ScrollableCanvasFrame(
            self,
            canvas_width=self.grid_cols * self.cell_size,
            canvas_height=self.grid_rows * self.cell_size,
        )
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _create_grid(self) -> None:
        """Create the grid with colored cell backgrounds and dashed borders."""
        canvas = self.canvas_frame.get_canvas()
        
        # Define the light colors for cell backgrounds
        colors = ["#FFE6E6", "#E6FFE6", "#FFFFE6"]  # light red, light green, light yellow
        
        # Create cell backgrounds with random colors
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Random color selection
                bg_color = random.choice(colors)
                
                # Create colored background rectangle
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline="",
                    width=0
                )
        
        # Create dashed borders around each cell
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Create dashed white border (outer)
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline="white",
                    width=2,
                    dash=(3, 3),
                    fill=""
                )
                
                # Create dashed black border (inner, slightly offset)
                canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    outline="black",
                    width=1,
                    dash=(2, 2),
                    fill=""
                )

    def _populate_sample_widgets(self) -> None:
        """Populate some grid cells with sample widgets."""
        # Sample widget positions
        widget_positions = [(2, 3), (5, 7), (8, 2), (12, 10), (15, 5), (3, 12), (18, 8)]

        for row, col in widget_positions:
            if 0 <= row < self.grid_rows and 0 <= col < self.grid_cols:
                self._add_grid_widget(row, col)

    def _initialize_stats_display(self) -> None:
        """Initializes the StatsDisplayFrame with current combobox values."""
        for widget in self.grid_widgets.values():
            initial_value = widget.get_data().get("selected_option")
            if initial_value:
                self.event_bus.publish("grid_value_changed", data={"old_value": None, "new_value": initial_value})

    def _add_grid_widget(self, row: int, col: int) -> None:
        """Add a custom widget to the specified grid cell."""
        # Calculate position
        x = col * self.cell_size + 5  # 5px padding
        y = row * self.cell_size + 5

        # Create widget
        widget = GridCellWidget(
            self.canvas_frame.get_canvas(),
            row=row,
            col=col,
            width=self.cell_size - 10,  # Account for padding
            height=self.cell_size - 10,
            event_bus=self.event_bus,
        )

        # Place widget on canvas
        canvas = self.canvas_frame.get_canvas()
        canvas.create_window(x, y, window=widget, anchor="nw")

        # Store reference
        self.grid_widgets[(row, col)] = widget

        # Bind widget events
        widget.bind_action_callback(self._on_widget_action)

    def _initialize_stats_display(self) -> None:
        """Initializes the StatsDisplayFrame with current combobox values."""
        for widget in self.grid_widgets.values():
            initial_value = widget.get_data().get("selected_option")
            if initial_value:
                self.event_bus.publish("grid_value_changed", data={"old_value": None, "new_value": initial_value})

    def _initialize_stats_display(self) -> None:
        """Initializes the StatsDisplayFrame with current combobox values."""
        for widget in self.grid_widgets.values():
            initial_value = widget.get_data().get("selected_option")
            if initial_value:
                self.event_bus.publish("grid_value_changed", data={"old_value": None, "new_value": initial_value})

    def _on_widget_action(
        self, row: int, col: int, action: str, value: str = ""
    ) -> None:
        """Handle actions from grid widgets."""
        print(f"Widget action: ({row}, {col}) - {action}: {value}")

        # Update parent status if available
        if hasattr(self.master, "parent") and hasattr(
            self.master.parent, "update_status"
        ):
            self.master.parent.update_status(f"Grid action: ({row}, {col}) - {action}")

    def get_widget_at(self, row: int, col: int) -> GridCellWidget:
        """Get the widget at the specified grid position."""
        return self.grid_widgets.get((row, col))

    def remove_widget_at(self, row: int, col: int) -> None:
        """Remove the widget at the specified grid position."""
        if (row, col) in self.grid_widgets:
            widget = self.grid_widgets[(row, col)]
            widget.destroy()
            del self.grid_widgets[(row, col)]

    def get_all_widget_data(self) -> Dict[Tuple[int, int], Dict]:
        """Get data from all grid widgets."""
        data = {}
        for pos, widget in self.grid_widgets.items():
            data[pos] = widget.get_data()
        return data
