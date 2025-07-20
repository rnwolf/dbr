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
    _create_default_organization()
    _create_system_roles()
    _create_test_users()


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