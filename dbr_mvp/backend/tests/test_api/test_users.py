# tests/test_api/test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.user import User
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.role import Role, RoleName
from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
from dbr.core.security import hash_password


client = TestClient(app)


@pytest.fixture
def test_roles(session):
    """Create all system roles"""
    from dbr.core.database import create_system_roles
    return create_system_roles(session)


@pytest.fixture
def test_admin_role(session, test_roles):
    """Get admin role"""
    role = session.query(Role).filter_by(name=RoleName.ORGANIZATION_ADMIN).first()
    print(f"DEBUG: Found admin role: {role.id if role else 'None'}")
    assert role is not None, "Admin role not found in database"
    return role


@pytest.fixture
def test_planner_role(session, test_roles):
    """Get planner role"""
    role = session.query(Role).filter_by(name=RoleName.PLANNER).first()
    print(f"DEBUG: Found planner role: {role.id if role else 'None'}")
    assert role is not None, "Planner role not found in database"
    return role


@pytest.fixture
def test_admin_user(session, test_organization, test_admin_role):
    """Create a test admin user"""
    # Debug: Print role info
    print(f"DEBUG: Admin role ID: {test_admin_role.id}, Name: {test_admin_role.name}")
    
    user = User(
        username="admin_user",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        display_name="Admin User",
        active_status=True,
        system_role_id=test_admin_role.id
    )
    session.add(user)
    session.flush()  # Flush to get the user ID without committing
    
    # Create membership
    membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=user.id,
        role_id=test_admin_role.id,
        invitation_status=InvitationStatus.ACCEPTED,
        invited_by_user_id=user.id
    )
    session.add(membership)
    session.commit()
    
    return user


