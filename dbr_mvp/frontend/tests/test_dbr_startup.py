"""Tests for DBR application startup sequence."""

import pytest
from unittest.mock import Mock, patch
import customtkinter

from frontend.main_window import MainWindow
from utils.config import AppConfig


@pytest.fixture
def mocked_window(mocker):
    """
    Fixture to create a MainWindow instance with its CTk base class
    and other dependencies fully mocked.
    """
    mocker.patch.object(customtkinter.CTk, "__init__", return_value=None)

    mock_title = mocker.patch.object(customtkinter.CTk, "title")
    mock_geometry = mocker.patch.object(customtkinter.CTk, "geometry")
    mock_minsize = mocker.patch.object(customtkinter.CTk, "minsize")
    mock_protocol = mocker.patch.object(customtkinter.CTk, "protocol")

    mocker.patch("frontend.main_window.MenuBar", autospec=True)
    mocker.patch("frontend.main_window.TabNavigation", autospec=True)
    mocker.patch("frontend.main_window.Page1", autospec=True)
    mocker.patch("frontend.main_window.Page2", autospec=True)
    mocker.patch("frontend.main_window.ctk.CTkLabel", autospec=True)

    with patch.object(MainWindow, "_center_window") as mock_center:
        window = MainWindow()

    return window, {
        "title": mock_title,
        "geometry": mock_geometry,
        "minsize": mock_minsize,
        "protocol": mock_protocol,
        "center": mock_center,
    }


class TestDbrStartup:
    """Test cases for DBR application startup."""

    def test_application_branding(self, mocked_window):
        """Test that MainWindow is correctly branded."""
        _, mocks = mocked_window
        mocks["title"].assert_called_with("DBR Buffer Management System")

    @patch('main.MainWindow')
    @patch('main.BackendConfigDialog')
    @patch('main.DBRService')
    def test_startup_sequence_shows_config_dialog(self, mock_dbr_service, mock_backend_dialog, mock_main_window):
        """
        Tests that the main application entry point shows the backend config dialog
        and, upon successful configuration, launches the main window.
        """
        import main as app_main

        # Mock the dialog to simulate a successful configuration
        mock_dialog_instance = mock_backend_dialog.return_value
        mock_dialog_instance.get_url.return_value = "http://127.0.0.1:8000"

        # Mock the service to simulate a successful health check
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.health_check.return_value = True

        # To make main() testable without blocking, we'll patch the run method
        mock_main_window.return_value.run = Mock()

        # Act
        app_main.main()

        # Assert
        mock_backend_dialog.assert_called_once()
        mock_dbr_service.assert_called_once_with("http://127.0.0.1:8000")
        mock_service_instance.health_check.assert_called_once()
        mock_main_window.assert_called_once()
        mock_main_window.return_value.run.assert_called_once()

    @patch('main.MainWindow')
    @patch('main.BackendConfigDialog')
    @patch('main.DBRService')
    def test_health_check_after_config(self, mock_dbr_service, mock_backend_dialog, mock_main_window):
        """Tests that a health check is performed after URL configuration."""
        import main as app_main

        # Arrange: Mock the dialog and service layer
        mock_dialog_instance = mock_backend_dialog.return_value
        mock_dialog_instance.get_url.return_value = "http://127.0.0.1:8000"

        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.health_check.return_value = True

        # Act
        app_main.main()

        # Assert
        mock_dbr_service.assert_called_once_with("http://127.0.0.1:8000")
        mock_service_instance.health_check.assert_called_once()
        mock_main_window.assert_called_once()
