# tests/test_models/test_user.py
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_create_test_users():
    """Test creation of test user accounts"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password, verify_password
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create roles first
            roles = []
            role_definitions = [
                (RoleName.SUPER_ADMIN, "Super Admin"),
                (RoleName.ORGANIZATION_ADMIN, "Org Admin"),
                (RoleName.PLANNER, "Planner"),
                (RoleName.WORKER, "Worker"),
                (RoleName.VIEWER, "Viewer"),
            ]
            
            for role_name, description in role_definitions:
                role = Role(name=role_name, description=description)
                session.add(role)
                roles.append(role)
            session.commit()
            
            # Test: Create users for each role
            test_users = [
                ("admin@test.com", "admin123", "Super Admin User", RoleName.SUPER_ADMIN),
                ("orgadmin@test.com", "orgadmin123", "Org Admin User", RoleName.ORGANIZATION_ADMIN),
                ("planner@test.com", "planner123", "Planner User", RoleName.PLANNER),
                ("worker@test.com", "worker123", "Worker User", RoleName.WORKER),
                ("viewer@test.com", "viewer123", "Viewer User", RoleName.VIEWER),
            ]
            
            created_users = []
            for email, password, display_name, role_name in test_users:
                # Test: Password hashing works
                hashed_password = hash_password(password)
                assert hashed_password != password
                assert verify_password(password, hashed_password)
                
                # Find the role
                role = session.query(Role).filter_by(name=role_name).first()
                assert role is not None
                
                user = User(
                    username=email.split('@')[0],
                    email=email,
                    display_name=display_name,
                    password_hash=hashed_password,
                    active_status=True,
                    system_role_id=role.id
                )
                session.add(user)
                created_users.append(user)
            
            session.commit()
            
            # Test: Users created successfully
            assert len(created_users) == 5
            for user in created_users:
                assert user.id is not None
                assert user.email is not None
                assert user.password_hash is not None
                assert user.system_role_id is not None
                assert isinstance(uuid.UUID(user.id), uuid.UUID)
    finally:
        engine.dispose()


def test_user_authentication():
    """Test user login functionality"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password, verify_password, authenticate_user
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create a test role
            role = Role(name=RoleName.PLANNER, description="Test Planner")
            session.add(role)
            session.commit()
            
            # Create a test user
            password = "testpassword123"
            hashed_password = hash_password(password)
            
            user = User(
                username="testuser",
                email="test@example.com",
                display_name="Test User",
                password_hash=hashed_password,
                active_status=True,
                system_role_id=role.id
            )
            session.add(user)
            session.commit()
            
            # Test: Valid credentials authenticate
            authenticated_user = authenticate_user(session, "test@example.com", password)
            assert authenticated_user is not None
            assert authenticated_user.email == "test@example.com"
            
            # Test: Invalid credentials rejected
            invalid_user = authenticate_user(session, "test@example.com", "wrongpassword")
            assert invalid_user is None
            
            invalid_email = authenticate_user(session, "wrong@example.com", password)
            assert invalid_email is None
            
            # Test: User roles accessible after auth
            assert authenticated_user.system_role_id == role.id
            user_role = session.query(Role).filter_by(id=authenticated_user.system_role_id).first()
            assert user_role.name == RoleName.PLANNER
    finally:
        engine.dispose()


def test_user_model_validation():
    """Test user model field validation"""
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    from dbr.core.security import hash_password
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create a test role
            role = Role(name=RoleName.VIEWER, description="Test Viewer")
            session.add(role)
            session.commit()
            
            # Test: Required fields validation
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
            
            # Test: User has all required attributes
            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.display_name == "Test User"
            assert user.password_hash is not None
            assert user.active_status is True
            assert user.system_role_id == role.id
            assert user.created_date is not None
            assert user.updated_date is not None
            
            # Test: Last login date is initially None
            assert user.last_login_date is None
            
            # Test: Can update last login date
            from datetime import timezone
            user.last_login_date = datetime.now(timezone.utc)
            session.commit()
            assert user.last_login_date is not None
    finally:
        engine.dispose()


def test_create_test_user_accounts():
    """Test creation of all test user accounts"""
    from dbr.core.database import create_test_users
    from dbr.models.user import User
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create roles first
            from dbr.core.database import create_system_roles
            roles = create_system_roles(session)
            
            # Test: Create test users for each role
            test_users = create_test_users(session)
            
            assert len(test_users) == 5
            
            # Test: Each role has a corresponding test user
            user_emails = [user.email for user in test_users]
            expected_emails = [
                "admin@test.com",
                "orgadmin@test.com", 
                "planner@test.com",
                "worker@test.com",
                "viewer@test.com"
            ]
            
            for email in expected_emails:
                assert email in user_emails
            
            # Test: Users are linked to correct roles
            admin_user = next(u for u in test_users if u.email == "admin@test.com")
            admin_role = session.query(Role).filter_by(id=admin_user.system_role_id).first()
            assert admin_role.name == RoleName.SUPER_ADMIN
    finally:
        engine.dispose()