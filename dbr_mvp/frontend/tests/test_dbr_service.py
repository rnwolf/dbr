"""Tests for the DBRService class."""

import pytest
from unittest.mock import patch, MagicMock

# Since DBRService imports dbrsdk, we need to patch it before the import
with patch.dict('sys.modules', {
    'dbrsdk': MagicMock(),
    'dbrsdk.models': MagicMock(),
}) as mock:
    from frontend.dbr_service import DBRService


class TestDBRService:
    """Test cases for the DBRService."""

    @patch('frontend.dbr_service.Dbrsdk')
    def test_authentication_service_login_success(self, mock_dbrsdk):
        """Tests that the login method correctly calls the SDK and stores the token."""
        # Arrange
        mock_sdk_instance = mock_dbrsdk.return_value
        mock_login_response = MagicMock()
        mock_login_response.access_token = "fake_token"
        mock_login_response.user = MagicMock()
        mock_login_response.user.username = "testuser"
        mock_sdk_instance.authentication.login.return_value = mock_login_response

        service = DBRService("http://127.0.0.1:8000")

        # Act
        success = service.login("testuser", "password")

        # Assert
        assert success is True
        assert service.get_token() == "fake_token"
        mock_sdk_instance.authentication.login.assert_called_once()
