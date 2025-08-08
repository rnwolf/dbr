# src/dbr/core/database.py
from sqlalchemy import create_engine, text
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
    """Create all database tables and perform lightweight migrations for SQLite"""
    Base.metadata.create_all(bind=engine)
    # Lightweight migrations: add columns if missing (SQLite online)
    if DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            # Check existing columns in work_items
            try:
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(work_items);")).fetchall()]
            except Exception:
                cols = []
            # Add responsible_user_id if missing
            if "responsible_user_id" not in cols:
                try:
                    conn.execute(text("ALTER TABLE work_items ADD COLUMN responsible_user_id TEXT"))
                except Exception:
                    pass
            # Add url if missing
            if "url" not in cols:
                try:
                    conn.execute(text("ALTER TABLE work_items ADD COLUMN url TEXT"))
                except Exception:
                    pass


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """Get a database session (for direct use, not as dependency)"""
    return SessionLocal()


def init_db():
    """Initialize database - create tables"""
    create_tables()
    default_org = _create_default_organization()
    _create_system_roles()
    _create_test_users()
    _create_default_memberships(default_org.id if default_org else None)
    
    # Create additional organizations and comprehensive seed data
    additional_org_ids = _create_additional_organizations()
    _create_additional_users()
    
    # Get organization IDs instead of objects to avoid session issues
    default_org_id = default_org.id if default_org else None
    additional_org_ids = additional_org_ids or []  # Ensure it's a list
    
    _create_multi_organization_memberships_by_id(default_org_id, additional_org_ids)
    _create_test_ccrs_by_id(default_org_id, additional_org_ids)
    _create_test_board_configs_by_id(default_org_id, additional_org_ids)
    _create_test_collections_by_id(default_org_id, additional_org_ids)
    _create_test_work_items_by_id(default_org_id, additional_org_ids)
    _create_test_schedules_by_id(default_org_id, additional_org_ids)


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


def _create_additional_organizations():
    """Create additional organizations for multi-tenant testing"""
    from dbr.models.organization import Organization, OrganizationStatus
    
    db = SessionLocal()
    try:
        additional_org_definitions = [
            {
                "name": "TechCorp Solutions",
                "description": "Technology consulting and software development company",
                "status": OrganizationStatus.ACTIVE,
                "contact_email": "admin@techcorp.com",
                "country": "US",
                "subscription_level": "premium"
            },
            {
                "name": "StartupVenture Inc",
                "description": "Early-stage startup focused on innovative solutions",
                "status": OrganizationStatus.ACTIVE,
                "contact_email": "founder@startupventure.com", 
                "country": "CA",
                "subscription_level": "basic"
            }
        ]
        
        created_org_ids = []
        for org_def in additional_org_definitions:
            # Check if organization already exists
            existing_org = db.query(Organization).filter_by(name=org_def["name"]).first()
            if existing_org:
                created_org_ids.append(existing_org.id)
                continue
                
            # Create new organization
            org = Organization(
                name=org_def["name"],
                description=org_def["description"],
                status=org_def["status"],
                contact_email=org_def["contact_email"],
                country=org_def["country"],
                subscription_level=org_def["subscription_level"]
            )
            db.add(org)
            db.flush()  # Flush to get the ID before commit
            created_org_ids.append(org.id)
        
        db.commit()
        return created_org_ids
    finally:
        db.close()


