"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(autouse=True)
def mock_dbrsdk():
    """Mock the entire dbrsdk to prevent import errors and isolate the frontend."""
    with patch.dict(
        "sys.modules",
        {
            "dbrsdk": MagicMock(),
            "dbrsdk.models": MagicMock(),
        },
    ) as mock:
        yield mock


@pytest.fixture
def mocked_main_window_dependencies():
    """Provides a comprehensive set of mocks for all CustomTkinter widgets
    and methods used in the MainWindow, preventing any actual GUI rendering.
    """
    with (
        patch("customtkinter.CTk.__init__", return_value=None),
        patch("customtkinter.CTk.title"),
        patch("customtkinter.CTk.geometry"),
        patch("customtkinter.CTk.minsize"),
        patch("customtkinter.CTk.update_idletasks"),
        patch("customtkinter.CTk.winfo_width", return_value=1280),
        patch("customtkinter.CTk.winfo_height", return_value=720),
        patch("customtkinter.CTk.winfo_screenwidth", return_value=1920),
        patch("customtkinter.CTk.winfo_screenheight", return_value=1080),
        patch("customtkinter.CTk.protocol"),
        patch("customtkinter.CTkFrame") as mock_frame,
        patch("customtkinter.CTkLabel") as mock_label,
        patch("customtkinter.CTkButton") as mock_button,
        patch("customtkinter.CTkFont") as mock_font,
        patch("customtkinter.CTkOptionMenu") as mock_option_menu,
        patch("customtkinter.CTkScrollableFrame") as mock_scrollable_frame,
        patch("frontend.main_window.MenuBar") as mock_menu_bar,
        patch("frontend.main_window.TabNavigation") as mock_tab_navigation,
        patch("frontend.main_window.UserContextWidget") as mock_user_context_widget,
    ):
        yield {
            "CTkFrame": mock_frame,
            "CTkLabel": mock_label,
            "CTkButton": mock_button,
            "CTkFont": mock_font,
            "CTkOptionMenu": mock_option_menu,
            "CTkScrollableFrame": mock_scrollable_frame,
            "MenuBar": mock_menu_bar,
            "TabNavigation": mock_tab_navigation,
            "UserContextWidget": mock_user_context_widget,
        }


@pytest.fixture
def mock_messagebox():
    """Mock messagebox for testing."""
    with patch("tkinter.messagebox") as mock_mb:
        yield mock_mb


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test mode
    os.environ["TESTING"] = "1"
    yield
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
