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