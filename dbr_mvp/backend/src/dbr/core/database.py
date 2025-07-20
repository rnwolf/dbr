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