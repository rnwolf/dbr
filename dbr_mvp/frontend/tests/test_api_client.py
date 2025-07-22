# tests/test_api_client.py
import pytest
import requests
from unittest.mock import Mock, patch
from frontend.api_client import APIClient
from frontend.exceptions import AuthenticationError, APIError


@pytest.fixture
def api_client():
    """Create an API client for testing"""
    return APIClient(base_url="http://localhost:8000/api/v1")


@pytest.fixture
def mock_response():
    """Create a mock response object"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"message": "success"}
    return response


def test_api_client_initialization():
    """Test API client can be initialized"""
    # This test should FAIL initially since APIClient doesn't exist yet
    client = APIClient(base_url="http://localhost:8000/api/v1")
    
    assert client.base_url == "http://localhost:8000/api/v1"
    assert client.token is None
    assert client.session is not None


def test_api_client_authentication(api_client):
    """Test frontend API authentication"""
    # This test should FAIL initially
    
    # Mock successful login response
    mock_response = {
        "access_token": "test_token_123",
        "token_type": "bearer",
        "user": {
            "id": "user-123",
            "username": "testuser",
            "email": "test@example.com",
            "active_status": True
        }
    }
    
    with patch.object(api_client.session, 'post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        # Test: Login with test credentials
        result = api_client.login("testuser", "testpassword")
        
        # Should return user info and store token
        assert result["user"]["username"] == "testuser"
        assert api_client.token == "test_token_123"
        assert api_client.is_authenticated() is True


def test_api_client_token_storage_and_reuse(api_client):
    """Test token storage and reuse"""
    # This test should FAIL initially
    
    # Set a token
    api_client.set_token("stored_token_456")
    
    # Test: Token storage
    assert api_client.token == "stored_token_456"
    assert api_client.is_authenticated() is True
    
    # Test: Token reuse in requests
    with patch.object(api_client.session, 'get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}
        
        api_client.get("/test-endpoint")
        
        # Should include Authorization header
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert "Authorization" in call_kwargs["headers"]
        assert call_kwargs["headers"]["Authorization"] == "Bearer stored_token_456"


def test_api_client_automatic_logout_on_token_expiry(api_client):
    """Test automatic logout on token expiry"""
    # This test should FAIL initially
    
    # Set a token
    api_client.set_token("expired_token")
    
    # Mock 401 response (token expired)
    with patch.object(api_client.session, 'get') as mock_get:
        mock_get.return_value.status_code = 401
        mock_get.return_value.json.return_value = {"detail": "Token expired"}
        
        # Should raise AuthenticationError and clear token
        with pytest.raises(AuthenticationError):
            api_client.get("/protected-endpoint")
        
        # Token should be cleared
        assert api_client.token is None
        assert api_client.is_authenticated() is False


def test_api_client_work_items_fetch(api_client):
    """Test work item API integration - fetch"""
    # This test should FAIL initially
    
    # Mock work items response
    mock_work_items = [
        {
            "id": "wi-001",
            "title": "Test Work Item 1",
            "status": "Ready",
            "priority": "medium",
            "estimated_total_hours": 8.0
        },
        {
            "id": "wi-002", 
            "title": "Test Work Item 2",
            "status": "In Progress",
            "priority": "high",
            "estimated_total_hours": 12.0
        }
    ]
    
    with patch.object(api_client.session, 'get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_work_items
        
        # Test: Fetch work items from backend
        work_items = api_client.get_work_items(organization_id="org-123")
        
        assert len(work_items) == 2
        assert work_items[0]["title"] == "Test Work Item 1"
        assert work_items[1]["status"] == "In Progress"


def test_api_client_work_items_create(api_client):
    """Test work item API integration - create"""
    # This test should FAIL initially
    
    # Mock create work item response
    mock_created_item = {
        "id": "wi-003",
        "title": "New Work Item",
        "status": "Backlog",
        "priority": "medium",
        "estimated_total_hours": 6.0,
        "created_date": "2025-01-21T10:00:00Z"
    }
    
    with patch.object(api_client.session, 'post') as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = mock_created_item
        
        # Test: Create new work item
        work_item_data = {
            "organization_id": "org-123",
            "title": "New Work Item",
            "estimated_total_hours": 6.0
        }
        
        result = api_client.create_work_item(work_item_data)
        
        assert result["id"] == "wi-003"
        assert result["title"] == "New Work Item"
        assert result["status"] == "Backlog"


def test_api_client_work_items_update_status(api_client):
    """Test work item API integration - update status"""
    # This test should FAIL initially
    
    # Mock update response
    mock_updated_item = {
        "id": "wi-001",
        "title": "Test Work Item 1",
        "status": "Ready",  # Updated status
        "priority": "medium",
        "estimated_total_hours": 8.0
    }
    
    with patch.object(api_client.session, 'put') as mock_put:
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = mock_updated_item
        
        # Test: Update work item status
        result = api_client.update_work_item(
            work_item_id="wi-001",
            organization_id="org-123",
            data={"status": "Ready"}
        )
        
        assert result["status"] == "Ready"


def test_api_client_schedules_integration(api_client):
    """Test schedule API integration"""
    # This test should FAIL initially
    
    # Mock schedules response
    mock_schedules = [
        {
            "id": "sch-001",
            "status": "Planning",
            "work_item_ids": ["wi-001", "wi-002"],
            "time_unit_position": -5,
            "total_ccr_time": 20.0
        }
    ]
    
    with patch.object(api_client.session, 'get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_schedules
        
        # Test: Fetch schedules
        schedules = api_client.get_schedules(organization_id="org-123")
        
        assert len(schedules) == 1
        assert schedules[0]["status"] == "Planning"
        assert len(schedules[0]["work_item_ids"]) == 2


def test_api_client_time_progression_integration(api_client):
    """Test time progression API integration"""
    # This test should FAIL initially
    
    # Mock time progression response
    mock_response = {
        "message": "All active schedules advanced one time unit.",
        "advanced_schedules_count": 3
    }
    
    with patch.object(api_client.session, 'post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        # Test: Advance time
        result = api_client.advance_time_unit(organization_id="org-123")
        
        assert result["advanced_schedules_count"] == 3
        assert "advanced" in result["message"]


def test_api_client_error_handling(api_client):
    """Test API client error handling"""
    # This test should FAIL initially
    
    # Test 404 error
    with patch.object(api_client.session, 'get') as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {"detail": "Not found"}
        
        with pytest.raises(APIError) as exc_info:
            api_client.get("/nonexistent-endpoint")
        
        assert exc_info.value.status_code == 404
        assert "Not found" in str(exc_info.value)


def test_api_client_retry_logic(api_client):
    """Test API client retry logic for network errors"""
    # This test should FAIL initially
    
    with patch.object(api_client.session, 'get') as mock_get:
        # First call fails with connection error, second succeeds
        mock_get.side_effect = [
            requests.ConnectionError("Network error"),
            Mock(status_code=200, json=lambda: {"data": "success"})
        ]
        
        # Should retry and succeed
        result = api_client.get("/test-endpoint")
        assert result["data"] == "success"
        
        # Should have made 2 calls (original + 1 retry)
        assert mock_get.call_count == 2


def test_api_client_logout(api_client):
    """Test API client logout functionality"""
    # This test should FAIL initially
    
    # Set a token first
    api_client.set_token("test_token")
    assert api_client.is_authenticated() is True
    
    # Test logout
    api_client.logout()
    
    # Token should be cleared
    assert api_client.token is None
    assert api_client.is_authenticated() is False


if __name__ == "__main__":
    pytest.main([__file__])