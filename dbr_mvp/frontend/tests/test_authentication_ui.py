"""Tests for the Authentication UI components."""

import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk


class TestLoginDialog:
    """Test cases for the LoginDialog."""

    @patch('frontend.authentication_ui.DBRService')
    def test_login_dialog_initialization(self, mock_dbr_service):
        """Test login dialog initializes correctly."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange & Act
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Assert
        assert dialog.backend_url == "http://localhost:8000"
        assert dialog.result is None
        assert dialog.user_info is None

    @patch('frontend.authentication_ui.DBRService')
    def test_login_dialog_with_test_users(self, mock_dbr_service):
        """Test login dialog with actual test credentials."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = True
        mock_service_instance.get_user_info.return_value = {
            "username": "admin", "role": "Super Admin"
        }
        mock_service_instance.get_current_organization.return_value = {
            "name": "Default Organization"
        }
        
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Act - Simulate successful login
        result = dialog._attempt_login("admin", "admin123")
        
        # Assert
        assert result is True
        mock_service_instance.login.assert_called_once_with("admin", "admin123")

    @patch('frontend.authentication_ui.DBRService')
    def test_login_dialog_invalid_credentials(self, mock_dbr_service):
        """Test login dialog handles invalid credentials."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = False
        
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Act
        result = dialog._attempt_login("invalid", "invalid")
        
        # Assert
        assert result is False
        mock_service_instance.login.assert_called_once_with("invalid", "invalid")

    @patch('frontend.authentication_ui.DBRService')
    def test_role_detection_and_caching(self, mock_dbr_service):
        """Test role detection from login response."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = True
        mock_service_instance.get_user_info.return_value = {
            "id": "123", "username": "planner", "display_name": "Planner User"
        }
        mock_service_instance.get_user_role.return_value = "Planner"
        mock_service_instance.get_current_organization.return_value = {
            "id": "org-1", "name": "Default Organization"
        }
        
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Act
        success = dialog._attempt_login("planner", "planner123")
        
        # Assert
        assert success is True
        assert dialog.user_info is not None
        assert dialog.user_info["username"] == "planner"

    @patch('frontend.authentication_ui.DBRService')
    def test_session_persistence_setup(self, mock_dbr_service):
        """Test session management setup."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.login.return_value = True
        mock_service_instance.get_token.return_value = "test_token_123"
        mock_service_instance.get_user_info.return_value = {"username": "admin"}
        
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Act
        success = dialog._attempt_login("admin", "admin123")
        
        # Assert
        assert success is True
        # Verify service is stored for session management
        assert dialog.dbr_service is not None


class TestUserContextDisplay:
    """Test cases for user context display components."""

    def test_user_context_widget_creation(self):
        """Test user context widget displays correctly."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import UserContextWidget
        
        # Arrange
        root = ctk.CTk()
        user_info = {
            "username": "admin",
            "display_name": "Admin User",
            "email": "admin@example.com"
        }
        
        # Act
        widget = UserContextWidget(root, user_info, "Super Admin", "Default Organization")
        
        # Assert
        assert widget.user_info == user_info
        assert widget.user_role == "Super Admin"
        assert widget.organization_name == "Default Organization"
        
        # Cleanup
        root.destroy()

    def test_user_context_display_formatting(self):
        """Test user context displays formatted information."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import UserContextWidget
        
        # Arrange
        root = ctk.CTk()
        user_info = {"username": "planner", "display_name": "Planner User"}
        
        # Act
        widget = UserContextWidget(root, user_info, "Planner", "Default Organization")
        
        # Assert
        # Test that display shows appropriate user information
        assert "planner" in widget.get_display_text().lower()
        assert "planner user" in widget.get_display_text().lower()
        
        # Cleanup
        root.destroy()


class TestAuthenticationFlow:
    """Test cases for complete authentication flow."""

    @patch('frontend.authentication_ui.DBRService')
    def test_complete_authentication_workflow(self, mock_dbr_service):
        """Test complete authentication process from login to main window."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import AuthenticationManager
        
        # Arrange
        mock_service_instance = mock_dbr_service.return_value
        mock_service_instance.health_check.return_value = True
        mock_service_instance.login.return_value = True
        mock_service_instance.get_user_info.return_value = {
            "username": "orgadmin", "display_name": "Org Admin User"
        }
        mock_service_instance.get_user_role.return_value = "Org Admin"
        mock_service_instance.get_current_organization.return_value = {
            "name": "Default Organization"
        }
        
        # Act
        auth_manager = AuthenticationManager("http://localhost:8000")
        result = auth_manager.authenticate()
        
        # Assert
        assert result is not None  # Should return authenticated service
        assert result == mock_service_instance

    @patch('frontend.authentication_ui.DBRService')
    @patch('frontend.authentication_ui.LoginDialog')
    def test_authentication_failure_handling(self, mock_login_dialog, mock_dbr_service):
        """Test authentication failure scenarios."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import AuthenticationManager
        
        # Arrange - Mock login dialog to return None (user cancelled)
        mock_dialog_instance = mock_login_dialog.return_value
        mock_dialog_instance.result = None  # User cancelled login
        
        # Act
        auth_manager = AuthenticationManager("http://localhost:8000")
        result = auth_manager.authenticate()
        
        # Assert
        assert result is None  # Should return None on failure/cancellation

    @patch('frontend.authentication_ui.DBRService')
    def test_test_user_credential_hints(self, mock_dbr_service):
        """Test that login dialog shows test user credential hints."""
        # Import after patching to avoid import issues
        from frontend.authentication_ui import LoginDialog
        
        # Arrange & Act
        dialog = LoginDialog(None, "http://localhost:8000")
        
        # Assert
        # Check that test user hints are available
        test_users = dialog.get_test_user_hints()
        assert len(test_users) == 5
        assert any(user["username"] == "admin" for user in test_users)
        assert any(user["username"] == "orgadmin" for user in test_users)
        assert any(user["username"] == "planner" for user in test_users)
        assert any(user["username"] == "testuser" for user in test_users)
        assert any(user["username"] == "viewer2" for user in test_users)