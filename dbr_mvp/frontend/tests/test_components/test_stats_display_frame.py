import pytest
from unittest.mock import Mock, patch
from collections import Counter
from frontend.components.stats_display_frame import StatsDisplayFrame
from frontend.components.widgets.grid_cell_widget import GridCellWidget
from frontend.utils.event_bus import EventBus


@pytest.fixture
def mock_event_bus():
    return Mock(spec=EventBus)


@pytest.fixture
def stats_frame(mock_event_bus):
    # Mock the CTk parent to avoid tkinter initialization
    with (
        patch("customtkinter.CTk"),
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkLabel") as mock_label,
    ):
        mock_parent = Mock()
        mock_parent._last_child_ids = {}
        mock_parent.tk = Mock()
        mock_parent.children = {}
        mock_parent._w = "mock_window"

        # Create mock label instance with dynamic text behavior
        mock_label_instance = Mock()
        mock_label_instance.pack = Mock()
        mock_label_instance.configure = Mock()
        mock_label_instance._text = "No selections yet."

        def mock_cget(key):
            if key == "text":
                return mock_label_instance._text
            return ""

        def mock_configure(**kwargs):
            if "text" in kwargs:
                mock_label_instance._text = kwargs["text"]

        mock_label_instance.cget = Mock(side_effect=mock_cget)
        mock_label_instance.configure = Mock(side_effect=mock_configure)
        mock_label.return_value = mock_label_instance

        frame = StatsDisplayFrame(mock_parent, mock_event_bus)
        frame.stats_label = mock_label_instance
        # Add required tkinter attributes to frame
        frame._w = "mock_frame"
        frame.tk = Mock()
        frame._last_child_ids = {}
        frame.children = {}
        yield frame


@pytest.fixture
def grid_cell_widget(mock_event_bus):
    # Mock the CTk parent and all tkinter components to avoid initialization
    with (
        patch("customtkinter.CTkFrame.__init__", return_value=None),
        patch("customtkinter.CTkComboBox") as mock_combo,
        patch("customtkinter.CTkButton") as mock_button,
        patch("customtkinter.CTkLabel") as mock_label,
        patch("customtkinter.CTkFont") as mock_font,
    ):
        mock_parent = Mock()
        mock_parent._last_child_ids = {}
        mock_parent.tk = Mock()
        mock_parent.children = {}
        mock_parent._w = "mock_canvas"

        # Mock font to avoid tkinter font initialization
        mock_font.return_value = Mock()

        # Create mock instances
        mock_combo_instance = Mock()
        mock_combo_instance.pack = Mock()
        mock_combo_instance.get = Mock(return_value="Option 1")
        mock_combo_instance.set = Mock()
        mock_combo.return_value = mock_combo_instance

        mock_button_instance = Mock()
        mock_button_instance.pack = Mock()
        mock_button.return_value = mock_button_instance

        mock_label_instance = Mock()
        mock_label_instance.pack = Mock()
        mock_label.return_value = mock_label_instance

        widget = GridCellWidget(mock_parent, row=0, col=0, event_bus=mock_event_bus)
        widget.option_combo = mock_combo_instance
        widget.action_button = mock_button_instance
        widget.coords_label = mock_label_instance
        # Add required tkinter attributes
        widget._w = "mock_widget"
        widget.tk = Mock()
        widget._last_child_ids = {}
        widget.children = {}
        yield widget


class TestStatsDisplayFrame:
    def test_initialization_and_subscription(self, stats_frame, mock_event_bus):
        mock_event_bus.subscribe.assert_called_once_with(
            "grid_value_changed", stats_frame.handle_grid_update
        )
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
        stats_frame.stats_label._text = stats_frame._format_stats()

        # Change from Option 1 to Option 2
        data = {"old_value": "Option 1", "new_value": "Option 2"}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 2": 1' in stats_frame.stats_label.cget("text")
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_increment_value(self, stats_frame):
        # Initial state
        stats_frame.stats = Counter({"Option 1": 1})
        stats_frame.stats_label._text = stats_frame._format_stats()

        # Add another Option 1
        data = {"old_value": None, "new_value": "Option 1"}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 1": 2}
        assert '"Option 1": 2' in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_remove_value(self, stats_frame):
        # Initial state
        stats_frame.stats = Counter({"Option 1": 1, "Option 2": 1})
        stats_frame.stats_label._text = stats_frame._format_stats()

        # Remove Option 1
        data = {"old_value": "Option 1", "new_value": None}
        stats_frame.handle_grid_update(data)
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")

    def test_handle_grid_update_multiple_changes(self, stats_frame):
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option A"})
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option B"})
        stats_frame.handle_grid_update({"old_value": None, "new_value": "Option A"})
        stats_frame.handle_grid_update(
            {"old_value": "Option B", "new_value": "Option C"}
        )

        assert stats_frame.stats == {"Option A": 2, "Option C": 1}
        assert '"Option A": 2' in stats_frame.stats_label.cget("text")
        assert '"Option C": 1' in stats_frame.stats_label.cget("text")
        assert '"Option B"' not in stats_frame.stats_label.cget("text")

    def test_integration_grid_cell_to_stats_frame(
        self, stats_frame, grid_cell_widget, mock_event_bus
    ):
        # Simulate initial state from Page1's _initialize_stats_display
        mock_event_bus.publish(
            "grid_value_changed", data={"old_value": None, "new_value": "Option 1"}
        )
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
        stats_frame.handle_grid_update(
            {"old_value": "Option 1", "new_value": "Option 2"}
        )
        assert stats_frame.stats == {"Option 2": 1}
        assert '"Option 2": 1' in stats_frame.stats_label.cget("text")
        assert '"Option 1"' not in stats_frame.stats_label.cget("text")
