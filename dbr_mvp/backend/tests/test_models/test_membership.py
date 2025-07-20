# tests/test_models/test_membership.py
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_user_organization_membership():
    """Test user-organization relationships"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create test organization
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic"
            )
            session.add(org)
            
            # Create test role
            role = Role(name=RoleName.PLANNER, description="Test Planner")
            session.add(role)
            session.commit()  # Commit role first to get ID
            
            # Create test user
            user = User(
                username="testuser",
                email="test@example.com",
                display_name="Test User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=role.id
            )
            session.add(user)
            session.commit()
            
            # Test: Users belong to default organization
            membership = OrganizationMembership(
                organization_id=org.id,
                user_id=user.id,
                role_id=role.id,
                invitation_status=InvitationStatus.ACCEPTED,
                invited_by_user_id=user.id,  # Self-invited for test
                joined_date=datetime.now(timezone.utc)
            )
            session.add(membership)
            session.commit()
            
            # Test: Role assignments work
            assert membership.organization_id == org.id
            assert membership.user_id == user.id
            assert membership.role_id == role.id
            assert membership.invitation_status == InvitationStatus.ACCEPTED
            
            # Test: Membership validation
            assert membership.id is not None
            assert isinstance(uuid.UUID(membership.id), uuid.UUID)
            assert membership.joined_date is not None
    finally:
        engine.dispose()


def test_permission_checking():
    """Test role-based permission system"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password
    from dbr.core.permissions import user_has_permission, Permission, get_user_role_in_org
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create test organization
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic"
            )
            session.add(org)
            
            # Create test roles
            admin_role = Role(name=RoleName.ORGANIZATION_ADMIN, description="Org Admin")
            worker_role = Role(name=RoleName.WORKER, description="Worker")
            session.add_all([admin_role, worker_role])
            session.commit()  # Commit roles first to get IDs
            
            # Create test users
            admin_user = User(
                username="admin",
                email="admin@example.com",
                display_name="Admin User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=admin_role.id
            )
            
            worker_user = User(
                username="worker",
                email="worker@example.com",
                display_name="Worker User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=worker_role.id
            )
            session.add_all([admin_user, worker_user])
            session.commit()
            
            # Create memberships
            admin_membership = OrganizationMembership(
                organization_id=org.id,
                user_id=admin_user.id,
                role_id=admin_role.id,
                invitation_status=InvitationStatus.ACCEPTED,
                invited_by_user_id=admin_user.id,
                joined_date=datetime.now(timezone.utc)
            )
            
            worker_membership = OrganizationMembership(
                organization_id=org.id,
                user_id=worker_user.id,
                role_id=worker_role.id,
                invitation_status=InvitationStatus.ACCEPTED,
                invited_by_user_id=admin_user.id,
                joined_date=datetime.now(timezone.utc)
            )
            session.add_all([admin_membership, worker_membership])
            session.commit()
            
            # Test: Users can perform role-appropriate actions
            assert user_has_permission(session, admin_user.id, org.id, Permission.MANAGE_USERS)
            assert not user_has_permission(session, worker_user.id, org.id, Permission.MANAGE_USERS)
            
            # Test: Users blocked from unauthorized actions
            assert not user_has_permission(session, worker_user.id, org.id, Permission.CREATE_WORK_ITEMS)
            assert user_has_permission(session, admin_user.id, org.id, Permission.CREATE_WORK_ITEMS)
            
            # Test: Role hierarchy respected
            admin_role_in_org = get_user_role_in_org(session, admin_user.id, org.id)
            worker_role_in_org = get_user_role_in_org(session, worker_user.id, org.id)
            
            assert admin_role_in_org == RoleName.ORGANIZATION_ADMIN
            assert worker_role_in_org == RoleName.WORKER
    finally:
        engine.dispose()


def test_invitation_status():
    """Test invitation status workflow"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.organization import Organization, OrganizationStatus
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create test data
            org = Organization(
                name="Test Organization",
                description="Test org",
                status=OrganizationStatus.ACTIVE,
                contact_email="test@org.com",
                country="US",
                subscription_level="basic"
            )
            
            role = Role(name=RoleName.VIEWER, description="Viewer")
            session.add_all([org, role])
            session.commit()  # Commit first to get IDs
            
            inviter = User(
                username="inviter",
                email="inviter@example.com",
                display_name="Inviter User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=role.id
            )
            
            invitee = User(
                username="invitee",
                email="invitee@example.com",
                display_name="Invitee User",
                password_hash=hash_password("password123"),
                active_status=True,
                system_role_id=role.id
            )
            
            session.add_all([inviter, invitee])
            session.commit()
            
            # Test: Pending invitation
            membership = OrganizationMembership(
                organization_id=org.id,
                user_id=invitee.id,
                role_id=role.id,
                invitation_status=InvitationStatus.PENDING,
                invited_by_user_id=inviter.id
            )
            session.add(membership)
            session.commit()
            
            assert membership.invitation_status == InvitationStatus.PENDING
            assert membership.joined_date is None
            
            # Test: Accept invitation
            membership.invitation_status = InvitationStatus.ACCEPTED
            membership.joined_date = datetime.now(timezone.utc)
            session.commit()
            
            assert membership.invitation_status == InvitationStatus.ACCEPTED
            assert membership.joined_date is not None
    finally:
        engine.dispose()


def test_default_organization_memberships():
    """Test linking test users to default organization"""
    from dbr.core.database import create_default_memberships
    from dbr.models.organization_membership import OrganizationMembership
    from dbr.models.organization import Organization
    from dbr.models.user import User
    from dbr.models.role import Role
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create test data using existing functions
            from dbr.core.database import create_system_roles, create_test_users, _create_default_organization
            
            # Create default org
            from dbr.models.organization import OrganizationStatus
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
            
            # Create roles and users
            roles = create_system_roles(session)
            users = create_test_users(session)
            
            # Test: Create default memberships
            memberships = create_default_memberships(session, default_org.id)
            
            assert len(memberships) == 5  # One for each test user
            
            # Test: All users are members of default organization
            for membership in memberships:
                assert membership.organization_id == default_org.id
                assert membership.invitation_status.value == "accepted"
                assert membership.joined_date is not None
            
            # Test: Users have correct roles in organization
            user_emails = [u.email for u in users]
            assert "admin@test.com" in user_emails
            assert "planner@test.com" in user_emails
    finally:
        engine.dispose()