import pytest
from unittest.mock import Mock
import customtkinter as ctk
from collections import Counter
from app.components.stats_display_frame import StatsDisplayFrame
from app.components.widgets.grid_cell_widget import GridCellWidget
from app.utils.event_bus import EventBus


@pytest.fixture
def mock_event_bus():
    return Mock(spec=EventBus)


@pytest.fixture
def stats_frame(mock_event_bus):
    # Create a dummy CTk object for parent
    root = ctk.CTk()
    frame = StatsDisplayFrame(root, mock_event_bus)
    yield frame
    root.destroy()


@pytest.fixture
def grid_cell_widget(mock_event_bus):
    # Create a dummy CTk object for parent
    root = ctk.CTk()
    widget = GridCellWidget(root, row=0, col=0, event_bus=mock_event_bus)
    yield widget
    root.destroy()


class TestStatsDisplayFrame:
    def test_initialization_and_subscription(self, stats_frame, mock_event_bus):
        mock_event_bus.subscribe.assert_called_once_with("grid_value_changed", stats_frame.handle_grid_update)
        assert stats_frame.stats == {}
        assert "No selections yet." in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_add_new_value(self, stats_frame):
        data = {"old_value": None, "new_value": "Option 1"}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 1": 1}
        assert '"Option 1": 1' in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_change_value(self, stats_frame):
        # Initial state
        stats_frame.stats = Counter({"Option 1": 1})
        stats_frame.stats_label.configure(text=stats_frame._format_stats())

        # Change from Option 1 to Option 2
        data = {"old_value": "Option 1", "new_value": "Option 2"}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 2": 1' in stats_frame.stats_label.cget("text")
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_increment_value(self, stats_frame):
        # Initial state
        stats_frame.stats = {"Option 1": 1}
        stats_frame.stats_label.configure(text=stats_frame._format_stats())

        # Add another Option 1
        data = {"old_value": None, "new_value": "Option 1"}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 1": 2}
        assert '"Option 1": 2' in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_remove_value(self, stats_frame):
        # Initial state
        stats_frame.stats = {"Option 1": 1, "Option 2": 1}
        stats_frame.stats_label.configure(text=stats_frame._format_stats())

        # Remove Option 1
        data = {"old_value": "Option 1", "new_value": None}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_multiple_changes(self, stats_frame):
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option A"})
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option B"})
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option A"})
        stats_frame.handle_grid_update({"old_value": "Option B", "new_value": "Option C"})

        assert stats_frame.stats == {"Option A": 2, "Option C": 1}
        assert '"Option A": 2' in stats_frame.stats_label.cget("text")
        assert '"Option C": 1' in stats_frame.stats_label.cget("text")
        assert '"Option B"' not in stats_frame.stats_label.cget("text")

    def test_integration_grid_cell_to_stats_frame(self, stats_frame, grid_cell_widget, mock_event_bus):
        # Simulate initial state from Page1's _initialize_stats_display
        mock_event_bus.publish("grid_value_changed", data={"old_value": None, "new_value": "Option 1"})
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option 1"})
        assert stats_frame.stats == {"Option 1": 1}

        # Simulate a combobox change in GridCellWidget
        grid_cell_widget._on_combo_change("Option 2")

        # Verify that the event bus was called with the correct data
        mock_event_bus.publish.assert_called_with(
            "grid_value_changed",
            data={"old_value": "Option 1", "new_value": "Option 2"},
        )

        # Manually call handle_grid_update as it would be called by the event bus
        stats_frame.handle_grid_update({"old_value": "Option 1", "new_value": "Option 2"})
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 2": 1' in stats_frame.stats_label.cget("text")
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")