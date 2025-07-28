"""Tests for the DBRService class."""

import pytest
from unittest.mock import patch, MagicMock


class TestDBRService:
    """Test cases for the DBRService."""

    @patch('frontend.dbr_service.Dbrsdk')
    @patch('frontend.dbr_service.LoginRequest')
    def test_authentication_service_login_success(self, mock_login_request, mock_dbrsdk):
        """Tests that the login method correctly calls the SDK and stores the token."""
        # Import after patching to avoid import issues
        from frontend.dbr_service import DBRService
        
        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        success = service.login("testuser", "password")

        # Assert
        assert success is True
        assert service.get_token() == "fake_token"
        mock_sdk_instance.authentication.login.assert_called_once()

    @patch('frontend.dbr_service.Dbrsdk')
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

    @patch('frontend.dbr_service.Dbrsdk')
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

    @patch('frontend.dbr_service.Dbrsdk')
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
