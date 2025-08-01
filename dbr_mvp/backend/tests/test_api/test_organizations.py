# tests/test_api/test_organizations.py
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
def test_super_admin_user(session, test_super_admin_role):
    """Create a test super admin user"""
    user = User(
        username="super_admin",
        email="superadmin@test.com",
        password_hash=hash_password("superadmin123"),
        display_name="Super Admin User",
        active_status=True,
        system_role_id=test_super_admin_role.id
    )
    session.add(user)
    session.commit()
    return user


@pytest.fixture
def super_admin_headers(session, test_super_admin_user):
    """Get super admin authentication headers"""
    login_response = client.post("/api/v1/auth/login", json={
        "username": "super_admin",
        "password": "superadmin123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
def test_second_organization(session):
    """Create a second test organization"""
    org = Organization(
        name="Second Test Organization",
        description="Second test org for organization API testing",
        status=OrganizationStatus.ACTIVE,
        contact_email="second@example.com",
        country="CA"
    )
    session.add(org)
    session.commit()
    return org


class TestGetOrganizations:
    """Test GET /api/v1/organizations endpoint"""
    
    def test_get_organizations_success_super_admin(self, session, super_admin_headers, test_organization, test_second_organization):
        """Test successful retrieval of organizations list by super admin"""
        response = client.get(
            "/api/v1/organizations",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        organizations = response.json()
        assert isinstance(organizations, list)
        assert len(organizations) >= 2  # At least our two test organizations
        
        # Check organization structure
        org_names = [org["name"] for org in organizations]
        assert "Test Organization" in org_names
        assert "Second Test Organization" in org_names
        
        # Check required fields
        for org in organizations:
            assert "id" in org
            assert "name" in org
            assert "description" in org
            assert "status" in org
            assert "contact_email" in org
            assert "country" in org
            assert "subscription_level" in org
            assert "created_date" in org
            assert "updated_date" in org

    def test_get_organizations_filtered_by_status(self, super_admin_headers, test_organization):
        """Test filtering organizations by status"""
        response = client.get(
            "/api/v1/organizations",
            params={"status": "active"},
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        organizations = response.json()
        
        # All returned organizations should have active status
        for org in organizations:
            assert org["status"] == "active"

    def test_get_organizations_without_auth(self):
        """Test that organizations endpoint requires authentication"""
        response = client.get("/api/v1/organizations")
        
        assert response.status_code == 403

    def test_get_organizations_org_admin_limited_access(self, org_admin_headers, test_organization):
        """Test that org admin can only see their own organization"""
        response = client.get(
            "/api/v1/organizations",
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        organizations = response.json()
        
        # Org admin should only see their own organization
        assert len(organizations) == 1
        assert organizations[0]["name"] == "Test Organization"


class TestCreateOrganization:
    """Test POST /api/v1/organizations endpoint"""
    
    def test_create_organization_success(self, session, super_admin_headers):
        """Test successful organization creation by super admin"""
        org_data = {
            "name": "New Test Organization",
            "description": "A newly created test organization",
            "contact_email": "neworg@test.com",
            "country": "US",
            "subscription_level": "premium"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=org_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 201
        created_org = response.json()
        
        # Check response structure
        assert created_org["name"] == "New Test Organization"
        assert created_org["description"] == "A newly created test organization"
        assert created_org["contact_email"] == "neworg@test.com"
        assert created_org["country"] == "US"
        assert created_org["subscription_level"] == "premium"
        assert created_org["status"] == "active"  # Default status
        assert "id" in created_org
        assert "created_date" in created_org
        assert "updated_date" in created_org
        
        # Verify organization was created in database
        db_org = session.query(Organization).filter_by(name="New Test Organization").first()
        assert db_org is not None
        assert db_org.contact_email == "neworg@test.com"

    def test_create_organization_duplicate_name(self, super_admin_headers, test_organization):
        """Test creating organization with duplicate name fails"""
        org_data = {
            "name": test_organization.name,  # Use existing name
            "description": "Duplicate name organization",
            "contact_email": "duplicate@test.com",
            "country": "US"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=org_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        assert "name already exists" in response.json()["detail"].lower()

    def test_create_organization_missing_required_fields(self, super_admin_headers):
        """Test creating organization with missing required fields"""
        org_data = {
            "name": "Incomplete Organization"
            # Missing description, contact_email, country
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=org_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 422  # Validation error

    def test_create_organization_org_admin_forbidden(self, org_admin_headers):
        """Test that org admin cannot create organizations"""
        org_data = {
            "name": "Unauthorized Organization",
            "description": "Should not be created",
            "contact_email": "unauthorized@test.com",
            "country": "US"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=org_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 403

    def test_create_organization_without_auth(self):
        """Test that organization creation requires authentication"""
        org_data = {
            "name": "No Auth Organization",
            "description": "Should not be created",
            "contact_email": "noauth@test.com",
            "country": "US"
        }
        
        response = client.post("/api/v1/organizations", json=org_data)
        
        assert response.status_code == 403


class TestGetOrganization:
    """Test GET /api/v1/organizations/{org_id} endpoint"""
    
    def test_get_organization_success_super_admin(self, super_admin_headers, test_organization):
        """Test successful retrieval of specific organization by super admin"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        org = response.json()
        
        assert org["id"] == test_organization.id
        assert org["name"] == test_organization.name
        assert org["description"] == test_organization.description
        assert org["status"] == test_organization.status.value
        assert org["contact_email"] == test_organization.contact_email
        assert org["country"] == test_organization.country

    def test_get_organization_success_org_admin(self, org_admin_headers, test_organization):
        """Test successful retrieval of own organization by org admin"""
        response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        org = response.json()
        assert org["id"] == test_organization.id

    def test_get_organization_forbidden_other_org(self, org_admin_headers, test_second_organization):
        """Test that org admin cannot access other organizations"""
        response = client.get(
            f"/api/v1/organizations/{test_second_organization.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 403

    def test_get_organization_not_found(self, super_admin_headers):
        """Test getting nonexistent organization"""
        import uuid
        fake_org_id = str(uuid.uuid4())
        
        response = client.get(
            f"/api/v1/organizations/{fake_org_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 404

    def test_get_organization_invalid_uuid(self, super_admin_headers):
        """Test getting organization with invalid UUID"""
        response = client.get(
            "/api/v1/organizations/invalid-uuid",
            headers=super_admin_headers
        )
        
        assert response.status_code == 422

    def test_get_organization_without_auth(self, test_organization):
        """Test that getting organization requires authentication"""
        response = client.get(f"/api/v1/organizations/{test_organization.id}")
        
        assert response.status_code == 403


class TestUpdateOrganization:
    """Test PUT /api/v1/organizations/{org_id} endpoint"""
    
    def test_update_organization_success_super_admin(self, session, super_admin_headers, test_organization):
        """Test successful organization update by super admin"""
        update_data = {
            "description": "Updated organization description",
            "subscription_level": "enterprise"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        updated_org = response.json()
        
        assert updated_org["description"] == "Updated organization description"
        assert updated_org["subscription_level"] == "enterprise"
        assert updated_org["name"] == test_organization.name  # Unchanged

    def test_update_organization_success_org_admin(self, session, org_admin_headers, test_organization):
        """Test successful organization update by org admin"""
        update_data = {
            "description": "Updated by org admin"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 200
        updated_org = response.json()
        assert updated_org["description"] == "Updated by org admin"

    def test_update_organization_forbidden_other_org(self, org_admin_headers, test_second_organization):
        """Test that org admin cannot update other organizations"""
        update_data = {
            "description": "Unauthorized update"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_second_organization.id}",
            json=update_data,
            headers=org_admin_headers
        )
        
        assert response.status_code == 403

    def test_update_organization_duplicate_name(self, super_admin_headers, test_organization, test_second_organization):
        """Test updating organization with duplicate name fails"""
        update_data = {
            "name": test_second_organization.name  # Use existing name
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 400
        assert "name already exists" in response.json()["detail"].lower()

    def test_update_organization_not_found(self, super_admin_headers):
        """Test updating nonexistent organization"""
        import uuid
        fake_org_id = str(uuid.uuid4())
        
        update_data = {"description": "New Description"}
        
        response = client.put(
            f"/api/v1/organizations/{fake_org_id}",
            json=update_data,
            headers=super_admin_headers
        )
        
        assert response.status_code == 404

    def test_update_organization_without_auth(self, test_organization):
        """Test that updating organization requires authentication"""
        update_data = {"description": "Unauthorized Update"}
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}",
            json=update_data
        )
        
        assert response.status_code == 403


class TestDeleteOrganization:
    """Test DELETE /api/v1/organizations/{org_id} endpoint"""
    
    def test_delete_organization_success_super_admin(self, session, super_admin_headers, test_second_organization):
        """Test successful organization deletion by super admin"""
        org_id = test_second_organization.id
        
        response = client.delete(
            f"/api/v1/organizations/{org_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Organization deleted successfully"

    def test_delete_organization_forbidden_org_admin(self, org_admin_headers, test_organization):
        """Test that org admin cannot delete organizations"""
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}",
            headers=org_admin_headers
        )
        
        assert response.status_code == 403

    def test_delete_organization_not_found(self, super_admin_headers):
        """Test deleting nonexistent organization"""
        import uuid
        fake_org_id = str(uuid.uuid4())
        
        response = client.delete(
            f"/api/v1/organizations/{fake_org_id}",
            headers=super_admin_headers
        )
        
        assert response.status_code == 404

    def test_delete_organization_without_auth(self, test_organization):
        """Test that deleting organization requires authentication"""
        response = client.delete(f"/api/v1/organizations/{test_organization.id}")
        
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__])