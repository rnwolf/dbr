"""Tests for DBR application startup sequence."""

import pytest
from unittest.mock import Mock, patch
import customtkinter


@pytest.fixture
def mocked_window(mocker):
    """
    Fixture to create a MainWindow instance with its CTk base class
    and other dependencies fully mocked.
    """
    # Mock the dbrsdk import at the module level first
    mocker.patch("dbrsdk.Dbrsdk")

    # Mock UserContextWidget before any imports
    mocker.patch("frontend.authentication_ui.UserContextWidget")

    # Mock the DBR service
    mock_dbr_service = mocker.patch("frontend.dbr_service.DBRService")
    mock_service_instance = mock_dbr_service.return_value
    mock_service_instance.get_user_info.return_value = {"username": "testuser"}
    mock_service_instance.get_user_role.return_value = "Planner"
    mock_service_instance.get_current_organization.return_value = {"name": "Test Org"}
    mock_service_instance.get_connection_status.return_value = {
        "backend_url": "http://localhost:8000",
        "backend_healthy": True,
    }

    # Mock CustomTkinter components
    mocker.patch.object(customtkinter.CTk, "__init__", return_value=None)
    mock_title = mocker.patch.object(customtkinter.CTk, "title")
    mock_geometry = mocker.patch.object(customtkinter.CTk, "geometry")
    mock_minsize = mocker.patch.object(customtkinter.CTk, "minsize")
    mock_protocol = mocker.patch.object(customtkinter.CTk, "protocol")

    # Mock all UI components used in MainWindow
    mocker.patch("frontend.main_window.MenuBar", autospec=True)
    mock_tab_navigation = mocker.patch(
        "frontend.main_window.TabNavigation", autospec=True
    )
    mock_tab_navigation.return_value.content_frame = mocker.Mock()
    mocker.patch("frontend.main_window.Page1", autospec=True)
    mocker.patch("frontend.main_window.Page2", autospec=True)
    mocker.patch("frontend.main_window.ctk.CTkLabel", autospec=True)
    mocker.patch("frontend.main_window.ctk.CTkFrame", autospec=True)
    mocker.patch("frontend.main_window.ctk.CTkButton", autospec=True)

    # Import after mocking
    from frontend.main_window import MainWindow

    with patch.object(MainWindow, "_center_window") as mock_center:
        window = MainWindow(mock_service_instance)

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
        from utils.config import AppConfig

        _, mocks = mocked_window
        mocks["title"].assert_called_with(AppConfig.WINDOW_TITLE)

    @patch("main.MainWindow")
    @patch("main.BackendConfigDialog")
    @patch("main.AuthenticationManager")
    def test_startup_sequence_and_health_check(
        self, mock_auth_manager, mock_backend_dialog, mock_main_window
    ):
        """Tests the startup sequence including the health check."""
        import main as app_main

        # Arrange
        mock_dialog_instance = mock_backend_dialog.return_value
        mock_dialog_instance.get_url.return_value = "http://127.0.0.1:8000"

        # Mock authentication manager
        mock_auth_instance = mock_auth_manager.return_value
        mock_service_instance = Mock()
        mock_service_instance.health_check.return_value = True
        mock_auth_instance.authenticate.return_value = mock_service_instance

        mock_main_window.return_value.run = Mock()

        # Act
        app_main.main()

        # Assert
        mock_backend_dialog.assert_called_once()
        mock_auth_manager.assert_called_once_with("http://127.0.0.1:8000")
        mock_auth_instance.authenticate.assert_called_once()
        mock_main_window.assert_called_once_with(mock_service_instance)
        mock_main_window.return_value.run.assert_called_once()
