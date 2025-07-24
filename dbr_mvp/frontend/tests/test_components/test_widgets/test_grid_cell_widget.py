"""Tests for GridCellWidget class."""

from unittest.mock import Mock, patch
from frontend.components.widgets.grid_cell_widget import GridCellWidget
from frontend.utils.event_bus import EventBus


class TestGridCellWidget:
    """Test cases for GridCellWidget."""

    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_widget_initialization(self, mock_frame_init, mock_button, mock_label, mock_combo, mock_font):
        """Test widget initialization."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        event_bus = EventBus()
        
        widget = GridCellWidget(parent, row=5, col=3, event_bus=event_bus)

        assert widget.row == 5
        assert widget.col == 3
        assert widget.event_bus is event_bus
        assert widget._data["row"] == 5
        assert widget._data["col"] == 3
        assert widget._data["button_clicks"] == 0
        assert widget._data["selected_option"] == "Option 1"

    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_button_click_handling(self, mock_frame_init, mock_button, mock_label, mock_combo, mock_font):
        """Test button click functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        widget = GridCellWidget(parent, row=2, col=4)

        # Mock the button
        widget.action_button = Mock()

        # Test button click
        widget._on_button_click()

        assert widget._data["button_clicks"] == 1
        widget.action_button.configure.assert_called_with(text="Click 1")

    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_combo_change_handling_and_event_publishing(self, mock_frame_init, mock_button, mock_label, mock_combo, mock_font):
        """Test combobox change functionality and event publishing."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        event_bus = Mock(spec=EventBus)
        
        widget = GridCellWidget(parent, row=1, col=1, event_bus=event_bus)
        initial_value = widget._data["selected_option"]

        # Test combo change
        new_value = "Option 3"
        widget._on_combo_change(new_value)

        assert widget._data["selected_option"] == new_value
        event_bus.publish.assert_called_once_with(
            "grid_value_changed",
            data={"old_value": initial_value, "new_value": new_value}
        )

    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_action_callback(self, mock_frame_init, mock_button, mock_label, mock_combo, mock_font):
        """Test action callback functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        widget = GridCellWidget(parent, row=0, col=0)

        callback = Mock()
        widget.bind_action_callback(callback)

        # Mock button for click test
        widget.action_button = Mock()

        # Test button click callback
        widget._on_button_click()
        callback.assert_called_with(0, 0, "button_click", "1")

        # Test combo change callback
        widget._on_combo_change("Option 2")
        callback.assert_called_with(0, 0, "combo_change", "Option 2")

    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkComboBox")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_data_management(self, mock_frame_init, mock_button, mock_label, mock_combo, mock_font):
        """Test data get/set functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        widget = GridCellWidget(parent, row=1, col=2)

        # Mock widgets for set_data test
        widget.action_button = Mock()
        widget.option_combo = Mock()

        # Test getting data
        data = widget.get_data()
        expected = {
            "row": 1,
            "col": 2,
            "button_clicks": 0,
            "selected_option": "Option 1",
        }
        assert data == expected

        # Test setting data
        new_data = {"button_clicks": 5, "selected_option": "Option 4"}
        widget.set_data(new_data)

        assert widget._data["button_clicks"] == 5
        assert widget._data["selected_option"] == "Option 4"
        widget.action_button.configure.assert_called_with(text="Click 5")
        widget.option_combo.set.assert_called_with("Option 4")
