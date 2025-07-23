# tests/test_api/test_security_audit.py
"""
Security audit tests to ensure ALL API endpoints require authentication.
This test file ensures no endpoint can be accessed without proper authentication.
"""
import pytest
from fastapi.testclient import TestClient
from dbr.main import app


client = TestClient(app)


class TestSecurityAudit:
    """Comprehensive security audit for all API endpoints"""
    
    def test_schedules_api_requires_authentication(self):
        """Test that ALL schedules endpoints require authentication"""
        
        # Test GET /schedules
        response = client.get("/api/v1/schedules?organization_id=test-org-id")
        assert response.status_code in [401, 403], "GET /schedules should require authentication"
        
        # Test POST /schedules (CREATE)
        schedule_data = {
            "organization_id": "test-org-id",
            "board_config_id": "test-board-id",
            "work_item_ids": ["item1", "item2"]
        }
        response = client.post("/api/v1/schedules", json=schedule_data)
        assert response.status_code in [401, 403], "POST /schedules should require authentication"
        
        # Test GET /schedules/{id}
        response = client.get("/api/v1/schedules/test-schedule-id?organization_id=test-org-id")
        assert response.status_code in [401, 403], "GET /schedules/{id} should require authentication"
        
        # Test PUT /schedules/{id} (UPDATE)
        update_data = {"status": "Completed"}
        response = client.put("/api/v1/schedules/test-schedule-id?organization_id=test-org-id", json=update_data)
        assert response.status_code in [401, 403], "PUT /schedules/{id} should require authentication"
        
        # Test DELETE /schedules/{id}
        response = client.delete("/api/v1/schedules/test-schedule-id?organization_id=test-org-id")
        assert response.status_code in [401, 403], "DELETE /schedules/{id} should require authentication"
        
        # Test GET /schedules/{id}/analytics
        response = client.get("/api/v1/schedules/test-schedule-id/analytics?organization_id=test-org-id")
        assert response.status_code in [401, 403], "GET /schedules/{id}/analytics should require authentication"
        
        # Test GET /schedules/board/{board_id}/analytics
        response = client.get("/api/v1/schedules/board/test-board-id/analytics?organization_id=test-org-id")
        assert response.status_code in [401, 403], "GET /schedules/board/{board_id}/analytics should require authentication"
    
    def test_system_api_requires_authentication(self):
        """Test that ALL system endpoints require authentication"""
        
        # Test POST /system/advance_time_unit (CRITICAL - TIME MANIPULATION)
        response = client.post("/api/v1/system/advance_time_unit?organization_id=test-org-id")
        assert response.status_code in [401, 403], "POST /system/advance_time_unit should require authentication"
        
        # Test GET /system/time
        response = client.get("/api/v1/system/time")
        assert response.status_code in [401, 403], "GET /system/time should require authentication"
        
        # Test POST /system/time (CRITICAL - TIME MANIPULATION)
        response = client.post("/api/v1/system/time?time_iso=2024-01-01T00:00:00Z")
        assert response.status_code in [401, 403], "POST /system/time should require authentication"
    
    def test_work_items_api_has_authentication(self):
        """Verify work items API properly requires authentication (should pass after our fix)"""
        
        # Test GET /workitems (should require auth)
        response = client.get("/api/v1/workitems?organization_id=test-org-id")
        assert response.status_code in [401, 403], "GET /workitems should require authentication"
        
        # Test POST /workitems (should require auth after our fix)
        work_item_data = {
            "organization_id": "test-org-id",
            "title": "Test Item",
            "estimated_total_hours": 8.0
        }
        response = client.post("/api/v1/workitems", json=work_item_data)
        assert response.status_code in [401, 403], "POST /workitems should require authentication"
        
        # Test PUT /workitems/{id} (should require auth after our fix)
        response = client.put("/api/v1/workitems/test-id?organization_id=test-org-id", json={"title": "Updated"})
        assert response.status_code in [401, 403], "PUT /workitems/{id} should require authentication"
        
        # Test DELETE /workitems/{id} (should require auth after our fix)
        response = client.delete("/api/v1/workitems/test-id?organization_id=test-org-id")
        assert response.status_code in [401, 403], "DELETE /workitems/{id} should require authentication"
    
    def test_auth_endpoints_behavior(self):
        """Test auth endpoints behave correctly"""
        
        # Test /auth/login should be accessible (no auth required for login)
        response = client.post("/api/v1/auth/login", json={})
        # Should return 422 (validation error) not 401/403 (auth error)
        assert response.status_code == 422, "Login endpoint should be accessible but require valid credentials"
        
        # Test /auth/me should require authentication
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403], "GET /auth/me should require authentication"
        
        # Test /auth/logout should require authentication  
        response = client.post("/api/v1/auth/logout")
        assert response.status_code in [401, 403], "POST /auth/logout should require authentication"


if __name__ == "__main__":
    pytest.main([__file__])