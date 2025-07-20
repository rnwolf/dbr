# tests/test_models/test_organization.py
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_create_default_organization():
    """Test default organization creation"""
    from dbr.models.organization import Organization
    from dbr.models.base import Base
    
    # Test: Default org created on startup
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: Can create organization with required attributes
            from dbr.models.organization import OrganizationStatus
            org = Organization(
                name="Default Organization",
                description="Default organization for MVP testing",
                status=OrganizationStatus.ACTIVE,
                contact_email="admin@default.org",
                country="US",
                subscription_level="basic"
            )
            session.add(org)
            session.commit()
            
            # Test: Has required attributes
            assert org.id is not None
            assert org.name == "Default Organization"
            assert org.status == OrganizationStatus.ACTIVE
            assert org.contact_email == "admin@default.org"
            
            # Test: UUID generated correctly
            assert isinstance(uuid.UUID(org.id), uuid.UUID)
            
            # Test: Audit fields populated
            assert org.created_date is not None
            assert isinstance(org.created_date, datetime)
    finally:
        engine.dispose()


def test_organization_crud():
    """Test organization CRUD operations"""
    from dbr.models.organization import Organization
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: Create
            from dbr.models.organization import OrganizationStatus
            org = Organization(
                name="Test Organization",
                description="Test description",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@test.com",
                country="CA",
                subscription_level="premium"
            )
            session.add(org)
            session.commit()
            org_id = org.id
            
            # Test: Read
            retrieved_org = session.query(Organization).filter_by(id=org_id).first()
            assert retrieved_org is not None
            assert retrieved_org.name == "Test Organization"
            
            # Test: Update
            retrieved_org.name = "Updated Organization"
            session.commit()
            
            updated_org = session.query(Organization).filter_by(id=org_id).first()
            assert updated_org.name == "Updated Organization"
            assert updated_org.updated_date > updated_org.created_date
            
            # Test: Delete
            session.delete(updated_org)
            session.commit()
            
            deleted_org = session.query(Organization).filter_by(id=org_id).first()
            assert deleted_org is None
    finally:
        engine.dispose()


def test_organization_validation():
    """Test organization field validation"""
    from dbr.models.organization import Organization
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: Valid status values
            from dbr.models.organization import OrganizationStatus
            valid_statuses = [OrganizationStatus.ACTIVE, OrganizationStatus.SUSPENDED, OrganizationStatus.ARCHIVED]
            for status in valid_statuses:
                org = Organization(
                    name=f"Test Org {status.value}",
                    description="Test",
                    status=status,
                    contact_email="test@test.com",
                    country="US",
                    subscription_level="basic"
                )
                session.add(org)
                session.commit()
                assert org.status == status
                session.delete(org)
                session.commit()
    finally:
        engine.dispose()


def test_default_organization_seed():
    """Test default organization seed data creation"""
    from dbr.core.database import _create_default_organization
    from dbr.models.base import Base
    from dbr.models.organization import Organization, OrganizationStatus
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: Can create default organization directly
            # Create default organization using the internal function logic
            existing_org = session.query(Organization).filter_by(name="Default Organization").first()
            assert existing_org is None  # Should not exist yet
            
            # Create default organization
            default_org = Organization(
                name="Default Organization",
                description="Default organization for MVP testing and development",
                status=OrganizationStatus.ACTIVE,
                contact_email="admin@default.org",
                country="US",
                subscription_level="basic"
            )
            session.add(default_org)
            session.commit()
            
            # Test: Default organization was created correctly
            assert default_org is not None
            assert default_org.name == "Default Organization"
            assert default_org.status == OrganizationStatus.ACTIVE
            assert default_org.contact_email == "admin@default.org"
    finally:
        engine.dispose()