def _create_additional_users():
    """Create additional users for multi-organization testing"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.core.security import hash_password
    
    db = SessionLocal()
    try:
        additional_user_definitions = [
            # TechCorp Solutions Users
            ("techcorp_admin", "admin@techcorp.com", "techcorp123", "TechCorp Admin", RoleName.ORGANIZATION_ADMIN),
            ("techcorp_planner", "planner@techcorp.com", "techcorp123", "TechCorp Planner", RoleName.PLANNER),
            ("techcorp_worker1", "worker1@techcorp.com", "techcorp123", "TechCorp Senior Developer", RoleName.WORKER),
            ("techcorp_worker2", "worker2@techcorp.com", "techcorp123", "TechCorp Frontend Developer", RoleName.WORKER),
            ("techcorp_worker3", "worker3@techcorp.com", "techcorp123", "TechCorp Backend Developer", RoleName.WORKER),
            ("techcorp_worker4", "worker4@techcorp.com", "techcorp123", "TechCorp QA Engineer", RoleName.WORKER),
            
            # StartupVenture Inc Users  
            ("startup_founder", "founder@startupventure.com", "startup123", "Startup Founder", RoleName.ORGANIZATION_ADMIN),
            ("startup_dev", "dev@startupventure.com", "startup123", "Startup Lead Developer", RoleName.PLANNER),
            ("startup_worker1", "worker1@startupventure.com", "startup123", "Startup Full-Stack Dev", RoleName.WORKER),
            ("startup_worker2", "worker2@startupventure.com", "startup123", "Startup UI/UX Designer", RoleName.WORKER),
            
            # Default Organization Additional Workers
            ("default_worker2", "worker2@test.com", "default123", "Default Frontend Developer", RoleName.WORKER),
            ("default_worker3", "worker3@test.com", "default123", "Default Backend Developer", RoleName.WORKER),
            ("default_worker4", "worker4@test.com", "default123", "Default QA Tester", RoleName.WORKER),
            ("default_worker5", "worker5@test.com", "default123", "Default DevOps Engineer", RoleName.WORKER),
            
            # Cross-Organization Users
            ("consultant", "consultant@freelance.com", "consultant123", "External Consultant", RoleName.WORKER),
            ("contractor", "contractor@external.com", "contractor123", "External Contractor", RoleName.WORKER),
            
            # Users with NO organization membership (for testing access denial)
            ("outsider", "outsider@external.com", "outsider123", "External User", RoleName.VIEWER),
            ("prospect", "prospect@potential.com", "prospect123", "Potential Client", RoleName.VIEWER),
        ]
        
        created_users = []
        for username, email, password, display_name, role_name in additional_user_definitions:
            # Check if user already exists
            existing_user = db.query(User).filter_by(email=email).first()
            if existing_user:
                created_users.append(existing_user)
                continue
            
            # Find the role
            role = db.query(Role).filter_by(name=role_name).first()
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
            db.add(user)
            created_users.append(user)
        
        db.commit()
        return created_users
    finally:
        db.close()


def _create_multi_organization_memberships_by_id(default_org_id, additional_org_ids):
    """Create memberships linking users to multiple organizations"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.organization import Organization
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from datetime import datetime, timezone
    
    db = SessionLocal()
    try:
        # Get organizations by ID and name
        techcorp_org = None
        startup_org = None
        
        for org_id in additional_org_ids:
            org = db.query(Organization).filter_by(id=org_id).first()
            if org and org.name == "TechCorp Solutions":
                techcorp_org = org
            elif org and org.name == "StartupVenture Inc":
                startup_org = org
        
        if not techcorp_org or not startup_org:
            return []
        
        # Get admin user for inviter reference
        admin_user = db.query(User).filter_by(email="admin@test.com").first()
        if not admin_user:
            return []
        
        # Define membership mappings: (org_name, user_email, role_name)
        membership_definitions = [
            # TechCorp Solutions memberships
            ("TechCorp Solutions", "admin@test.com", RoleName.SUPER_ADMIN),  # Super admin has access
            ("TechCorp Solutions", "admin@techcorp.com", RoleName.ORGANIZATION_ADMIN),
            ("TechCorp Solutions", "planner@techcorp.com", RoleName.PLANNER), 
            ("TechCorp Solutions", "worker1@techcorp.com", RoleName.WORKER),
            ("TechCorp Solutions", "worker2@techcorp.com", RoleName.WORKER),
            ("TechCorp Solutions", "worker3@techcorp.com", RoleName.WORKER),
            ("TechCorp Solutions", "worker4@techcorp.com", RoleName.WORKER),
            ("TechCorp Solutions", "consultant@freelance.com", RoleName.WORKER),  # Cross-org user
            
            # StartupVenture Inc memberships
            ("StartupVenture Inc", "admin@test.com", RoleName.SUPER_ADMIN),  # Super admin has access
            ("StartupVenture Inc", "founder@startupventure.com", RoleName.ORGANIZATION_ADMIN),
            ("StartupVenture Inc", "dev@startupventure.com", RoleName.PLANNER),
            ("StartupVenture Inc", "worker1@startupventure.com", RoleName.WORKER),
            ("StartupVenture Inc", "worker2@startupventure.com", RoleName.WORKER),
            ("StartupVenture Inc", "contractor@external.com", RoleName.WORKER),  # Cross-org user
            
            # Default Organization additional memberships
            ("Default Organization", "worker2@test.com", RoleName.WORKER),
            ("Default Organization", "worker3@test.com", RoleName.WORKER),
            ("Default Organization", "worker4@test.com", RoleName.WORKER),
            ("Default Organization", "worker5@test.com", RoleName.WORKER),
            ("Default Organization", "consultant@freelance.com", RoleName.WORKER),  # Cross-org user
        ]
        
        created_memberships = []
        for org_name, user_email, role_name in membership_definitions:
            # Get organization
            if org_name == "Default Organization":
                org = db.query(Organization).filter_by(id=default_org_id).first() if default_org_id else None
            elif org_name == "TechCorp Solutions":
                org = techcorp_org
            elif org_name == "StartupVenture Inc":
                org = startup_org
            else:
                continue
            
            if not org:
                continue
            
            # Get user and role
            user = db.query(User).filter_by(email=user_email).first()
            role = db.query(Role).filter_by(name=role_name).first()
            
            if not user or not role:
                continue
            
            # Check if membership already exists
            existing_membership = db.query(OrganizationMembership).filter_by(
                organization_id=org.id,
                user_id=user.id
            ).first()
            
            if existing_membership:
                created_memberships.append(existing_membership)
                continue
            
            # Create membership
            membership = OrganizationMembership(
                organization_id=org.id,
                user_id=user.id,
                role_id=role.id,
                invitation_status=InvitationStatus.ACCEPTED,
                invited_by_user_id=admin_user.id,
                joined_date=datetime.now(timezone.utc)
            )
            db.add(membership)
            created_memberships.append(membership)
        
        db.commit()
        return created_memberships
    finally:
        db.close()


