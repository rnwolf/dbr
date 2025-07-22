"""Tests for Page1 class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.pages.page1 import Page1


class TestPage1:
    """Test cases for Page1."""

    @patch("app.pages.page1.StatsDisplayFrame")
    @patch("app.pages.page1.GridCellWidget")
    @patch("app.pages.page1.ScrollableCanvasFrame")
    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_page_initialization(self, mock_frame_init, mock_label, mock_font, mock_canvas_frame, mock_grid_widget, mock_stats_frame):
        """Test page initialization."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        # Mock the canvas frame methods
        mock_canvas_instance = Mock()
        mock_canvas_instance.get_canvas.return_value = Mock()
        mock_canvas_instance.pack = Mock()
        mock_canvas_frame.return_value = mock_canvas_instance
        
        page = Page1(parent)
        # Add required tkinter attributes to the page object
        page.tk = Mock()
        page._last_child_ids = {}
        page.children = {}

        assert page.grid_rows == 20
        assert page.grid_cols == 15
        assert page.cell_size == 100
        assert isinstance(page.grid_widgets, dict)
        mock_stats_frame.assert_called_once()

    @patch("app.pages.page1.StatsDisplayFrame")
    @patch("app.pages.page1.ScrollableCanvasFrame")
    @patch("app.pages.page1.GridCellWidget")
    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_widget_addition(self, mock_frame_init, mock_label, mock_font, mock_widget, mock_canvas_frame, mock_stats_frame):
        """Test adding widgets to grid."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        
        page = Page1(parent)
        # Add required tkinter attributes to the page object
        page.tk = Mock()
        page._last_child_ids = {}
        page.children = {}

        # Mock canvas frame
        mock_canvas = Mock()
        page.canvas_frame.get_canvas.return_value = mock_canvas
        page.canvas_frame.get_canvas_frame.return_value = Mock()

        # Test adding widget
        page._add_grid_widget(5, 3)

        # Verify widget was created and stored
        assert (5, 3) in page.grid_widgets
        mock_widget.assert_called()
        assert mock_widget.call_args.kwargs["event_bus"] is page.event_bus

    @patch("app.pages.page1.StatsDisplayFrame")
    @patch("app.pages.page1.GridCellWidget")
    @patch("app.pages.page1.ScrollableCanvasFrame")
    @patch("customtkinter.CTkFont")
    @patch("customtkinter.CTkLabel")
    @patch("customtkinter.CTkFrame.__init__", return_value=None)
    def test_widget_action_handling(self, mock_frame_init, mock_label, mock_font, mock_canvas_frame, mock_grid_widget, mock_stats_frame):
        """Test widget action handling."""
        # Create a proper mock parent with required tkinter attributes
        parent = Mock()
        parent._last_child_ids = {}
        parent.tk = Mock()
        parent.children = {}
        parent.parent = Mock()
        parent.parent.update_status = Mock()

        # Mock the canvas frame methods
        mock_canvas_instance = Mock()
        mock_canvas_instance.get_canvas.return_value = Mock()
        mock_canvas_instance.pack = Mock()
        mock_canvas_frame.return_value = mock_canvas_instance

        page = Page1(parent)
        # Add required tkinter attributes to the page object
        page.tk = Mock()
        page._last_child_ids = {}
        page.children = {}
        page.master = parent

        # Test action handling
        page._on_widget_action(2, 3, "test_action", "test_value")

        # Verify status update was called
        parent.parent.update_status.assert_called_with(
            "Grid action: (2, 3) - test_action"
        )
