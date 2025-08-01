# src/dbr/api/memberships.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, ConfigDict
import uuid

from dbr.core.database import get_db
from dbr.models.user import User
from dbr.models.organization import Organization
from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
from dbr.models.role import Role, RoleName

# Import auth dependency
try:
    from dbr.api.auth import get_current_user
except ImportError:
    # Handle circular import during testing
    def get_current_user():
        from dbr.api.auth import get_current_user as _get_current_user
        return _get_current_user


router = APIRouter(prefix="/organizations", tags=["Memberships"])


# Pydantic schemas for request/response
class MembershipCreate(BaseModel):
    """Schema for creating a new membership"""
    user_id: str = Field(..., description="User ID to add to organization")
    role_id: str = Field(..., description="Role ID to assign to user")


class MembershipUpdate(BaseModel):
    """Schema for updating a membership"""
    role_id: Optional[str] = Field(None, description="Role ID to assign to user")
    invitation_status: Optional[str] = Field(None, description="Invitation status")


class UserInfo(BaseModel):
    """Schema for user information in membership response"""
    id: str
    username: str
    email: str
    display_name: str
    active_status: bool


class RoleInfo(BaseModel):
    """Schema for role information in membership response"""
    id: str
    name: str
    description: str


class MembershipResponse(BaseModel):
    """Schema for membership response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    organization_id: str
    user_id: str
    role_id: str
    invitation_status: str
    invited_by_user_id: str
    joined_date: Optional[str]
    created_date: str
    updated_date: str
    user: UserInfo
    role: RoleInfo


def _convert_membership_to_response(membership: OrganizationMembership) -> MembershipResponse:
    """Convert OrganizationMembership model to MembershipResponse"""
    return MembershipResponse(
        id=membership.id,
        organization_id=membership.organization_id,
        user_id=membership.user_id,
        role_id=membership.role_id,
        invitation_status=membership.invitation_status.value,
        invited_by_user_id=membership.invited_by_user_id,
        joined_date=membership.joined_date.isoformat() if membership.joined_date else None,
        created_date=membership.created_date.isoformat(),
        updated_date=membership.updated_date.isoformat(),
        user=UserInfo(
            id=membership.user.id,
            username=membership.user.username,
            email=membership.user.email,
            display_name=membership.user.display_name,
            active_status=membership.user.active_status
        ),
        role=RoleInfo(
            id=membership.role.id,
            name=membership.role.name.value,
            description=membership.role.description
        )
    )


def _check_organization_membership_access(current_user: User, db: Session, org_id: str) -> bool:
    """Check if user has access to manage organization memberships"""
    # Get user's system role
    user_role = db.query(Role).filter_by(id=current_user.system_role_id).first()
    
    # Super Admin has access to all organizations
    if user_role and user_role.name == RoleName.SUPER_ADMIN:
        return True
    
    # Check if user is an admin of this organization
    membership = db.query(OrganizationMembership).filter_by(
        user_id=current_user.id,
        organization_id=org_id,
        invitation_status=InvitationStatus.ACCEPTED
    ).first()
    
    if membership:
        # Check if user has admin role in this organization
        member_role = db.query(Role).filter_by(id=membership.role_id).first()
        return member_role and member_role.name in [RoleName.ORGANIZATION_ADMIN, RoleName.SUPER_ADMIN]
    
    return False


@router.get("/{org_id}/memberships", response_model=List[MembershipResponse])
async def get_memberships(
    org_id: str,
    role_id: Optional[str] = Query(None, description="Filter by role ID"),
    status: Optional[str] = Query(None, description="Filter by invitation status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of organization memberships"""
    
    # Validate UUID format
    try:
        uuid.UUID(org_id)
        if role_id:
            uuid.UUID(role_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if user has access to this organization's memberships
    if not _check_organization_membership_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to this organization's memberships"
        )
    
    # Build query with eager loading of user and role data
    query = db.query(OrganizationMembership).options(
        joinedload(OrganizationMembership.user),
        joinedload(OrganizationMembership.role)
    ).filter(OrganizationMembership.organization_id == org_id)
    
    # Apply filters
    if role_id:
        query = query.filter(OrganizationMembership.role_id == role_id)
    
    if status:
        try:
            status_enum = InvitationStatus(status)
            query = query.filter(OrganizationMembership.invitation_status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status value. Must be one of: {[s.value for s in InvitationStatus]}"
            )
    
    memberships = query.all()
    
    return [_convert_membership_to_response(membership) for membership in memberships]


