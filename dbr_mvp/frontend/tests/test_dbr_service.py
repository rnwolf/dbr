"""Tests for the DBRService class."""

from unittest.mock import patch, MagicMock


class TestDBRService:
    """Test cases for the DBRService."""

    @patch("frontend.dbr_service.Dbrsdk")
    def test_authentication_service_login_success(self, mock_dbrsdk):
        """Tests that the login method correctly calls the SDK and stores the token."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Org Admin"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        success = service.login("testuser", "password")

        # Assert
        assert success is True
        assert service.get_token() == "fake_token"
        assert service.get_user_role() == "Org Admin"
        assert service.is_authenticated() is True
        mock_sdk_instance.authentication.login.assert_called_once()

    @patch("frontend.dbr_service.Dbrsdk")
    def test_health_check_success(self, mock_dbrsdk):
        """Tests that the health check method works correctly."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_health_response = {"status": "healthy", "service": "DBR API"}
        mock_sdk_instance.health.get.return_value = mock_health_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        result = service.health_check()

        # Assert
        assert result is True
        mock_sdk_instance.health.get.assert_called_once()

    @patch("frontend.dbr_service.Dbrsdk")
    def test_health_check_failure(self, mock_dbrsdk):
        """Tests that the health check method handles failures correctly."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_sdk_instance.health.get.side_effect = Exception("Connection failed")

        service = DBRService("http://127.0.0.1:8000")

        # Act
        result = service.health_check()

        # Assert
        assert result is False
        mock_sdk_instance.health.get.assert_called_once()

    @patch("frontend.dbr_service.Dbrsdk")
    def test_health_check_invalid_response(self, mock_dbrsdk):
        """Tests that the health check method handles invalid responses correctly."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_health_response = {"status": "unhealthy"}  # Wrong status
        mock_sdk_instance.health.get.return_value = mock_health_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        result = service.health_check()

        # Assert
        assert result is False
        mock_sdk_instance.health.get.assert_called_once()

    @patch("frontend.dbr_service.Dbrsdk")
    def test_organization_context_setup(self, mock_dbrsdk):
        """Test organization context management after login."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Planner"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        success = service.login("planner", "password")

        # Assert
        assert success is True
        org_context = service.get_current_organization()
        assert org_context is not None
        assert org_context["name"] == "Default Organization"
        assert org_context["auto_selected"] is True

    @patch("frontend.dbr_service.Dbrsdk")
    def test_role_based_permissions(self, mock_dbrsdk):
        """Test role-based permission checking."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Planner"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")
        service.login("planner", "password")

        # Act & Assert - Planner permissions
        assert service.has_permission("manage_schedules") is True
        assert service.has_permission("manage_work_items") is True
        assert service.has_permission("view_analytics") is True
        assert service.has_permission("manage_users") is False  # Only Org Admin+

    @patch("frontend.dbr_service.Dbrsdk")
    def test_super_admin_permissions(self, mock_dbrsdk):
        """Test Super Admin has all permissions."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Super Admin"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")
        service.login("admin", "password")

        # Act & Assert - Super Admin has all permissions
        assert service.has_permission("manage_users") is True
        assert service.has_permission("manage_schedules") is True
        assert service.has_permission("any_permission") is True

    @patch("frontend.dbr_service.Dbrsdk")
    def test_viewer_permissions(self, mock_dbrsdk):
        """Test Viewer has only read permissions."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Viewer"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")
        service.login("viewer", "password")

        # Act & Assert - Viewer permissions
        assert service.has_permission("view_schedules") is True
        assert service.has_permission("view_work_items") is True
        assert service.has_permission("manage_schedules") is False
        assert service.has_permission("manage_work_items") is False

    @patch("frontend.dbr_service.Dbrsdk")
    def test_logout_clears_context(self, mock_dbrsdk):
        """Test logout clears all authentication context."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Planner"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")
        service.login("planner", "password")

        # Verify logged in
        assert service.is_authenticated() is True
        assert service.get_token() is not None

        # Act
        service.logout()

        # Assert
        assert service.is_authenticated() is False
        assert service.get_token() is None
        assert service.get_user_info() is None
        assert service.get_user_role() is None
        assert service.get_current_organization() is None

    @patch("frontend.dbr_service.Dbrsdk")
    def test_connection_status(self, mock_dbrsdk):
        """Test comprehensive connection status reporting."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService

        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_health_response = {"status": "healthy", "service": "DBR API"}
        mock_sdk_instance.health.get.return_value = mock_health_response

        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.role = "Org Admin"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")
        service.login("orgadmin", "password")

        # Act
        status = service.get_connection_status()

        # Assert
        assert status["backend_url"] == "http://127.0.0.1:8000"
        assert status["backend_healthy"] is True
        assert status["authenticated"] is True
        assert status["role"] == "Org Admin"
        assert status["token_available"] is True
        assert status["organization"] is not None
