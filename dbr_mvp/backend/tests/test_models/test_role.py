# tests/test_models/test_role.py
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid


def test_create_system_roles():
    """Test all 5 system roles created"""
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: Super Admin, Org Admin, Planner, Worker, Viewer
            expected_roles = [
                RoleName.SUPER_ADMIN,
                RoleName.ORGANIZATION_ADMIN,
                RoleName.PLANNER,
                RoleName.WORKER,
                RoleName.VIEWER
            ]
            
            created_roles = []
            for role_name in expected_roles:
                role = Role(
                    name=role_name,
                    description=f"System role: {role_name.value}"
                )
                session.add(role)
                created_roles.append(role)
            
            session.commit()
            
            # Test: Roles have correct permissions structure
            for role in created_roles:
                assert role.id is not None
                assert role.name in expected_roles
                assert role.description is not None
                assert isinstance(uuid.UUID(role.id), uuid.UUID)
            
            # Test: Role hierarchy validation
            super_admin = next(r for r in created_roles if r.name == RoleName.SUPER_ADMIN)
            org_admin = next(r for r in created_roles if r.name == RoleName.ORGANIZATION_ADMIN)
            planner = next(r for r in created_roles if r.name == RoleName.PLANNER)
            worker = next(r for r in created_roles if r.name == RoleName.WORKER)
            viewer = next(r for r in created_roles if r.name == RoleName.VIEWER)
            
            assert super_admin.name == RoleName.SUPER_ADMIN
            assert org_admin.name == RoleName.ORGANIZATION_ADMIN
            assert planner.name == RoleName.PLANNER
            assert worker.name == RoleName.WORKER
            assert viewer.name == RoleName.VIEWER
    finally:
        engine.dispose()


def test_role_permissions():
    """Test role permission validation"""
    from dbr.models.role import Role, RoleName
    from dbr.core.permissions import has_permission, Permission
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Create test roles
            super_admin = Role(name=RoleName.SUPER_ADMIN, description="Super Admin")
            org_admin = Role(name=RoleName.ORGANIZATION_ADMIN, description="Org Admin")
            planner = Role(name=RoleName.PLANNER, description="Planner")
            worker = Role(name=RoleName.WORKER, description="Worker")
            viewer = Role(name=RoleName.VIEWER, description="Viewer")
            
            session.add_all([super_admin, org_admin, planner, worker, viewer])
            session.commit()
            
            # Test: Each role has appropriate permissions
            # Super Admin can do everything
            assert has_permission(super_admin.name, Permission.CREATE_ORGANIZATION)
            assert has_permission(super_admin.name, Permission.MANAGE_USERS)
            assert has_permission(super_admin.name, Permission.CREATE_WORK_ITEMS)
            assert has_permission(super_admin.name, Permission.ADVANCE_TIME)
            assert has_permission(super_admin.name, Permission.VIEW_REPORTS)
            
            # Org Admin can manage organization but not create new orgs
            assert not has_permission(org_admin.name, Permission.CREATE_ORGANIZATION)
            assert has_permission(org_admin.name, Permission.MANAGE_USERS)
            assert has_permission(org_admin.name, Permission.CREATE_WORK_ITEMS)
            assert has_permission(org_admin.name, Permission.ADVANCE_TIME)
            assert has_permission(org_admin.name, Permission.VIEW_REPORTS)
            
            # Planner can create work items and schedules
            assert not has_permission(planner.name, Permission.CREATE_ORGANIZATION)
            assert not has_permission(planner.name, Permission.MANAGE_USERS)
            assert has_permission(planner.name, Permission.CREATE_WORK_ITEMS)
            assert has_permission(planner.name, Permission.ADVANCE_TIME)
            assert has_permission(planner.name, Permission.VIEW_REPORTS)
            
            # Worker can update work items but not create
            assert not has_permission(worker.name, Permission.CREATE_ORGANIZATION)
            assert not has_permission(worker.name, Permission.MANAGE_USERS)
            assert not has_permission(worker.name, Permission.CREATE_WORK_ITEMS)
            assert not has_permission(worker.name, Permission.ADVANCE_TIME)
            assert has_permission(worker.name, Permission.VIEW_REPORTS)
            
            # Viewer can only view
            assert not has_permission(viewer.name, Permission.CREATE_ORGANIZATION)
            assert not has_permission(viewer.name, Permission.MANAGE_USERS)
            assert not has_permission(viewer.name, Permission.CREATE_WORK_ITEMS)
            assert not has_permission(viewer.name, Permission.ADVANCE_TIME)
            assert has_permission(viewer.name, Permission.VIEW_REPORTS)
    finally:
        engine.dispose()


def test_role_hierarchy():
    """Test role hierarchy and inheritance"""
    from dbr.models.role import Role, RoleName
    from dbr.core.permissions import get_role_level
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        
        # Test: Permission inheritance (Org Admin > Planner > Worker > Viewer)
        assert get_role_level(RoleName.SUPER_ADMIN) > get_role_level(RoleName.ORGANIZATION_ADMIN)
        assert get_role_level(RoleName.ORGANIZATION_ADMIN) > get_role_level(RoleName.PLANNER)
        assert get_role_level(RoleName.PLANNER) > get_role_level(RoleName.WORKER)
        assert get_role_level(RoleName.WORKER) > get_role_level(RoleName.VIEWER)
        
        # Test: Role comparison
        assert get_role_level(RoleName.SUPER_ADMIN) == 5
        assert get_role_level(RoleName.ORGANIZATION_ADMIN) == 4
        assert get_role_level(RoleName.PLANNER) == 3
        assert get_role_level(RoleName.WORKER) == 2
        assert get_role_level(RoleName.VIEWER) == 1
    finally:
        engine.dispose()


def test_role_seed_data():
    """Test role seed data creation"""
    from dbr.core.database import create_system_roles
    from dbr.models.role import Role, RoleName
    from dbr.models.base import Base
    
    engine = create_engine("sqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Test: System roles can be created via seed function
            roles = create_system_roles(session)
            
            assert len(roles) == 5
            role_names = [role.name for role in roles]
            
            assert RoleName.SUPER_ADMIN in role_names
            assert RoleName.ORGANIZATION_ADMIN in role_names
            assert RoleName.PLANNER in role_names
            assert RoleName.WORKER in role_names
            assert RoleName.VIEWER in role_names
            
            # Test: Roles have proper descriptions
            for role in roles:
                assert role.description is not None
                assert len(role.description) > 0
    finally:
        engine.dispose()