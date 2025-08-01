# tests/test_api/test_memberships.py
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
def test_super_admin_role(session, test_roles):
    """Get super admin role"""
    role = session.query(Role).filter_by(name=RoleName.SUPER_ADMIN).first()
    assert role is not None, "Super Admin role not found in database"
    return role


@pytest.fixture
def test_org_admin_role(session, test_roles):
    """Get organization admin role"""
    role = session.query(Role).filter_by(name=RoleName.ORGANIZATION_ADMIN).first()
    assert role is not None, "Organization Admin role not found in database"
    return role


@pytest.fixture
def test_planner_role(session, test_roles):
    """Get planner role"""
    role = session.query(Role).filter_by(name=RoleName.PLANNER).first()
    assert role is not None, "Planner role not found in database"
    return role


@pytest.fixture
def test_viewer_role(session, test_roles):
    """Get viewer role"""
    role = session.query(Role).filter_by(name=RoleName.VIEWER).first()
    assert role is not None, "Viewer role not found in database"
    return role


@pytest.fixture
def test_org_admin_user(session, test_organization, test_org_admin_role):
    """Create a test organization admin user"""
    user = User(
        username="org_admin",
        email="orgadmin@test.com",
        password_hash=hash_password("orgadmin123"),
        display_name="Org Admin User",
        active_status=True,
        system_role_id=test_org_admin_role.id
    )
    session.add(user)
    session.commit()
    
    # Create membership
    membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=user.id,
        role_id=test_org_admin_role.id,
        invitation_status=InvitationStatus.ACCEPTED,
        invited_by_user_id=user.id
    )
    session.add(membership)
    session.commit()
    
    return user


@pytest.fixture
def org_admin_headers(session, test_org_admin_user):
    """Get organization admin authentication headers"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "org_admin",
        "password": "orgadmin123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_planner_user(session, test_organization, test_planner_role, test_org_admin_user):
    """Create a test planner user"""
    user = User(
        username="planner_user",
        email="planner@test.com",
        password_hash=hash_password("planner123"),
        display_name="Planner User",
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
        invited_by_user_id=test_org_admin_user.id
    )
    session.add(membership)
    session.commit()
    
    return user


@pytest.fixture
def test_viewer_user(session, test_organization, test_viewer_role, test_org_admin_user):
    """Create a test viewer user"""
    user = User(
        username="viewer_user",
        email="viewer@test.com",
        password_hash=hash_password("viewer123"),
        display_name="Viewer User",
        active_status=True,
        system_role_id=test_viewer_role.id
    )
    session.add(user)
    session.commit()
    
    # Create membership
    membership = OrganizationMembership(
        organization_id=test_organization.id,
        user_id=user.id,
        role_id=test_viewer_role.id,
        invitation_status=InvitationStatus.ACCEPTED,
        invited_by_user_id=test_org_admin_user.id
    )
    session.add(membership)
    session.commit()
    
    return user


@pytest.fixture
def test_unaffiliated_user(session, test_planner_role):
    """Create a user not affiliated with any organization"""
    user = User(
        username="unaffiliated_user",
        email="unaffiliated@test.com",
        password_hash=hash_password("unaffiliated123"),
        display_name="Unaffiliated User",
        active_status=True,
        system_role_id=test_planner_role.id
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def test_second_organization(session):
    """Create a second test organization"""
    org = Organization(
        name="Second Test Organization",
        description="Second test org for membership testing",
        status=OrganizationStatus.ACTIVE,
        contact_email="second@example.com",
        country="CA"
    )
    session.add(org)
    session.commit()
    return org


class TestGetMemberships:
    """Test GET /api/v1/organizations/{org_id}/memberships endpoint"""
    
    def test_get_memberships_success(self, session, test_organization, org_admin_headers, test_org_admin_user, test_planner_user, test_viewer_user):
        """Test successful retrieval of organization memberships"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        memberships = response.json()
        assert isinstance(memberships, list)
        assert len(memberships) >= 3  # At least admin, planner, viewer
        
        # Check membership structure
        user_emails = [membership["user"]["email"] for membership in memberships]
        assert "orgadmin@test.com" in user_emails
        assert "planner@test.com" in user_emails
        assert "viewer@test.com" in user_emails
        
        # Check required fields
        for membership in memberships:
            assert "id" in membership
            assert "organization_id" in membership
            assert "user_id" in membership
            assert "role_id" in membership
            assert "invitation_status" in membership
            assert "invited_by_user_id" in membership
            assert "joined_date" in membership
            assert "created_date" in membership
            assert "updated_date" in membership
            # Check nested user and role information
            assert "user" in membership
            assert "role" in membership
            assert "username" in membership["user"]
            assert "email" in membership["user"]
            assert "name" in membership["role"]

    def test_get_memberships_filtered_by_role(self, test_organization, org_admin_headers, test_planner_role):
        """Test filtering memberships by role"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            params={"role_id": test_planner_role.id},
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        memberships = response.json()
        
        # All returned memberships should have planner role
        for membership in memberships:
            assert membership["role_id"] == test_planner_role.id

    def test_get_memberships_filtered_by_status(self, test_organization, org_admin_headers):
        """Test filtering memberships by invitation status"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            params={"status": "accepted"},
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        memberships = response.json()
        
        # All returned memberships should have accepted status
        for membership in memberships:
            assert membership["invitation_status"] == "accepted"

    def test_get_memberships_invalid_organization(self, org_admin_headers):
        """Test memberships endpoint with invalid organization ID"""
        response = client.get(
            "/api/v1/organizations/invalid-uuid/memberships",
            headers=org_admin_headers
        )
        
        assert response.status_code == 422

    def test_get_memberships_nonexistent_organization(self, org_admin_headers):
        """Test memberships endpoint with nonexistent organization"""
        import uuid
        fake_org_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/v1/organizations/{fake_org_id}/memberships",
            headers=org_admin_headers
        )
        
        assert response.status_code == 404

    def test_get_memberships_without_auth(self, test_organization):
        """Test that memberships endpoint requires authentication"""
        response = client.get(f"/api/v1/organizations/{test_organization.id}/memberships")
        
        assert response.status_code == 403

    def test_get_memberships_forbidden_other_org(self, org_admin_headers, test_second_organization):
        """Test that org admin cannot access other organization memberships"""
        response = client.get(
            f"/api/v1/organizations/{test_second_organization.id}/memberships",
            headers=org_admin_headers
        )
        
        assert response.status_code == 403


