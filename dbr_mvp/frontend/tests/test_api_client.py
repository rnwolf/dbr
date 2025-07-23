# tests/test_api_client.py
"""Test API client functionality - Step 5.2 TDD"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests

# Add src to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.unit
class TestAPIClientAuthentication:
    """Test API authentication flow"""
    
    def test_api_client_initialization(self):
        """Test API client can be initialized"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"
        assert client.token is None
        assert client.current_organization_id is None
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock successful login response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_jwt_token",
            "token_type": "bearer",
            "user": {
                "id": "user123",
                "username": "testuser",
                "email": "test@example.com"
            }
        }
        mock_response.status_code = 200
        
        with patch('requests.post', return_value=mock_response):
            result = client.login("testuser", "password123")
        
        assert result is True
        assert client.token == "test_jwt_token"
        assert client.current_user["id"] == "user123"
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock failed login response
        mock_response = Mock()
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_response.status_code = 401
        
        with patch('requests.post', return_value=mock_response):
            result = client.login("baduser", "badpass")
        
        assert result is False
        assert client.token is None
    
    def test_jwt_token_storage_and_headers(self):
        """Test JWT token storage and automatic header inclusion"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_jwt_token"
        
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer test_jwt_token"
        assert headers["Content-Type"] == "application/json"
    
    def test_automatic_logout_on_token_expiry(self):
        """Test automatic logout when token expires"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "expired_token"
        
        # Mock 401 response (token expired)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Token expired"}
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_organizations()
        
        # Should automatically logout and return None
        assert result is None
        assert client.token is None


@pytest.mark.unit
class TestAPIClientEndpoints:
    """Test API endpoint integration"""
    
    def test_organization_api_calls(self):
        """Test Organization API calls (CRUD)"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        
        # Test GET organizations
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "org1", "name": "Test Org 1"},
            {"id": "org2", "name": "Test Org 2"}
        ]
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            orgs = client.get_organizations()
        
        assert len(orgs) == 2
        assert orgs[0]["name"] == "Test Org 1"
    
    def test_work_items_api_with_organization_scoping(self):
        """Test Work items API calls with organization scoping"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        client.current_organization_id = "org123"
        
        # Test GET work items
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "wi1", "title": "Work Item 1", "organization_id": "org123"},
            {"id": "wi2", "title": "Work Item 2", "organization_id": "org123"}
        ]
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            work_items = client.get_work_items()
        
        # Verify organization_id was included in request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "organization_id=org123" in call_args[0][0] or "org123" in str(call_args)
        
        assert len(work_items) == 2
        assert work_items[0]["organization_id"] == "org123"
    
    def test_schedules_api_with_organization_scoping(self):
        """Test Schedules API calls with organization scoping"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        client.current_organization_id = "org123"
        
        # Test GET schedules
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": "sched1", "organization_id": "org123", "status": "Planning"},
            {"id": "sched2", "organization_id": "org123", "status": "Pre-Constraint"}
        ]
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            schedules = client.get_schedules()
        
        # Verify organization_id was included in request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "organization_id=org123" in call_args[0][0] or "org123" in str(call_args)
        
        assert len(schedules) == 2
        assert schedules[0]["organization_id"] == "org123"
    
    def test_system_api_calls(self):
        """Test System API calls (time progression)"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        
        # Test time progression
        mock_response = Mock()
        mock_response.json.return_value = {
            "message": "Time advanced successfully",
            "new_time": "2024-01-15T10:00:00Z"
        }
        mock_response.status_code = 200
        
        with patch('requests.post', return_value=mock_response):
            result = client.advance_time()
        
        assert result["message"] == "Time advanced successfully"
    
    def test_error_handling_and_retries(self):
        """Test error handling and retries"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        
        # Test network error handling
        with patch('requests.get', side_effect=requests.ConnectionError("Network error")):
            result = client.get_organizations()
        
        assert result is None
        
        # Test server error handling
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        
        with patch('requests.get', return_value=mock_response):
            result = client.get_organizations()
        
        assert result is None


@pytest.mark.unit
class TestOrganizationScoping:
    """Test organization context in API calls"""
    
    def test_organization_switching_updates_context(self):
        """Test organization switching updates context"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        
        # Switch to organization
        client.set_current_organization("org456")
        assert client.current_organization_id == "org456"
        
        # Switch to different organization
        client.set_current_organization("org789")
        assert client.current_organization_id == "org789"
    
    def test_all_api_calls_include_organization_id(self):
        """Test all API calls include organization_id when set"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        client.current_organization_id = "org123"
        
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            # Test various API calls
            client.get_work_items()
            client.get_schedules()
            client.get_ccrs()
        
        # Verify all calls included organization_id
        assert mock_get.call_count == 3
        for call in mock_get.call_args_list:
            call_url = call[0][0]
            assert "organization_id=org123" in call_url or "org123" in str(call)
    
    def test_multi_tenant_data_isolation(self):
        """Test multi-tenant data isolation"""
        from app.api.api_client import APIClient
        
        client = APIClient(base_url="http://localhost:8000")
        client.token = "test_token"
        
        # Test with org1
        client.set_current_organization("org1")
        
        mock_response_org1 = Mock()
        mock_response_org1.json.return_value = [
            {"id": "wi1", "title": "Org1 Work Item", "organization_id": "org1"}
        ]
        mock_response_org1.status_code = 200
        
        with patch('requests.get', return_value=mock_response_org1):
            org1_items = client.get_work_items()
        
        # Test with org2
        client.set_current_organization("org2")
        
        mock_response_org2 = Mock()
        mock_response_org2.json.return_value = [
            {"id": "wi2", "title": "Org2 Work Item", "organization_id": "org2"}
        ]
        mock_response_org2.status_code = 200
        
        with patch('requests.get', return_value=mock_response_org2):
            org2_items = client.get_work_items()
        
        # Verify data isolation
        assert org1_items[0]["organization_id"] == "org1"
        assert org2_items[0]["organization_id"] == "org2"
        assert org1_items[0]["id"] != org2_items[0]["id"]


if __name__ == "__main__":
    pytest.main([__file__])