def _create_test_ccrs_by_id(default_org_id, additional_org_ids):
    """Create CCRs for testing across organizations"""
    from dbr.models.ccr import CCR, CCRType
    from dbr.models.organization import Organization
    
    db = SessionLocal()
    try:
        # Get organizations by ID and name
        techcorp_org_id = None
        startup_org_id = None
        
        for org_id in additional_org_ids:
            org = db.query(Organization).filter_by(id=org_id).first()
            if org and org.name == "TechCorp Solutions":
                techcorp_org_id = org_id
            elif org and org.name == "StartupVenture Inc":
                startup_org_id = org_id
        
        ccr_definitions = [
            # Default Organization CCRs
            {
                "organization_id": default_org_id,
                "name": "Development Team",
                "description": "Software development team with full-stack capabilities",
                "ccr_type": CCRType.TEAM_BASED,
                "capacity_per_time_unit": 40.0,
                "time_unit": "week"
            },
            {
                "organization_id": default_org_id,
                "name": "QA Testing",
                "description": "Quality assurance and testing team",
                "ccr_type": CCRType.SKILL_BASED,
                "capacity_per_time_unit": 20.0,
                "time_unit": "week"
            },
            {
                "organization_id": default_org_id,
                "name": "DevOps Pipeline",
                "description": "CI/CD pipeline and deployment infrastructure",
                "ccr_type": CCRType.EQUIPMENT_BASED,
                "capacity_per_time_unit": 10.0,
                "time_unit": "week"
            },
            {
                "organization_id": default_org_id,
                "name": "UI/UX Design",
                "description": "User interface and experience design team",
                "ccr_type": CCRType.SKILL_BASED,
                "capacity_per_time_unit": 15.0,
                "time_unit": "week"
            },
        ]
        
        # Add TechCorp CCRs if organization exists
        if techcorp_org_id:
            ccr_definitions.extend([
                {
                    "organization_id": techcorp_org_id,
                    "name": "Senior Developers",
                    "description": "Senior development team for enterprise solutions",
                    "ccr_type": CCRType.SKILL_BASED,
                    "capacity_per_time_unit": 60.0,
                    "time_unit": "week"
                },
                {
                    "organization_id": techcorp_org_id,
                    "name": "Architecture Review",
                    "description": "Technical architecture review and approval process",
                    "ccr_type": CCRType.SKILL_BASED,
                    "capacity_per_time_unit": 8.0,
                    "time_unit": "week"
                },
                {
                    "organization_id": techcorp_org_id,
                    "name": "Client Deployment",
                    "description": "Client-specific deployment and configuration",
                    "ccr_type": CCRType.EQUIPMENT_BASED,
                    "capacity_per_time_unit": 12.0,
                    "time_unit": "week"
                },
            ])
        
        # Add StartupVenture CCRs if organization exists
        if startup_org_id:
            ccr_definitions.extend([
                {
                    "organization_id": startup_org_id,
                    "name": "Full-Stack Developer",
                    "description": "Single full-stack developer (startup constraint)",
                    "ccr_type": CCRType.SKILL_BASED,
                    "capacity_per_time_unit": 35.0,
                    "time_unit": "week"
                },
                {
                    "organization_id": startup_org_id,
                    "name": "Founder Review",
                    "description": "Founder approval for major features",
                    "ccr_type": CCRType.SKILL_BASED,
                    "capacity_per_time_unit": 5.0,
                    "time_unit": "week"
                }
            ])
        
        created_ccrs = []
        for ccr_def in ccr_definitions:
            # Check if CCR already exists
            existing_ccr = db.query(CCR).filter_by(
                organization_id=ccr_def["organization_id"],
                name=ccr_def["name"]
            ).first()
            
            if existing_ccr:
                created_ccrs.append(existing_ccr)
                continue
            
            # Create CCR
            ccr = CCR(
                organization_id=ccr_def["organization_id"],
                name=ccr_def["name"],
                description=ccr_def["description"],
                ccr_type=ccr_def["ccr_type"],
                capacity_per_time_unit=ccr_def["capacity_per_time_unit"],
                time_unit=ccr_def["time_unit"],
                is_active=True
            )
            db.add(ccr)
            created_ccrs.append(ccr)
        
        db.commit()
        return created_ccrs
    finally:
        db.close()


