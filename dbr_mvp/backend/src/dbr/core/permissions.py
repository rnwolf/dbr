# src/dbr/core/permissions.py
from enum import Enum
from dbr.models.role import RoleName


class Permission(Enum):
    """System permissions enumeration"""
    CREATE_ORGANIZATION = "create_organization"
    MANAGE_USERS = "manage_users"
    CREATE_WORK_ITEMS = "create_work_items"
    UPDATE_WORK_ITEMS = "update_work_items"
    ADVANCE_TIME = "advance_time"
    VIEW_REPORTS = "view_reports"
    MANAGE_SCHEDULES = "manage_schedules"


# Role permission matrix - defines what each role can do
ROLE_PERMISSIONS = {
    RoleName.SUPER_ADMIN: [
        Permission.CREATE_ORGANIZATION,
        Permission.MANAGE_USERS,
        Permission.CREATE_WORK_ITEMS,
        Permission.UPDATE_WORK_ITEMS,
        Permission.ADVANCE_TIME,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_SCHEDULES,
    ],
    RoleName.ORGANIZATION_ADMIN: [
        Permission.MANAGE_USERS,
        Permission.CREATE_WORK_ITEMS,
        Permission.UPDATE_WORK_ITEMS,
        Permission.ADVANCE_TIME,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_SCHEDULES,
    ],
    RoleName.PLANNER: [
        Permission.CREATE_WORK_ITEMS,
        Permission.UPDATE_WORK_ITEMS,
        Permission.ADVANCE_TIME,
        Permission.VIEW_REPORTS,
        Permission.MANAGE_SCHEDULES,
    ],
    RoleName.WORKER: [
        Permission.UPDATE_WORK_ITEMS,
        Permission.VIEW_REPORTS,
    ],
    RoleName.VIEWER: [
        Permission.VIEW_REPORTS,
    ],
}

# Role hierarchy levels (higher number = more permissions)
ROLE_LEVELS = {
    RoleName.SUPER_ADMIN: 5,
    RoleName.ORGANIZATION_ADMIN: 4,
    RoleName.PLANNER: 3,
    RoleName.WORKER: 2,
    RoleName.VIEWER: 1,
}


def has_permission(role_name: RoleName, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    if role_name not in ROLE_PERMISSIONS:
        return False
    
    return permission in ROLE_PERMISSIONS[role_name]


def get_role_level(role_name: RoleName) -> int:
    """Get the hierarchy level of a role"""
    return ROLE_LEVELS.get(role_name, 0)


def can_manage_role(manager_role: RoleName, target_role: RoleName) -> bool:
    """Check if a manager role can manage a target role"""
    return get_role_level(manager_role) > get_role_level(target_role)


def get_permissions_for_role(role_name: RoleName) -> list[Permission]:
    """Get all permissions for a specific role"""
    return ROLE_PERMISSIONS.get(role_name, [])


def user_has_permission(session, user_id: str, organization_id: str, permission: Permission) -> bool:
    """Check if a user has a specific permission within an organization"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.role import Role
    
    # Get user's membership in the organization
    membership = session.query(OrganizationMembership).filter_by(
        user_id=user_id,
        organization_id=organization_id,
        invitation_status=InvitationStatus.ACCEPTED
    ).first()
    
    if not membership:
        return False
    
    # Get the role
    role = session.query(Role).filter_by(id=membership.role_id).first()
    if not role:
        return False
    
    # Check if role has the permission
    return has_permission(role.name, permission)


def get_user_role_in_org(session, user_id: str, organization_id: str) -> RoleName:
    """Get a user's role within a specific organization"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.role import Role
    
    # Get user's membership in the organization
    membership = session.query(OrganizationMembership).filter_by(
        user_id=user_id,
        organization_id=organization_id,
        invitation_status=InvitationStatus.ACCEPTED
    ).first()
    
    if not membership:
        return None
    
    # Get the role
    role = session.query(Role).filter_by(id=membership.role_id).first()
    if not role:
        return None
    
    return role.name


def get_user_organizations(session, user_id: str) -> list:
    """Get all organizations a user is a member of"""
    from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
    from dbr.models.organization import Organization
    
    memberships = session.query(OrganizationMembership).filter_by(
        user_id=user_id,
        invitation_status=InvitationStatus.ACCEPTED
    ).all()
    
    organizations = []
    for membership in memberships:
        org = session.query(Organization).filter_by(id=membership.organization_id).first()
        if org:
            organizations.append(org)
    
    return organizations