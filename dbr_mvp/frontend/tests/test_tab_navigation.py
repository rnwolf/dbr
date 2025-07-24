"""Tests for TabNavigation class."""

from unittest.mock import Mock, patch
from frontend.tab_navigation import TabNavigation


class TestTabNavigation:
    """Test cases for TabNavigation."""

    @patch("frontend.tab_navigation.TabNavigation._setup_navigation")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_tab_creation(self, mock_frame_init, mock_button, mock_setup_nav):
        """Test tab creation and management."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        parent._w = "mock_window"
        
        # Create mock button instance
        mock_button_instance = Mock()
        mock_button_instance.pack = Mock()
        mock_button_instance.configure = Mock()
        mock_button.return_value = mock_button_instance
        
        tab_nav = TabNavigation(parent)
        
        # Manually set up the frame attributes since _setup_navigation is mocked
        tab_nav.tab_button_frame = Mock()
        tab_nav.content_frame = Mock()

        # Create mock tab content
        mock_content = Mock()
        mock_content.place = Mock()
        mock_content.place_forget = Mock()
        
        tab_nav.add_tab("Test Tab", mock_content)

        assert "Test Tab" in tab_nav._tabs
        assert "Test Tab" in tab_nav._tab_buttons
        assert tab_nav.get_active_tab_name() == "Test Tab"

    @patch("frontend.tab_navigation.TabNavigation._setup_navigation")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_tab_switching(self, mock_frame_init, mock_button, mock_setup_nav):
        """Test tab switching functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        parent._w = "mock_window"
        
        # Create mock button instance
        mock_button_instance = Mock()
        mock_button_instance.pack = Mock()
        mock_button_instance.configure = Mock()
        mock_button.return_value = mock_button_instance
        
        tab_nav = TabNavigation(parent)
        
        # Manually set up the frame attributes since _setup_navigation is mocked
        tab_nav.tab_button_frame = Mock()
        tab_nav.content_frame = Mock()

        # Add multiple tabs
        content1 = Mock()
        content1.place = Mock()
        content1.place_forget = Mock()
        content2 = Mock()
        content2.place = Mock()
        content2.place_forget = Mock()
        
        tab_nav.add_tab("Tab 1", content1)
        tab_nav.add_tab("Tab 2", content2)

        # Test switching
        tab_nav._switch_tab("Tab 2")
        assert tab_nav.get_active_tab_name() == "Tab 2"

    @patch("frontend.tab_navigation.TabNavigation._setup_navigation")
    @patch("customtkinter.CTkButton")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_tab_change_callback(self, mock_frame_init, mock_button, mock_setup_nav):
        """Test tab change callback functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        parent._w = "mock_window"
        
        # Create mock button instance
        mock_button_instance = Mock()
        mock_button_instance.pack = Mock()
        mock_button_instance.configure = Mock()
        mock_button.return_value = mock_button_instance
        
        tab_nav = TabNavigation(parent)
        
        # Manually set up the frame attributes since _setup_navigation is mocked
        tab_nav.tab_button_frame = Mock()
        tab_nav.content_frame = Mock()

        callback = Mock()
        tab_nav.bind_tab_change(callback)

        content = Mock()
        content.place = Mock()
        content.place_forget = Mock()
        
        tab_nav.add_tab("Test Tab", content)

        # Callback should be called when tab is added (auto-activated)
        callback.assert_called_with("Test Tab")
