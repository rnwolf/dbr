"""Tests for MainWindow class."""

import pytest
from unittest.mock import Mock, patch
import customtkinter

# Import after setting up mocks if necessary, or patch where used.
from app.main_window import MainWindow
from utils.config import AppConfig


@pytest.fixture
def mocked_window(mocker):
    """
    Fixture to create a MainWindow instance with its CTk base class
    and other dependencies fully mocked.
    """
    # Prevent the TclError by mocking the base class's __init__
    mocker.patch.object(customtkinter.CTk, "__init__", return_value=None)

    # Mock the methods from the base class that are called by MainWindow
    mock_title = mocker.patch.object(customtkinter.CTk, "title")
    mock_geometry = mocker.patch.object(customtkinter.CTk, "geometry")
    mock_minsize = mocker.patch.object(customtkinter.CTk, "minsize")
    mock_protocol = mocker.patch.object(customtkinter.CTk, "protocol")
    mock_quit = mocker.patch.object(customtkinter.CTk, "quit")
    mock_destroy = mocker.patch.object(customtkinter.CTk, "destroy")

    # Mock other dependencies used within MainWindow
    mocker.patch("app.main_window.MenuBar", autospec=True)
    mocker.patch("app.main_window.TabNavigation", autospec=True)
    mocker.patch("app.main_window.Page1", autospec=True)
    mocker.patch("app.main_window.Page2", autospec=True)
    mocker.patch("app.main_window.ctk.CTkLabel", autospec=True)

    # Patch _center_window as it tries to do GUI work
    with patch.object(MainWindow, "_center_window") as mock_center:
        window = MainWindow()

    # Return the instance and a dictionary of the mocks for easy access
    return (
        window,
        {
            "title": mock_title,
            "geometry": mock_geometry,
            "minsize": mock_minsize,
            "protocol": mock_protocol,
            "quit": mock_quit,
            "destroy": mock_destroy,
            "center": mock_center,
        },
    )


class TestMainWindow:
    """Test cases for MainWindow."""

    def test_window_initialization(self, mocked_window):
        """Test that MainWindow initializes correctly."""
        window, mocks = mocked_window

        # Test _setup_window calls
        mocks["title"].assert_called_with(AppConfig.WINDOW_TITLE)
        mocks["geometry"].assert_called_with(
            f"{AppConfig.WINDOW_SIZE[0]}x{AppConfig.WINDOW_SIZE[1]}"
        )
        mocks["minsize"].assert_called_with(*AppConfig.MIN_WINDOW_SIZE)
        mocks["center"].assert_called_once()

        # Test _create_widgets calls
        assert hasattr(window, "menu_bar")
        assert hasattr(window, "tab_navigation")
        assert hasattr(window, "status_bar")

        # Test _setup_layout calls
        window.menu_bar.pack.assert_called_once()
        window.tab_navigation.pack.assert_called_once()
        window.status_bar.pack.assert_called_once()

        # Test _bind_events calls
        mocks["protocol"].assert_called_with("WM_DELETE_WINDOW", window._on_closing)
        window.tab_navigation.bind_tab_change.assert_called_once()

    def test_status_update(self, mocked_window):
        """Test status bar update."""
        window, _ = mocked_window
        window.status_bar = Mock()  # Replace the auto-mock with a simple one

        test_message = "Test Status"
        window.update_status(test_message)

        window.status_bar.configure.assert_called_with(text=test_message)

    def test_on_closing(self, mocked_window):
        """Test window closing behavior."""
        window, mocks = mocked_window

        window._on_closing()

        mocks["quit"].assert_called_once()
        mocks["destroy"].assert_called_once()