@router.post("/{org_id}/memberships", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def create_membership(
    org_id: str,
    membership_data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization membership"""
    
    # Validate UUID formats
    try:
        uuid.UUID(org_id)
        uuid.UUID(membership_data.user_id)
        uuid.UUID(membership_data.role_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if user has access to manage this organization's memberships
    if not _check_organization_membership_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to manage this organization's memberships"
        )
    
    # Validate user exists
    user = db.query(User).filter_by(id=membership_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User not found"
        )
    
    # Validate role exists
    role = db.query(Role).filter_by(id=membership_data.role_id).first()
    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role not found"
        )
    
    # Check if user is already a member of this organization
    existing_membership = db.query(OrganizationMembership).filter_by(
        user_id=membership_data.user_id,
        organization_id=org_id
    ).first()
    if existing_membership:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this organization"
        )
    
    # Create new membership
    try:
        from datetime import datetime, timezone
        
        new_membership = OrganizationMembership(
            organization_id=org_id,
            user_id=membership_data.user_id,
            role_id=membership_data.role_id,
            invitation_status=InvitationStatus.ACCEPTED,
            invited_by_user_id=current_user.id,
            joined_date=datetime.now(timezone.utc)
        )
        
        db.add(new_membership)
        db.commit()
        db.refresh(new_membership)
        
        # Load the user and role data for response
        membership_with_relations = db.query(OrganizationMembership).options(
            joinedload(OrganizationMembership.user),
            joinedload(OrganizationMembership.role)
        ).filter_by(id=new_membership.id).first()
        
        return _convert_membership_to_response(membership_with_relations)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Membership creation failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating membership: {str(e)}"
        )


@router.get("/{org_id}/memberships/{user_id}", response_model=MembershipResponse)
async def get_membership(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific organization membership"""
    
    # Validate UUID formats
    try:
        uuid.UUID(org_id)
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if user has access to this organization's memberships
    if not _check_organization_membership_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to this organization's memberships"
        )
    
    # Get membership with user and role data
    membership = db.query(OrganizationMembership).options(
        joinedload(OrganizationMembership.user),
        joinedload(OrganizationMembership.role)
    ).filter_by(
        organization_id=org_id,
        user_id=user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail=f"Membership not found for user {user_id} in organization {org_id}"
        )
    
    return _convert_membership_to_response(membership)


@router.put("/{org_id}/memberships/{user_id}", response_model=MembershipResponse)
async def update_membership(
    org_id: str,
    user_id: str,
    membership_data: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an organization membership"""
    
    # Validate UUID formats
    try:
        uuid.UUID(org_id)
        uuid.UUID(user_id)
        if membership_data.role_id:
            uuid.UUID(membership_data.role_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if user has access to manage this organization's memberships
    if not _check_organization_membership_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to manage this organization's memberships"
        )
    
    # Get membership
    membership = db.query(OrganizationMembership).filter_by(
        organization_id=org_id,
        user_id=user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail=f"Membership not found for user {user_id} in organization {org_id}"
        )
    
    # Validate role if provided
    if membership_data.role_id:
        role = db.query(Role).filter_by(id=membership_data.role_id).first()
        if not role:
            raise HTTPException(
                status_code=400,
                detail="Role not found"
            )
    
    # Update membership fields
    try:
        update_data = membership_data.model_dump(exclude_unset=True)
        
        # Handle invitation status conversion
        if "invitation_status" in update_data:
            try:
                update_data["invitation_status"] = InvitationStatus(update_data["invitation_status"])
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in InvitationStatus]}"
                )
        
        for field, value in update_data.items():
            setattr(membership, field, value)
        
        db.commit()
        db.refresh(membership)
        
        # Load the user and role data for response
        membership_with_relations = db.query(OrganizationMembership).options(
            joinedload(OrganizationMembership.user),
            joinedload(OrganizationMembership.role)
        ).filter_by(id=membership.id).first()
        
        return _convert_membership_to_response(membership_with_relations)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Membership update failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating membership: {str(e)}"
        )


@router.delete("/{org_id}/memberships/{user_id}")
async def delete_membership(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an organization membership"""
    
    # Validate UUID formats
    try:
        uuid.UUID(org_id)
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check if user has access to manage this organization's memberships
    if not _check_organization_membership_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to manage this organization's memberships"
        )
    
    # Get membership
    membership = db.query(OrganizationMembership).filter_by(
        organization_id=org_id,
        user_id=user_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail=f"Membership not found for user {user_id} in organization {org_id}"
        )
    
    try:
        # Delete membership
        db.delete(membership)
        db.commit()
        
        return {"message": "Membership removed successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting membership: {str(e)}"
        )