def _create_test_board_configs_by_id(default_org_id, additional_org_ids):
    """Create board configurations for testing - simplified implementation"""
    # Implementing as stub for now to avoid session complexity
    return []


def _create_test_collections_by_id(default_org_id, additional_org_ids):
    """Create collections for testing - simplified implementation"""
    # Implementing as stub for now to avoid session complexity
    return []


def _create_test_work_items_by_id(default_org_id, additional_org_ids):
    """Create work items for testing with representative fields including responsible_user_id and url"""
    from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
    from dbr.models.user import User
    from dbr.models.collection import Collection

    db = SessionLocal()
    try:
        if not default_org_id:
            return []
        # Pick some users to assign
        planner_user = db.query(User).filter_by(email="planner@test.com").first()
        worker_user = db.query(User).filter_by(email="worker@test.com").first()
        # Create a couple of sample work items if none exist yet
        existing = db.query(WorkItem).filter_by(organization_id=default_org_id).count()
        created_items = []
        if existing == 0:
            wi_defs = [
                {
                    "organization_id": default_org_id,
                    "collection_id": None,
                    "title": "Implement user authentication",
                    "description": "Add JWT-based auth and session handling",
                    "status": WorkItemStatus.READY,
                    "priority": WorkItemPriority.HIGH,
                    "responsible_user_id": planner_user.id if planner_user else None,
                    "url": "https://github.com/example/repo/issues/1",
                    "estimated_total_hours": 16.0,
                    "ccr_hours_required": {"Development Team": 12.0, "QA Testing": 4.0},
                    "estimated_sales_price": 5000.0,
                    "estimated_variable_cost": 1500.0,
                    "tasks": [
                        {"id": 1, "title": "Design login page", "completed": True},
                        {"id": 2, "title": "Implement backend endpoints", "completed": False},
                    ],
                },
                {
                    "organization_id": default_org_id,
                    "collection_id": None,
                    "title": "Create documentation site",
                    "description": "Set up docs with MkDocs",
                    "status": WorkItemStatus.BACKLOG,
                    "priority": WorkItemPriority.MEDIUM,
                    "responsible_user_id": worker_user.id if worker_user else None,
                    "url": "https://example.com/docs",
                    "estimated_total_hours": 8.0,
                    "ccr_hours_required": {"Development Team": 6.0, "QA Testing": 2.0},
                    "estimated_sales_price": 2000.0,
                    "estimated_variable_cost": 600.0,
                    "tasks": [
                        {"id": 1, "title": "Create docs skeleton", "completed": False},
                    ],
                },
            ]
            for d in wi_defs:
                wi = WorkItem(
                    organization_id=d["organization_id"],
                    collection_id=d["collection_id"],
                    title=d["title"],
                    description=d["description"],
                    status=d["status"],
                    priority=d["priority"],
                    responsible_user_id=d["responsible_user_id"],
                    url=d["url"],
                    estimated_total_hours=d["estimated_total_hours"],
                    ccr_hours_required=d["ccr_hours_required"],
                    estimated_sales_price=d["estimated_sales_price"],
                    estimated_variable_cost=d["estimated_variable_cost"],
                    tasks=d["tasks"],
                )
                db.add(wi)
                created_items.append(wi)
            db.commit()
        return created_items
    finally:
        db.close()


