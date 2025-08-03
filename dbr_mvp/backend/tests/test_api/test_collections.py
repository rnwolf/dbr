# tests/test_api/test_collections.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from dbr.main import app
from dbr.models.organization import Organization, OrganizationStatus
from dbr.models.collection import Collection, CollectionType, CollectionStatus
from dbr.models.role import Role, RoleName
from dbr.models.user import User
from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
from dbr.core.database import SessionLocal, create_tables
from dbr.core.security import hash_password
from dbr.api.auth import create_access_token

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def session():
    """Create a test database session"""
    create_tables()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_role(session):
    """Create a test role"""
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
def test_user(session, test_role):
    """Create a test user"""
    try:
        # Try to get existing user by username or email
        user = session.query(User).filter(
            (User.username == "testuser_collections") | 
            (User.email == "testuser_collections@example.com")
        ).first()
        
        if not user:
            # Create new user if it doesn't exist
            user = User(
                username="testuser_collections",
                email="testuser_collections@example.com",
                password_hash=hash_password("testpassword"),
                display_name="Test User Collections",
                active_status=True,
                system_role_id=test_role.id
            )
            session.add(user)
            session.commit()
        return user
    except Exception as e:
        # If there's any error, rollback and try again
        session.rollback()
        # Try to get existing user again after rollback
        user = session.query(User).filter(
            (User.username == "testuser_collections") | 
            (User.email == "testuser_collections@example.com")
        ).first()
        if user:
            return user
        raise e

@pytest.fixture
def test_membership(session, test_user, test_organization, test_role):
    """Create a test organization membership"""
    try:
        # Check if membership already exists
        existing_membership = session.query(OrganizationMembership).filter_by(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role_id=test_role.id
        ).first()
        
        if existing_membership:
            return existing_membership
        
        membership = OrganizationMembership(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role_id=test_role.id,
            invitation_status=InvitationStatus.ACCEPTED,
            invited_by_user_id=test_user.id  # Self-invited for testing purposes
        )
        session.add(membership)
        session.commit()
        return membership
    except Exception as e:
        # If there's any error, rollback and try again
        session.rollback()
        # Try to get existing membership again after rollback
        existing_membership = session.query(OrganizationMembership).filter_by(
            organization_id=test_organization.id,
            user_id=test_user.id,
            role_id=test_role.id
        ).first()
        if existing_membership:
            return existing_membership
        raise e

@pytest.fixture
def auth_headers(test_user):
    """Create auth headers for a test user"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_organization(session):
    """Create a test organization"""
    org = Organization(
        name="Test Organization",
        description="Test org for collection API testing",
        status=OrganizationStatus.ACTIVE,
        contact_email="test@example.com",
        country="US"
    )
    session.add(org)
    session.commit()
    return org

@pytest.fixture
def test_collection(session, test_organization):
    """Create a test collection"""
    collection = Collection(
        organization_id=test_organization.id,
        name="Test Collection",
        description="A description for test collection",
        type=CollectionType.PROJECT,
        status=CollectionStatus.ACTIVE,
        estimated_sales_price=10000.0,
        estimated_variable_cost=3000.0
    )
    session.add(collection)
    session.commit()
    return collection


def test_create_collection_api(client, session, test_organization, test_membership, auth_headers):
    """Test collection creation via API"""
    # Test: POST /collections creates collection
    # Test: Returns created collection with ID
    
    collection_data = {
        "organization_id": test_organization.id,
        "name": "New Collection",
        "description": "A new collection created via API",
        "type": "Epic",
        "status": "planning",
        "estimated_sales_price": 5000.0,
        "estimated_variable_cost": 1000.0
    }
    
    response = client.post("/api/v1/collections", json=collection_data, headers=auth_headers)
    
    assert response.status_code == 201
    created_collection = response.json()
    
    # Verify response structure
    assert "id" in created_collection
    assert created_collection["name"] == "New Collection"
    assert created_collection["organization_id"] == test_organization.id
    assert created_collection["status"] == "planning"
    assert created_collection["type"] == "Epic"
    assert created_collection["estimated_sales_price"] == 5000.0
    assert "created_date" in created_collection

def test_get_collections_api(client, session, test_organization, test_collection, test_membership, auth_headers):
    """Test retrieving collections via API"""
    # Test: GET /collections retrieves collections
    
    response = client.get(f"/api/v1/collections?organization_id={test_organization.id}", headers=auth_headers)
    
    assert response.status_code == 200
    collections = response.json()
    assert len(collections) >= 1  # At least the test_collection should exist
    
    # Verify collection structure
    for coll in collections:
        assert "id" in coll
        assert "name" in coll
        assert "organization_id" in coll
        assert coll["organization_id"] == test_organization.id
    

def test_update_collection_api(client, session, test_organization, test_collection, test_membership, auth_headers):
    """Test updating a collection via API"""
    # Test: PUT /collections/{id} updates collection
    
    update_data = {
        "name": "Updated Collection",
        "status": "active"
    }
    
    response = client.put(
        f"/api/v1/collections/{test_collection.id}?organization_id={test_organization.id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    updated_collection = response.json()
    
    # Verify updated structure
    assert updated_collection["id"] == test_collection.id
    assert updated_collection["name"] == "Updated Collection"
    assert updated_collection["status"] == "active"

def test_delete_collection_api(client, session, test_organization, test_collection, test_membership, auth_headers):
    """Test deleting a collection via API"""
    # Test: DELETE /collections/{id} deletes collection
    
    response = client.delete(f"/api/v1/collections/{test_collection.id}?organization_id={test_organization.id}", headers=auth_headers)
    
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/api/v1/collections/{test_collection.id}?organization_id={test_organization.id}", headers=auth_headers)
    assert response.status_code == 404


def test_collection_access_permissions(client, session, test_organization, test_collection, test_user, auth_headers):
    """Test access permissions for collection management via API"""
    # Test: Cannot create collection without membership
    collection_data = {
        "organization_id": "invalid_org",
        "name": "Unauthorized Collection",
    }
    
    response = client.post("/api/v1/collections", json=collection_data, headers=auth_headers)
    assert response.status_code == 403

    # Remove user's membership and verify access denial
    # Get all memberships for the user and delete them
    memberships = session.query(OrganizationMembership).filter_by(user_id=test_user.id).all()
    for membership in memberships:
        session.delete(membership)
    session.commit()
    
    response = client.get(f"/api/v1/collections?organization_id={test_organization.id}", headers=auth_headers)
    assert response.status_code == 403

    response = client.post("/api/v1/collections", json=collection_data, headers=auth_headers)
    assert response.status_code == 403
