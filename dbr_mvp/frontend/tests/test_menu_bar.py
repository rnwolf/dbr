"""Tests for MenuBar class."""

from unittest.mock import Mock, patch
from frontend.menu_bar import MenuBar


class TestMenuBar:
    """Test cases for MenuBar."""

    @patch("customtkinter.CTkOptionMenu")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_menu_creation(self, mock_frame_init, mock_option_menu):
        """Test menu creation."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        menu_bar = MenuBar(parent)

        # Verify menus are created
        assert hasattr(menu_bar, "file_menu")
        assert hasattr(menu_bar, "edit_menu")
        assert hasattr(menu_bar, "view_menu")
        assert hasattr(menu_bar, "help_menu")

    @patch("customtkinter.CTkOptionMenu")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_file_menu_items(self, mock_frame_init, mock_option_menu):
        """Test file menu items."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        menu_bar = MenuBar(parent)

        file_items = menu_bar._get_file_menu_items()
        expected_items = ["New", "Open", "Save", "Exit"]

        assert all(item in file_items for item in expected_items)

    @patch("customtkinter.CTkOptionMenu")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    @patch("customtkinter.set_appearance_mode")
    @patch("customtkinter.get_appearance_mode", return_value="dark")
    def test_toggle_theme(self, mock_get_mode, mock_set_mode, mock_frame_init, mock_option_menu):
        """Test theme toggle functionality."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        menu_bar = MenuBar(parent)

        menu_bar._view_toggle_theme()

        mock_set_mode.assert_called_with("light")