def _create_test_schedules_by_id(default_org_id, additional_org_ids):
    """Create schedules for testing - simplified implementation"""
    # Implementing as stub for now to avoid session complexity
    return []


def _create_test_board_configs(default_org, additional_orgs):
    """Create board configurations for testing"""
    from dbr.models.board_config import BoardConfig
    from dbr.models.ccr import CCR
    
    db = SessionLocal()
    try:
        # Get organizations by name for easier reference
        techcorp_org = next((org for org in additional_orgs if org.name == "TechCorp Solutions"), None)
        startup_org = next((org for org in additional_orgs if org.name == "StartupVenture Inc"), None)
        
        # Get CCRs for board configurations
        dev_team_ccr = db.query(CCR).filter_by(organization_id=default_org.id, name="Development Team").first()
        qa_testing_ccr = db.query(CCR).filter_by(organization_id=default_org.id, name="QA Testing").first()
        
        board_config_definitions = []
        
        # Default Organization Boards
        if dev_team_ccr:
            board_config_definitions.append({
                "organization_id": default_org.id,
                "name": "Main Development Board",
                "description": "Primary DBR board for development workflow",
                "ccr_id": dev_team_ccr.id,
                "pre_constraint_buffer_size": 5,
                "post_constraint_buffer_size": 3,
                "time_unit": "week"
            })
        
        if qa_testing_ccr:
            board_config_definitions.append({
                "organization_id": default_org.id,
                "name": "QA Testing Board",
                "description": "DBR board focused on QA testing workflow",
                "ccr_id": qa_testing_ccr.id,
                "pre_constraint_buffer_size": 3,
                "post_constraint_buffer_size": 2,
                "time_unit": "week"
            })
        
        # TechCorp Boards
        if techcorp_org:
            senior_dev_ccr = db.query(CCR).filter_by(organization_id=techcorp_org.id, name="Senior Developers").first()
            arch_review_ccr = db.query(CCR).filter_by(organization_id=techcorp_org.id, name="Architecture Review").first()
            
            if senior_dev_ccr:
                board_config_definitions.append({
                    "organization_id": techcorp_org.id,
                    "name": "Enterprise Development Board",
                    "description": "DBR board for enterprise client projects",
                    "ccr_id": senior_dev_ccr.id,
                    "pre_constraint_buffer_size": 4,
                    "post_constraint_buffer_size": 2,
                    "time_unit": "week"
                })
            
            if arch_review_ccr:
                board_config_definitions.append({
                    "organization_id": techcorp_org.id,
                    "name": "Architecture Review Board",
                    "description": "DBR board for architecture review process",
                    "ccr_id": arch_review_ccr.id,
                    "pre_constraint_buffer_size": 6,
                    "post_constraint_buffer_size": 1,
                    "time_unit": "week"
                })
        
        # StartupVenture Boards
        if startup_org:
            fullstack_ccr = db.query(CCR).filter_by(organization_id=startup_org.id, name="Full-Stack Developer").first()
            
            if fullstack_ccr:
                board_config_definitions.append({
                    "organization_id": startup_org.id,
                    "name": "MVP Development Board",
                    "description": "DBR board for MVP feature development",
                    "ccr_id": fullstack_ccr.id,
                    "pre_constraint_buffer_size": 3,
                    "post_constraint_buffer_size": 2,
                    "time_unit": "week"
                })
        
        created_boards = []
        for board_def in board_config_definitions:
            # Check if board config already exists
            existing_board = db.query(BoardConfig).filter_by(
                organization_id=board_def["organization_id"],
                name=board_def["name"]
            ).first()
            
            if existing_board:
                created_boards.append(existing_board)
                continue
            
            # Create board config
            board = BoardConfig(
                organization_id=board_def["organization_id"],
                name=board_def["name"],
                description=board_def["description"],
                ccr_id=board_def["ccr_id"],
                pre_constraint_buffer_size=board_def["pre_constraint_buffer_size"],
                post_constraint_buffer_size=board_def["post_constraint_buffer_size"],
                time_unit=board_def["time_unit"],
                is_active=True
            )
            db.add(board)
            created_boards.append(board)
        
        db.commit()
        return created_boards
    finally:
        db.close()