@pytest.fixture
def admin_headers(session, test_admin_user):
    """Get admin authentication headers"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "admin_user",
        "password": "admin123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_regular_user(session, test_organization, test_planner_role):
    """Create a test regular user"""
    user = User(
        username="regular_user",
        email="regular@test.com",
        password_hash=hash_password("regular123"),
        display_name="Regular User",
        active_status=True,
        system_role_id=test_planner_role.id
    )
    session.add(user)
    session.commit()
    
    # Create membership
    membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=user.id,
        role_id=test_planner_role.id,
        invitation_status=InvitationStatus.ACCEPTED,
        invited_by_user_id=user.id
    )
    session.add(membership)
    session.commit()
    
    return user


class TestGetUsers:
    """Test GET /api/v1/users endpoint"""
    
    def test_get_users_success(self, session, test_organization, admin_headers, test_admin_user, test_regular_user):
        """Test successful retrieval of users list"""
        response = client.get(
            "/api/v1/users",
            params={"organization_id": test_organization.id},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2  # At least admin and regular user
        
        # Check user structure
        user_emails = [user["email"] for user in users]
        assert "admin@test.com" in user_emails
        assert "regular@test.com" in user_emails
        
        # Check required fields
        for user in users:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "display_name" in user
            assert "active_status" in user
            assert "system_role_id" in user
            assert "created_date" in user
            assert "updated_date" in user
            # Password hash should not be exposed
            assert "password_hash" not in user


class TestCreateUser:
    """Test POST /api/v1/users endpoint"""
    
    def test_create_user_success(self, session, test_organization, admin_headers, test_planner_role):
        """Test successful user creation"""
        user_data = {
            "organization_id": test_organization.id,
            "username": "newuser",
            "email": "newuser@test.com",
            "display_name": "New User",
            "password": "newuser123",
            "system_role_id": test_planner_role.id,
            "active_status": True
        }
        
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers=admin_headers
        )
        
        assert response.status_code == 201
        created_user = response.json()
        
        # Check response structure
        assert created_user["username"] == "newuser"
        assert created_user["email"] == "newuser@test.com"
        assert created_user["display_name"] == "New User"
        assert created_user["active_status"] is True
        assert created_user["system_role_id"] == test_planner_role.id
        assert "id" in created_user
        assert "created_date" in created_user
        assert "updated_date" in created_user
        # Password should not be in response
        assert "password" not in created_user
        assert "password_hash" not in created_user

    def test_create_user_duplicate_email(self, test_organization, admin_headers, test_planner_role, test_regular_user):
        """Test creating user with duplicate email fails"""
        user_data = {
            "organization_id": test_organization.id,
            "username": "duplicate",
            "email": test_regular_user.email,  # Use existing email
            "display_name": "Duplicate User",
            "password": "duplicate123",
            "system_role_id": test_planner_role.id,
            "active_status": True
        }
        
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers=admin_headers
        )
        
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"].lower()

    def test_create_user_duplicate_username(self, test_organization, admin_headers, test_planner_role, test_regular_user):
        """Test creating user with duplicate username fails"""
        user_data = {
            "organization_id": test_organization.id,
            "username": test_regular_user.username,  # Use existing username
            "email": "unique@test.com",
            "display_name": "Duplicate Username",
            "password": "duplicate123",
            "system_role_id": test_planner_role.id,
            "active_status": True
        }
        
        response = client.post(
            "/api/v1/users",
            json=user_data,
            headers=admin_headers
        )
        
        assert response.status_code == 400
        assert "username already exists" in response.json()["detail"].lower()

    def test_create_user_without_auth(self, test_organization, test_planner_role):
        """Test that user creation requires authentication"""
        user_data = {
            "organization_id": test_organization.id,
            "username": "noauth",
            "email": "noauth@test.com",
            "display_name": "No Auth User",
            "password": "noauth123",
            "system_role_id": test_planner_role.id,
            "active_status": True
        }
        
        response = client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 403


class TestGetUser:
    """Test GET /api/v1/users/{user_id} endpoint"""
    
    def test_get_user_success(self, admin_headers, test_regular_user):
        """Test successful retrieval of specific user"""
        response = client.get(
            f"/api/v1/users/{test_regular_user.id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        user = response.json()
        
        assert user["id"] == test_regular_user.id
        assert user["username"] == test_regular_user.username
        assert user["email"] == test_regular_user.email
        assert user["display_name"] == test_regular_user.display_name
        assert user["active_status"] == test_regular_user.active_status
        assert "password_hash" not in user

    def test_get_user_not_found(self, admin_headers):
        """Test getting nonexistent user"""
        import uuid
        fake_user_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/v1/users/{fake_user_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_get_user_invalid_uuid(self, admin_headers):
        """Test getting user with invalid UUID"""
        response = client.get(
            "/api/v1/users/invalid-uuid",
            headers=admin_headers
        )
        
        assert response.status_code == 422

    def test_get_user_without_auth(self, test_regular_user):
        """Test that getting user requires authentication"""
        response = client.get(f"/api/v1/users/{test_regular_user.id}")
        
        assert response.status_code == 403


class TestUpdateUser:
    """Test PUT /api/v1/users/{user_id} endpoint"""
    
    def test_update_user_success(self, session, admin_headers, test_regular_user):
        """Test successful user update"""
        update_data = {
            "display_name": "Updated Display Name",
            "active_status": False
        }
        
        response = client.put(
            f"/api/v1/users/{test_regular_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["display_name"] == "Updated Display Name"
        assert updated_user["active_status"] is False
        assert updated_user["username"] == test_regular_user.username  # Unchanged
        assert updated_user["email"] == test_regular_user.email  # Unchanged

    def test_update_user_email(self, session, admin_headers, test_regular_user):
        """Test updating user email"""
        update_data = {
            "email": "newemail@test.com"
        }
        
        response = client.put(
            f"/api/v1/users/{test_regular_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["email"] == "newemail@test.com"

    def test_update_user_duplicate_email(self, admin_headers, test_regular_user, test_admin_user):
        """Test updating user with duplicate email fails"""
        update_data = {
            "email": test_admin_user.email  # Use existing email
        }
        
        response = client.put(
            f"/api/v1/users/{test_regular_user.id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"].lower()

    def test_update_user_not_found(self, admin_headers):
        """Test updating nonexistent user"""
        import uuid
        fake_user_id = str(uuid.uuid4())
        
        update_data = {"display_name": "New Name"}
        
        response = client.put(
            f"/api/v1/users/{fake_user_id}",
            json=update_data,
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_update_user_without_auth(self, test_regular_user):
        """Test that updating user requires authentication"""
        update_data = {"display_name": "Unauthorized Update"}
        
        response = client.put(
            f"/api/v1/users/{test_regular_user.id}",
            json=update_data
        )
        
        assert response.status_code == 403


class TestDeleteUser:
    """Test DELETE /api/v1/users/{user_id} endpoint"""
    
    def test_delete_user_success(self, session, admin_headers, test_regular_user):
        """Test successful user deletion"""
        user_id = test_regular_user.id
        
        response = client.delete(
            f"/api/v1/users/{user_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"

    def test_delete_user_not_found(self, admin_headers):
        """Test deleting nonexistent user"""
        import uuid
        fake_user_id = str(uuid.uuid4())
        
        response = client.delete(
            f"/api/v1/users/{fake_user_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 404

    def test_delete_user_without_auth(self, test_regular_user):
        """Test that deleting user requires authentication"""
        response = client.delete(f"/api/v1/users/{test_regular_user.id}")
        
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__])