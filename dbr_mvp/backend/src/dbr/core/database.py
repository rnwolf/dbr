# src/dbr/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dbr.models.base import Base
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dbr.db")

# Create engine with SQLite-specific configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # Set to False in production
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create tables"""
    create_tables()
    default_org = _create_default_organization()
    _create_system_roles()
    _create_test_users()
    _create_default_memberships(default_org.id if default_org else None)


def get_default_organization():
    """Get the default organization for MVP"""
    from dbr.models.organization import Organization
    
    db = SessionLocal()
    try:
        # Try to get existing default organization
        default_org = db.query(Organization).filter_by(name="Default Organization").first()
        if default_org is None:
            # Create default organization if it doesn't exist
            default_org = _create_default_organization()
        return default_org
    finally:
        db.close()


def _create_default_organization():
    """Create the default organization for MVP"""
    from dbr.models.organization import Organization
    
    db = SessionLocal()
    try:
        # Check if default org already exists
        existing_org = db.query(Organization).filter_by(name="Default Organization").first()
        if existing_org:
            return existing_org
            
        # Create new default organization
        from dbr.models.organization import OrganizationStatus
        default_org = Organization(
            name="Default Organization",
            description="Default organization for MVP testing and development",
            status=OrganizationStatus.ACTIVE,
            contact_email="admin@default.org",
            country="US",
            subscription_level="basic"
        )
        db.add(default_org)
        db.commit()
        db.refresh(default_org)
        return default_org
    finally:
        db.close()


def create_system_roles(session=None):
    """Create all system roles - can be called with existing session for testing"""
    from dbr.models.role import Role, RoleName
    
    if session is None:
        db = SessionLocal()
        try:
            return _create_roles_in_session(db)
        finally:
            db.close()
    else:
        return _create_roles_in_session(session)


def _create_system_roles():
    """Create system roles during database initialization"""
    from dbr.models.role import Role, RoleName
    
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles > 0:
            return
            
        _create_roles_in_session(db)
    finally:
        db.close()


def _create_roles_in_session(session):
    """Create roles within a given session"""
    from dbr.models.role import Role, RoleName
    
    role_definitions = [
        (RoleName.SUPER_ADMIN, "System administrator with full access to all features and organizations"),
        (RoleName.ORGANIZATION_ADMIN, "Organization administrator who can manage users and settings within their organization"),
        (RoleName.PLANNER, "Can create and manage work items, schedules, and advance time"),
        (RoleName.WORKER, "Can update work items and view reports"),
        (RoleName.VIEWER, "Read-only access to view reports and dashboards"),
    ]
    
    created_roles = []
    for role_name, description in role_definitions:
        # Check if role already exists
        existing_role = session.query(Role).filter_by(name=role_name).first()
        if existing_role:
            created_roles.append(existing_role)
            continue
            
        role = Role(
            name=role_name,
            description=description
        )
        session.add(role)
        created_roles.append(role)
    
    session.commit()
    return created_roles


def create_test_users(session=None):
    """Create test user accounts - can be called with existing session for testing"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.core.security import hash_password
    
    if session is None:
        db = SessionLocal()
        try:
            return _create_users_in_session(db)
        finally:
            db.close()
    else:
        return _create_users_in_session(session)


def _create_test_users():
    """Create test users during database initialization"""
    from dbr.models.user import User
    
    db = SessionLocal()
    try:
        # Check if users already exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            return
            
        _create_users_in_session(db)
    finally:
        db.close()


def _create_users_in_session(session):
    """Create test users within a given session"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.core.security import hash_password
    
    # Test user definitions
    test_user_definitions = [
        ("admin", "admin@test.com", "admin123", "Super Admin User", RoleName.SUPER_ADMIN),
        ("orgadmin", "orgadmin@test.com", "orgadmin123", "Org Admin User", RoleName.ORGANIZATION_ADMIN),
        ("planner", "planner@test.com", "planner123", "Planner User", RoleName.PLANNER),
        ("worker", "worker@test.com", "worker123", "Worker User", RoleName.WORKER),
        ("viewer", "viewer@test.com", "viewer123", "Viewer User", RoleName.VIEWER),
    ]
    
    created_users = []
    for username, email, password, display_name, role_name in test_user_definitions:
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            created_users.append(existing_user)
            continue
        
        # Find the role
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            continue  # Skip if role doesn't exist
        
        # Create user
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            password_hash=hash_password(password),
            active_status=True,
            system_role_id=role.id
        )
        session.add(user)
        created_users.append(user)
    
    session.commit()
    return created_users


def create_default_memberships(session=None, organization_id=None):
    """Create memberships linking test users to default organization"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.user import User
    from dbr.models.role import Role
    from datetime import datetime, timezone
    
    if session is None:
        db = SessionLocal()
        try:
            return _create_memberships_in_session(db, organization_id)
        finally:
            db.close()
    else:
        return _create_memberships_in_session(session, organization_id)


def _create_default_memberships(organization_id=None):
    """Create default memberships during database initialization"""
    if organization_id is None:
        return
        
    db = SessionLocal()
    try:
        # Check if memberships already exist
        from dbr.models.organization_membership import OrganizationMembership
        existing_memberships = db.query(OrganizationMembership).filter_by(organization_id=organization_id).count()
        if existing_memberships > 0:
            return
            
        _create_memberships_in_session(db, organization_id)
    finally:
        db.close()


def _create_memberships_in_session(session, organization_id):
    """Create memberships within a given session"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.user import User
    from dbr.models.role import Role
    from datetime import datetime, timezone
    
    if organization_id is None:
        return []
    
    # Get all test users
    test_users = session.query(User).filter(User.email.like('%@test.com')).all()
    
    created_memberships = []
    admin_user = None
    
    # Find admin user to use as inviter
    for user in test_users:
        if user.email == "admin@test.com":
            admin_user = user
            break
    
    if not admin_user:
        return []
    
    for user in test_users:
        # Check if membership already exists
        existing_membership = session.query(OrganizationMembership).filter_by(
            organization_id=organization_id,
            user_id=user.id
        ).first()
        
        if existing_membership:
            created_memberships.append(existing_membership)
            continue
        
        # Create membership
        membership = OrganizationMembership(
            organization_id=organization_id,
            user_id=user.id,
            role_id=user.system_role_id,  # Use the user's system role
            invitation_status=InvitationStatus.ACCEPTED,
            invited_by_user_id=admin_user.id,
            joined_date=datetime.now(timezone.utc)
        )
        session.add(membership)
        created_memberships.append(membership)
    
    session.commit()
    return created_memberships