def _create_test_collections(default_org, additional_orgs):
    """Create collections for testing across organizations"""
    from dbr.models.collection import Collection, CollectionStatus
    from dbr.models.user import User
    
    db = SessionLocal()
    try:
        # Get organizations by name for easier reference
        techcorp_org = next((org for org in additional_orgs if org.name == "TechCorp Solutions"), None)
        startup_org = next((org for org in additional_orgs if org.name == "StartupVenture Inc"), None)
        
        # Get users for ownership
        planner_user = db.query(User).filter_by(email="planner@test.com").first()
        orgadmin_user = db.query(User).filter_by(email="orgadmin@test.com").first()
        techcorp_planner = db.query(User).filter_by(email="planner@techcorp.com").first()
        techcorp_admin = db.query(User).filter_by(email="admin@techcorp.com").first()
        startup_founder = db.query(User).filter_by(email="founder@startupventure.com").first()
        startup_dev = db.query(User).filter_by(email="dev@startupventure.com").first()
        
        collection_definitions = [
            # Default Organization Collections
            {
                "organization_id": default_org.id,
                "name": "Customer Portal Enhancement",
                "description": "Enhance customer portal with new features and improved UX",
                "status": CollectionStatus.ACTIVE,
                "owner_user_id": planner_user.id if planner_user else None,
                "estimated_sales_price": 50000.0,
                "estimated_variable_cost": 15000.0,
                "url": "https://github.com/defaultorg/customer-portal"
            },
            {
                "organization_id": default_org.id,
                "name": "Mobile App Development",
                "description": "Develop native mobile application for iOS and Android",
                "status": CollectionStatus.PLANNING,
                "owner_user_id": planner_user.id if planner_user else None,
                "estimated_sales_price": 75000.0,
                "estimated_variable_cost": 25000.0,
                "url": "https://github.com/defaultorg/mobile-app"
            },
            {
                "organization_id": default_org.id,
                "name": "API Integration Project",
                "description": "Integrate with third-party APIs for enhanced functionality",
                "status": CollectionStatus.ACTIVE,
                "owner_user_id": orgadmin_user.id if orgadmin_user else None,
                "estimated_sales_price": 30000.0,
                "estimated_variable_cost": 10000.0,
                "url": "https://github.com/defaultorg/api-integration"
            },
            {
                "organization_id": default_org.id,
                "name": "Security Audit Implementation",
                "description": "Implement security improvements based on audit findings",
                "status": CollectionStatus.ON_HOLD,
                "owner_user_id": orgadmin_user.id if orgadmin_user else None,
                "estimated_sales_price": 20000.0,
                "estimated_variable_cost": 8000.0,
                "url": "https://github.com/defaultorg/security-audit"
            },
        ]
        
        # Add TechCorp Collections
        if techcorp_org:
            collection_definitions.extend([
                {
                    "organization_id": techcorp_org.id,
                    "name": "Enterprise CRM System",
                    "description": "Custom CRM solution for large enterprise client",
                    "status": CollectionStatus.ACTIVE,
                    "owner_user_id": techcorp_planner.id if techcorp_planner else None,
                    "estimated_sales_price": 250000.0,
                    "estimated_variable_cost": 80000.0,
                    "url": "https://github.com/techcorp/enterprise-crm"
                },
                {
                    "organization_id": techcorp_org.id,
                    "name": "Cloud Migration Project",
                    "description": "Migrate legacy systems to cloud infrastructure",
                    "status": CollectionStatus.ACTIVE,
                    "owner_user_id": techcorp_admin.id if techcorp_admin else None,
                    "estimated_sales_price": 180000.0,
                    "estimated_variable_cost": 60000.0,
                    "url": "https://github.com/techcorp/cloud-migration"
                },
                {
                    "organization_id": techcorp_org.id,
                    "name": "Microservices Architecture",
                    "description": "Refactor monolith to microservices architecture",
                    "status": CollectionStatus.PLANNING,
                    "owner_user_id": techcorp_planner.id if techcorp_planner else None,
                    "estimated_sales_price": 320000.0,
                    "estimated_variable_cost": 120000.0,
                    "url": "https://github.com/techcorp/microservices"
                },
            ])
        
        # Add StartupVenture Collections
        if startup_org:
            collection_definitions.extend([
                {
                    "organization_id": startup_org.id,
                    "name": "MVP Core Features",
                    "description": "Essential features for minimum viable product launch",
                    "status": CollectionStatus.ACTIVE,
                    "owner_user_id": startup_founder.id if startup_founder else None,
                    "estimated_sales_price": 15000.0,
                    "estimated_variable_cost": 5000.0,
                    "url": "https://github.com/startupventure/mvp-core"
                },
                {
                    "organization_id": startup_org.id,
                    "name": "User Onboarding Flow",
                    "description": "Streamlined user registration and onboarding process",
                    "status": CollectionStatus.PLANNING,
                    "owner_user_id": startup_dev.id if startup_dev else None,
                    "estimated_sales_price": 8000.0,
                    "estimated_variable_cost": 3000.0,
                    "url": "https://github.com/startupventure/onboarding"
                },
                {
                    "organization_id": startup_org.id,
                    "name": "Analytics Dashboard",
                    "description": "Basic analytics and reporting for early users",
                    "status": CollectionStatus.COMPLETED,
                    "owner_user_id": startup_dev.id if startup_dev else None,
                    "estimated_sales_price": 5000.0,
                    "estimated_variable_cost": 2000.0,
                    "url": "https://github.com/startupventure/analytics"
                }
            ])
        
        created_collections = []
        for coll_def in collection_definitions:
            # Check if collection already exists
            existing_collection = db.query(Collection).filter_by(
                organization_id=coll_def["organization_id"],
                name=coll_def["name"]
            ).first()
            
            if existing_collection:
                created_collections.append(existing_collection)
                continue
            
            # Create collection
            collection = Collection(
                organization_id=coll_def["organization_id"],
                name=coll_def["name"],
                description=coll_def["description"],
                status=coll_def["status"],
                owner_user_id=coll_def["owner_user_id"],
                estimated_sales_price=coll_def["estimated_sales_price"],
                estimated_variable_cost=coll_def["estimated_variable_cost"],
                url=coll_def["url"]
            )
            db.add(collection)
            created_collections.append(collection)
        
        db.commit()
        return created_collections
    finally:
        db.close()


def _create_test_work_items(default_org, additional_orgs):
    """Create work items with user assignments for testing"""
    # This is a complex function - implementing as stub for now
    # Will need to create work items with proper user assignments and tasks
    return []


def _create_test_schedules(default_org, additional_orgs):
    """Create schedules for testing"""
    # This is a complex function - implementing as stub for now
    # Will need to create schedules with work items in different buffer positions
    return []