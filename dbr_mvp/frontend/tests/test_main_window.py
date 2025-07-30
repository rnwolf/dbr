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

@pytest.fixture
def mocked_window(mock_dbr_service):
    """
    Fixture to create a MainWindow instance with its CTk base class
    and other dependencies fully mocked.
    """
    # Mock the dbrsdk import to prevent import errors
    with patch('frontend.dbr_service.Dbrsdk'):
        # Use comprehensive mocking like in role navigation tests
        with patch('frontend.main_window.ctk.CTk') as mock_ctk:
            with patch('frontend.main_window.MenuBar') as mock_menu:
                with patch('frontend.main_window.TabNavigation') as mock_tab_nav:
                    with patch('frontend.main_window.UserContextWidget') as mock_user_widget:
                        with patch('frontend.main_window.ctk.CTkFrame') as mock_frame:
                            with patch('frontend.main_window.ctk.CTkLabel') as mock_label:
                                with patch('frontend.main_window.ctk.CTkButton') as mock_button:
                                    
                                    # Mock the CTk instance and its methods
                                    mock_ctk_instance = Mock()
                                    mock_ctk.return_value = mock_ctk_instance
                                    
                                    # Mock tab navigation instance
                                    mock_tab_nav_instance = Mock()
                                    mock_tab_nav.return_value = mock_tab_nav_instance
                                    
                                    # Mock other components
                                    mock_menu_instance = Mock()
                                    mock_menu.return_value = mock_menu_instance
                                    
                                    mock_user_widget_instance = Mock()
                                    mock_user_widget.return_value = mock_user_widget_instance
                                    
                                    # Import MainWindow after mocking
                                    from frontend.main_window import MainWindow
                                    
                                    # Create window with mocked service
                                    window = MainWindow(mock_dbr_service)
                                    
                                    # Return the instance and mocks
                                    return (
                                        window,
                                        {
                                            "ctk_instance": mock_ctk_instance,
                                            "menu": mock_menu_instance,
                                            "tab_nav": mock_tab_nav_instance,
                                            "user_widget": mock_user_widget_instance,
                                        },
                                    )


class TestMainWindow:
    """Test cases for MainWindow."""

    def test_window_initialization(self, mocked_window):
        """Test that MainWindow initializes correctly."""
        window, mocks = mocked_window

        # Test that MainWindow was created successfully
        assert window is not None
        assert hasattr(window, 'dbr_service')

        # Test that components were created
        assert hasattr(window, "menu_bar")
        assert hasattr(window, "tab_navigation") 
        assert hasattr(window, "pages")  # Role-based pages

        # Test that role-based navigation was set up
        mocks["tab_nav"].add_tab.assert_called()
        
        # Verify tabs were added (Planner role should have 5 tabs)
        expected_tab_count = 5  # Work Items, Collections, Planning, Buffer Boards, Reports
        assert mocks["tab_nav"].add_tab.call_count == expected_tab_count

    def test_role_based_navigation_creation(self, mocked_window):
        """Test that role-based navigation is created correctly."""
        window, mocks = mocked_window
        
        # Get the tabs that were added
        added_tabs = [call[0][0] for call in mocks["tab_nav"].add_tab.call_args_list]
        
        # For Planner role, should have these tabs
        expected_tabs = ["Work Items", "Collections", "Planning", "Buffer Boards", "Reports"]
        
        for expected_tab in expected_tabs:
            assert expected_tab in added_tabs, f"Expected tab '{expected_tab}' not found"

    def test_user_context_integration(self, mocked_window):
        """Test that user context is properly integrated."""
        window, mocks = mocked_window
        
        # Verify that user context widget was created and stored
        assert hasattr(window, 'user_context')
        
        # Verify that header frame was created (which contains the user context)
        assert hasattr(window, 'header_frame')
        
        # Verify that logout button was created
        assert hasattr(window, 'logout_button')
        
        # This confirms the user context header was properly set up

    def test_status_update(self, mock_dbr_service):
        """Test status bar update."""
        # Use the same comprehensive mocking pattern as other tests
        with patch('frontend.dbr_service.Dbrsdk'):
            with patch('frontend.main_window.ctk.CTk') as mock_ctk:
                with patch('frontend.main_window.MenuBar'), patch('frontend.main_window.TabNavigation'):
                    with patch('frontend.main_window.UserContextWidget'), patch('frontend.main_window.ctk.CTkFrame'):
                        with patch('frontend.main_window.ctk.CTkLabel'), patch('frontend.main_window.ctk.CTkButton'):
                            mock_ctk.return_value = Mock()
                            
                            from frontend.main_window import MainWindow
                            window = MainWindow(mock_dbr_service)
                            
                            # Mock the status bar
                            window.status_bar = Mock()
                            
                            # Test status update
                            test_message = "Test Status"
                            window.update_status(test_message)
                            
                            window.status_bar.configure.assert_called_with(text=test_message)

    def test_dbr_service_integration(self, mocked_window, mock_dbr_service):
        """Test that DBR service is properly integrated."""
        window, _ = mocked_window
        
        # Verify the service is stored
        assert window.dbr_service == mock_dbr_service
        
        # Verify service methods were called during initialization
        mock_dbr_service.get_user_info.assert_called()
        mock_dbr_service.get_user_role.assert_called()
        mock_dbr_service.get_current_organization.assert_called()