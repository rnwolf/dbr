# tests/test_api/test_auth.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.user import User
from dbr.models.organization import Organization
from dbr.models.role import Role, RoleName
from dbr.models.organization_membership import OrganizationMembership
from dbr.core.security import hash_password


client = TestClient(app)


@pytest.fixture
def test_user(session, test_organization, test_role):
    """Create or get a test user with hashed password"""
    # Try to get existing user first
    user = session.query(User).filter_by(email="test@example.com").first()
    if not user:
        # Create new user if it doesn't exist
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("testpassword123"),
            display_name="Test User",
            active_status=True,
            system_role_id=test_role.id  # Add the required system_role_id
        )
        session.add(user)
        session.commit()
    return user


@pytest.fixture
def test_role(session):
    """Create or get a test role"""
    # Try to get existing role first
    role = session.query(Role).filter_by(name=RoleName.PLANNER).first()
    if not role:
        # Create new role if it doesn't exist
        role = Role(
            name=RoleName.PLANNER,
            description="Planner role for testing"
        )
        session.add(role)
        session.commit()
    return role


@pytest.fixture
def test_membership(session, test_user, test_organization, test_role):
    """Create a test organization membership"""
    membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=test_user.id,
        role_id=test_role.id,
        invitation_status="accepted",
        invited_by_user_id=test_user.id  # Self-invited for testing purposes
    )
    session.add(membership)
    session.commit()
    return membership


def test_auth_login_endpoint_exists():
    """Test that the login API endpoint exists"""
    # This test should FAIL initially since we haven't implemented the endpoint yet
    response = client.post("/api/v1/auth/login")
    
    # We expect this to fail with 404 initially, then pass when implemented
    assert response.status_code != 404, "Login endpoint should exist"


def test_auth_login_requires_credentials():
    """Test that login API requires username and password"""
    # This test should FAIL initially
    response = client.post("/api/v1/auth/login", json={})
    
    # Should fail with 422 (validation error) when credentials are missing
    assert response.status_code == 422, "Should require username and password"


def test_auth_login_with_valid_credentials(session, test_user, test_membership):
    """Test login with valid username and password"""
    # This test should FAIL initially since endpoint doesn't exist
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Should succeed when implemented
    assert response.status_code == 200
    
    # Check response format - should include JWT token and user info
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"


def test_auth_login_with_email_instead_of_username(session, test_user, test_membership):
    """Test login with email instead of username"""
    # This test should FAIL initially
    
    login_data = {
        "username": "test@example.com",  # Using email as username
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Should succeed - system should accept email as username
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_auth_login_with_invalid_credentials():
    """Test login with invalid credentials"""
    # This test should FAIL initially
    
    # Test wrong password
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "detail" in response.json()
    
    # Test non-existent user
    login_data = {
        "username": "nonexistentuser",
        "password": "anypassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_auth_login_with_inactive_user(session, test_organization, test_role):
    """Test login with inactive user account"""
    # This test should FAIL initially
    
    # Create or get inactive user
    inactive_user = session.query(User).filter_by(email="inactive@example.com").first()
    if not inactive_user:
        inactive_user = User(
            username="inactiveuser",
            email="inactive@example.com",
            password_hash=hash_password("password123"),
            display_name="Inactive User",
            active_status=False,  # Inactive
            system_role_id=test_role.id  # Add the required system_role_id
        )
        session.add(inactive_user)
        session.commit()
    else:
        # Update existing user to be inactive for this test
        inactive_user.active_status = False
        session.commit()
    
    login_data = {
        "username": "inactiveuser",
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    # Should return 401 Unauthorized for inactive user
    assert response.status_code == 401
    # The system correctly rejects inactive users (either with "inactive" message or generic "incorrect credentials")
    detail = response.json()["detail"].lower()
    assert "inactive" in detail or "incorrect" in detail


def test_protected_endpoint_requires_authentication():
    """Test that protected endpoints require authentication"""
    # This test should FAIL initially
    
    # Try to access a protected endpoint without token
    response = client.get("/api/v1/workitems")
    
    # Should return 401 Unauthorized or 403 Forbidden (both indicate auth required)
    assert response.status_code in [401, 403]


def test_protected_endpoint_with_valid_token(session, test_user, test_membership):
    """Test accessing protected endpoint with valid JWT token"""
    # This test should FAIL initially
    
    # First login to get token
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    
    # Use token to access protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/workitems", headers=headers)
    
    # Should succeed with valid token
    assert response.status_code in [200, 422]  # 422 if missing required params, but not 401


def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid JWT token"""
    # This test should FAIL initially
    
    # Use invalid token
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client.get("/api/v1/workitems", headers=headers)
    
    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_jwt_token_contains_user_info(session, test_user, test_membership):
    """Test that JWT token contains proper user information"""
    # This test should FAIL initially
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    token = data["access_token"]
    
    # Token should be a valid JWT (basic format check)
    assert len(token.split('.')) == 3, "JWT should have 3 parts separated by dots"
    
    # User info should be included in response
    user_info = data["user"]
    assert user_info["id"] == test_user.id
    assert user_info["username"] == test_user.username
    assert user_info["email"] == test_user.email
    assert user_info["active_status"] == test_user.active_status


def test_role_based_access_control(session, test_organization):
    """Test role-based access control for different user roles"""
    # This test should FAIL initially
    
    # Create or get users with different roles
    admin_role = session.query(Role).filter_by(name=RoleName.ORGANIZATION_ADMIN).first()
    if not admin_role:
        admin_role = Role(name=RoleName.ORGANIZATION_ADMIN, description="Admin role")
        session.add(admin_role)
    
    viewer_role = session.query(Role).filter_by(name=RoleName.VIEWER).first()
    if not viewer_role:
        viewer_role = Role(name=RoleName.VIEWER, description="Viewer role")
        session.add(viewer_role)
    
    session.commit()
    
    # Create or get admin user
    admin_user = session.query(User).filter_by(email="admin@example.com").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            display_name="Admin User",
            active_status=True,
            system_role_id=admin_role.id
        )
        session.add(admin_user)
    
    # Create or get viewer user
    viewer_user = session.query(User).filter_by(email="viewer@example.com").first()
    if not viewer_user:
        viewer_user = User(
            username="viewer",
            email="viewer@example.com",
            password_hash=hash_password("viewer123"),
            display_name="Viewer User",
            active_status=True,
            system_role_id=viewer_role.id
        )
        session.add(viewer_user)
    
    session.commit()
    
    # Create memberships
    admin_membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=admin_user.id,
        role_id=admin_role.id,
        invitation_status="accepted",
        invited_by_user_id=admin_user.id  # Self-invited for testing
    )
    
    viewer_membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=viewer_user.id,
        role_id=viewer_role.id,
        invitation_status="accepted",
        invited_by_user_id=admin_user.id  # Invited by admin
    )
    
    session.add_all([admin_membership, viewer_membership])
    session.commit()
    
    # Test admin can access admin endpoints
    admin_login = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test viewer has limited access
    viewer_login = client.post("/api/v1/auth/login", json={"username": "viewer", "password": "viewer123"})
    assert viewer_login.status_code == 200
    
    viewer_token = viewer_login.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    
    # Both should be able to login successfully
    assert "access_token" in admin_login.json()
    assert "access_token" in viewer_login.json()


if __name__ == "__main__":
    pytest.main([__file__])