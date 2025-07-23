"""Custom widget for grid cells containing button, label, and combobox."""

import customtkinter as ctk
from typing import Callable, Optional, Dict, Any

from app.utils.event_bus import EventBus


class GridCellWidget(ctk.CTkFrame):
    """Custom widget for grid cells with button, coordinates label, and combobox."""

    def __init__(
        self,
        parent,
        row: int,
        col: int,
        width: int = 90,
        height: int = 90,
        event_bus: Optional[EventBus] = None,
        **kwargs,
    ):
        super().__init__(parent, width=width, height=height, **kwargs)

        self.row = row
        self.col = col
        self.event_bus = event_bus
        self.action_callback: Optional[Callable[[int, int, str, str], None]] = None

        # Data storage
        self._data: Dict[str, Any] = {
            "row": row,
            "col": col,
            "button_clicks": 0,
            "selected_option": "Option 1",
        }

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """Create all widgets for the grid cell."""
        # Action button
        self.action_button = ctk.CTkButton(
            self,
            text="Action",
            command=self._on_button_click,
            width=70,
            height=25,
            font=ctk.CTkFont(size=10),
        )

        # Coordinates label
        self.coords_label = ctk.CTkLabel(
            self,
            text=f"({self.row}, {self.col})",
            font=ctk.CTkFont(size=9),
            width=70,
            height=15,
        )

        # Dropdown combobox
        self.option_combo = ctk.CTkComboBox(
            self,
            values=["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
            command=self._on_combo_change,
            width=70,
            height=25,
            font=ctk.CTkFont(size=9),
            dropdown_font=ctk.CTkFont(size=9),
        )
        self.option_combo.set("Option 1")

    def _setup_layout(self) -> None:
        """Setup the layout of widgets within the cell."""
        # Pack widgets vertically with minimal spacing
        self.action_button.pack(pady=(5, 2))
        self.coords_label.pack(pady=1)
        self.option_combo.pack(pady=(2, 5))

    def _on_button_click(self) -> None:
        """Handle button click events."""
        self._data["button_clicks"] += 1

        # Update button text to show click count
        self.action_button.configure(text=f"Click {self._data['button_clicks']}")

        # Call callback if set
        if self.action_callback:
            self.action_callback(
                self.row, self.col, "button_click", str(self._data["button_clicks"])
            )

    def _on_combo_change(self, selected_value: str) -> None:
        """Handle combobox selection changes."""
        old_value = self._data["selected_option"]
        self._data["selected_option"] = selected_value

        if self.event_bus:
            self.event_bus.publish(
                "grid_value_changed",
                data={"old_value": old_value, "new_value": selected_value},
            )

        # Call callback if set
        if self.action_callback:
            self.action_callback(self.row, self.col, "combo_change", selected_value)

    def bind_action_callback(
        self, callback: Callable[[int, int, str, str], None]
    ) -> None:
        """Bind a callback for widget actions."""
        self.action_callback = callback

    def get_data(self) -> Dict[str, Any]:
        """Get the current data from this widget."""
        return self._data.copy()

    def set_data(self, data: Dict[str, Any]) -> None:
        """Set data for this widget."""
        if "button_clicks" in data:
            self._data["button_clicks"] = data["button_clicks"]
            self.action_button.configure(text=f"Click {self._data['button_clicks']}")

        if "selected_option" in data:
            self._data["selected_option"] = data["selected_option"]
            self.option_combo.set(data["selected_option"])

    def reset(self) -> None:
        """Reset the widget to its initial state."""
        self._data["button_clicks"] = 0
        self._data["selected_option"] = "Option 1"
        self.action_button.configure(text="Action")
        self.option_combo.set("Option 1")

    def highlight(self, highlight: bool = True) -> None:
        """Highlight or unhighlight the widget."""
        if highlight:
            self.configure(border_color="orange", border_width=2)
        else:
            self.configure(border_color="gray", border_width=1)
