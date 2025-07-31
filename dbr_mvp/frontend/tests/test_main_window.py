"""Tests for MainWindow class."""

import pytest
from unittest.mock import Mock, patch
import customtkinter
from utils.config import AppConfig


@pytest.fixture
def mock_dbr_service():
    """Create a mock DBR service for testing."""
    service = Mock()
    service.get_user_info.return_value = {"username": "testuser", "display_name": "Test User"}
    service.get_user_role.return_value = "Planner"
    service.get_current_organization.return_value = {"name": "Test Organization"}
    service.get_connection_status.return_value = {
        "backend_url": "http://localhost:8000",
        "backend_healthy": True
    }
    service.is_authenticated.return_value = True
    service.has_permission.return_value = True
    return service




class TestMainWindow:
    """Test cases for MainWindow."""

    def test_window_initialization(self, mock_dbr_service, mocked_main_window_dependencies):
        """Test that MainWindow initializes correctly."""
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)

        assert window is not None
        assert window.dbr_service is mock_dbr_service
        mocked_main_window_dependencies["MenuBar"].assert_called_once()
        mocked_main_window_dependencies["TabNavigation"].assert_called_once()
        assert hasattr(window, "pages")

    def test_role_based_navigation_creation(self, mock_dbr_service, mocked_main_window_dependencies):
        """Test that role-based navigation is created correctly for a Planner."""
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        added_tabs = [
            call.args[0] for call in 
            mocked_main_window_dependencies["TabNavigation"].return_value.add_tab.call_args_list
        ]
        
        expected_tabs = [
            "Work Items", "Collections", "Planning", "Buffer Boards", "Reports"
        ]
        
        assert len(added_tabs) == len(expected_tabs)
        for expected_tab in expected_tabs:
            assert expected_tab in added_tabs, f"Expected tab '{expected_tab}' not found in {added_tabs}"

    def test_user_context_integration(self, mock_dbr_service, mocked_main_window_dependencies):
        """Test that user context is properly integrated."""
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        assert hasattr(window, 'user_context')
        assert hasattr(window, 'header_frame')
        assert hasattr(window, 'logout_button')
        mocked_main_window_dependencies["UserContextWidget"].assert_called_once()

    def test_status_update(self, mock_dbr_service, mocked_main_window_dependencies):
        """Test status bar update."""
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        mock_status_label = window.status_bar
        
        test_message = "Test Status"
        window.update_status(test_message)
        
        mock_status_label.configure.assert_called_with(text=test_message)

    def test_dbr_service_integration(self, mock_dbr_service, mocked_main_window_dependencies):
        """Test that DBR service is properly integrated."""
        from frontend.main_window import MainWindow
        window = MainWindow(mock_dbr_service)
        
        assert window.dbr_service is mock_dbr_service
        
        mock_dbr_service.get_user_info.assert_called()
        mock_dbr_service.get_user_role.assert_called()
        mock_dbr_service.get_current_organization.assert_called()