class TestCreateMembership:
    """Test POST /api/v1/organizations/{org_id}/memberships endpoint"""
    
    def test_create_membership_success(self, session, test_organization, org_admin_headers, test_unaffiliated_user, test_planner_role):
        """Test successful membership creation"""
        membership_data = {
            "user_id": test_unaffiliated_user.id,
            "role_id": test_planner_role.id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 201
        created_membership = response.json()
        
        # Check response structure
        assert created_membership["user_id"] == test_unaffiliated_user.id
        assert created_membership["role_id"] == test_planner_role.id
        assert created_membership["organization_id"] == test_organization.id
        assert created_membership["invitation_status"] == "accepted"
        assert "id" in created_membership
        assert "created_date" in created_membership
        assert "updated_date" in created_membership
        
        # Verify membership was created in database
        db_membership = session.query(OrganizationMembership).filter_by(
            user_id=test_unaffiliated_user.id,
            organization_id=test_organization.id
        ).first()
        assert db_membership is not None
        assert db_membership.role_id == test_planner_role.id

    def test_create_membership_duplicate_user(self, test_organization, org_admin_headers, test_planner_user, test_viewer_role):
        """Test creating membership for user already in organization fails"""
        membership_data = {
            "user_id": test_planner_user.id,  # User already in organization
            "role_id": test_viewer_role.id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 400
        assert "already a member" in response.json()["detail"].lower()

    def test_create_membership_invalid_user(self, test_organization, org_admin_headers, test_planner_role):
        """Test creating membership with invalid user ID"""
        import uuid
        fake_user_id = str(uuid.uuid4())
        
        membership_data = {
            "user_id": fake_user_id,
            "role_id": test_planner_role.id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 400
        assert "user not found" in response.json()["detail"].lower()

    def test_create_membership_invalid_role(self, test_organization, org_admin_headers, test_unaffiliated_user):
        """Test creating membership with invalid role ID"""
        import uuid
        fake_role_id = str(uuid.uuid4())
        
        membership_data = {
            "user_id": test_unaffiliated_user.id,
            "role_id": fake_role_id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 400
        assert "role not found" in response.json()["detail"].lower()

    def test_create_membership_missing_required_fields(self, test_organization, org_admin_headers):
        """Test creating membership with missing required fields"""
        membership_data = {
            "user_id": "some-user-id"
            # Missing role_id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_membership_without_auth(self, test_organization, test_unaffiliated_user, test_planner_role):
        """Test that membership creation requires authentication"""
        membership_data = {
            "user_id": test_unaffiliated_user.id,
            "role_id": test_planner_role.id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/memberships",
            json=membership_data
        )
        
        assert response.status_code == 403

    def test_create_membership_forbidden_other_org(self, org_admin_headers, test_second_organization, test_unaffiliated_user, test_planner_role):
        """Test that org admin cannot create memberships in other organizations"""
        membership_data = {
            "user_id": test_unaffiliated_user.id,
            "role_id": test_planner_role.id
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_second_organization.id}/memberships",
            json=membership_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 403


class TestGetMembership:
    """Test GET /api/v1/organizations/{org_id}/memberships/{user_id} endpoint"""
    
    def test_get_membership_success(self, org_admin_headers, test_organization, test_planner_user):
        """Test successful retrieval of specific membership"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        membership = response.json()
        
        assert membership["user_id"] == test_planner_user.id
        assert membership["organization_id"] == test_organization.id
        assert membership["invitation_status"] == "accepted"
        assert "user" in membership
        assert "role" in membership

    def test_get_membership_not_found(self, org_admin_headers, test_organization, test_unaffiliated_user):
        """Test getting nonexistent membership"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_unaffiliated_user.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 404

    def test_get_membership_invalid_user_uuid(self, org_admin_headers, test_organization):
        """Test getting membership with invalid user UUID"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships/invalid-uuid",
            headers=org_admin_headers
        )
        
        assert response.status_code == 422

    def test_get_membership_without_auth(self, test_organization, test_planner_user):
        """Test that getting membership requires authentication"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}"
        )
        
        assert response.status_code == 403


class TestUpdateMembership:
    """Test PUT /api/v1/organizations/{org_id}/memberships/{user_id} endpoint"""
    
    def test_update_membership_role_success(self, session, org_admin_headers, test_organization, test_planner_user, test_viewer_role):
        """Test successful membership role update"""
        update_data = {
            "role_id": test_viewer_role.id
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        updated_membership = response.json()
        
        assert updated_membership["role_id"] == test_viewer_role.id
        assert updated_membership["user_id"] == test_planner_user.id

    def test_update_membership_status_success(self, session, org_admin_headers, test_organization, test_planner_user):
        """Test successful membership status update"""
        update_data = {
            "invitation_status": "pending"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        updated_membership = response.json()
        
        assert updated_membership["invitation_status"] == "pending"

    def test_update_membership_invalid_role(self, org_admin_headers, test_organization, test_planner_user):
        """Test updating membership with invalid role ID"""
        import uuid
        fake_role_id = str(uuid.uuid4())
        
        update_data = {
            "role_id": fake_role_id
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 400
        assert "role not found" in response.json()["detail"].lower()

    def test_update_membership_not_found(self, org_admin_headers, test_organization, test_unaffiliated_user, test_viewer_role):
        """Test updating nonexistent membership"""
        update_data = {
            "role_id": test_viewer_role.id
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_unaffiliated_user.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 404

    def test_update_membership_without_auth(self, test_organization, test_planner_user, test_viewer_role):
        """Test that updating membership requires authentication"""
        update_data = {
            "role_id": test_viewer_role.id
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_planner_user.id}",
            json=update_data
        )
        
        assert response.status_code == 403


class TestDeleteMembership:
    """Test DELETE /api/v1/organizations/{org_id}/memberships/{user_id} endpoint"""
    
    def test_delete_membership_success(self, session, org_admin_headers, test_organization, test_viewer_user):
        """Test successful membership deletion"""
        user_id = test_viewer_user.id
        
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/memberships/{user_id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Membership removed successfully"
        
        # Verify membership is deleted from database
        deleted_membership = session.query(OrganizationMembership).filter_by(
            user_id=user_id,
            organization_id=test_organization.id
        ).first()
        assert deleted_membership is None

    def test_delete_membership_not_found(self, org_admin_headers, test_organization, test_unaffiliated_user):
        """Test deleting nonexistent membership"""
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_unaffiliated_user.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 404

    def test_delete_membership_without_auth(self, test_organization, test_viewer_user):
        """Test that deleting membership requires authentication"""
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/memberships/{test_viewer_user.id}"
        )
        
        assert response.status_code == 403

    def test_delete_membership_forbidden_other_org(self, org_admin_headers, test_second_organization, test_planner_user):
        """Test that org admin cannot delete memberships from other organizations"""
        response = client.delete(
            f"/api/v1/organizations/{test_second_organization.id}/memberships/{test_planner_user.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__])