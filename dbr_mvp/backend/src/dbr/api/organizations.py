# src/dbr/api/organizations.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, ConfigDict
import uuid

from dbr.core.database import get_db
from dbr.models.user import User
from dbr.models.organization import Organization, OrganizationStatus
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


router = APIRouter(prefix="/organizations", tags=["Organizations"])


# Pydantic schemas for request/response
class OrganizationCreate(BaseModel):
    """Schema for creating a new organization"""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")
    contact_email: str = Field(..., description="Contact email address")
    country: str = Field(..., min_length=2, max_length=2, description="ISO country code")
    subscription_level: str = Field(default="basic", description="Subscription level")


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Organization name")
    description: Optional[str] = Field(None, max_length=1000, description="Organization description")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    country: Optional[str] = Field(None, min_length=2, max_length=2, description="ISO country code")
    subscription_level: Optional[str] = Field(None, description="Subscription level")
    status: Optional[str] = Field(None, description="Organization status")


class OrganizationResponse(BaseModel):
    """Schema for organization response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str]
    status: str
    contact_email: str
    country: str
    subscription_level: str
    default_board_id: Optional[str]
    created_date: str
    updated_date: str


def _convert_organization_to_response(org: Organization) -> OrganizationResponse:
    """Convert Organization model to OrganizationResponse"""
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        description=org.description,
        status=org.status.value,
        contact_email=org.contact_email,
        country=org.country,
        subscription_level=org.subscription_level,
        default_board_id=org.default_board_id,
        created_date=org.created_date.isoformat(),
        updated_date=org.updated_date.isoformat()
    )


def _check_organization_access(current_user: User, db: Session, org_id: str = None) -> bool:
    """Check if user has access to organization operations"""
    # Get user's system role
    user_role = db.query(Role).filter_by(id=current_user.system_role_id).first()
    
    # Super Admin has access to all organizations
    if user_role and user_role.name == RoleName.SUPER_ADMIN:
        return True
    
    # For specific organization operations, check membership
    if org_id:
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


def _get_user_accessible_organizations(current_user: User, db: Session) -> Optional[List[str]]:
    """Get list of organization IDs the user can access"""
    # Get user's system role
    user_role = db.query(Role).filter_by(id=current_user.system_role_id).first()
    
    # Super Admin can access all organizations
    if user_role and user_role.name == RoleName.SUPER_ADMIN:
        return None  # None means all organizations
    
    # Get organizations where user is a member
    memberships = db.query(OrganizationMembership).filter_by(
        user_id=current_user.id,
        invitation_status=InvitationStatus.ACCEPTED
    ).all()
    
    return [membership.organization_id for membership in memberships]


@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    status: Optional[str] = Query(None, description="Filter by organization status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of organizations (filtered by user permissions)"""
    
    # Get organizations the user can access
    accessible_org_ids = _get_user_accessible_organizations(current_user, db)
    
    # Build query
    query = db.query(Organization)
    
    # Apply organization access filter
    if accessible_org_ids is not None:  # Not Super Admin
        if not accessible_org_ids:  # No accessible organizations
            return []
        query = query.filter(Organization.id.in_(accessible_org_ids))
    
    # Apply status filter if provided
    if status:
        try:
            status_enum = OrganizationStatus(status)
            query = query.filter(Organization.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid status value. Must be one of: {[s.value for s in OrganizationStatus]}"
            )
    
    organizations = query.all()
    
    return [_convert_organization_to_response(org) for org in organizations]


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization (Super Admin only)"""
    
    # Check if user is Super Admin
    user_role = db.query(Role).filter_by(id=current_user.system_role_id).first()
    if not user_role or user_role.name != RoleName.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only Super Admins can create organizations"
        )
    
    # Check for duplicate name
    existing_org = db.query(Organization).filter_by(name=org_data.name).first()
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Organization name already exists"
        )
    
    # Create new organization
    try:
        new_org = Organization(
            name=org_data.name,
            description=org_data.description,
            contact_email=org_data.contact_email,
            country=org_data.country,
            subscription_level=org_data.subscription_level,
            status=OrganizationStatus.ACTIVE
        )
        
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        return _convert_organization_to_response(new_org)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Organization creation failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating organization: {str(e)}"
        )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific organization by ID"""
    
    # Validate UUID format
    try:
        uuid.UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid organization_id format. Must be a valid UUID."
        )
    
    # Check if user has access to this organization
    if not _check_organization_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to this organization"
        )
    
    # Get organization
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    return _convert_organization_to_response(organization)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an organization"""
    
    # Validate UUID format
    try:
        uuid.UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid organization_id format. Must be a valid UUID."
        )
    
    # Check if user has access to this organization
    if not _check_organization_access(current_user, db, org_id):
        raise HTTPException(
            status_code=403,
            detail="Access denied to this organization"
        )
    
    # Get organization
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    # Check for duplicate name if name is being updated
    if org_data.name and org_data.name != organization.name:
        existing_org = db.query(Organization).filter_by(name=org_data.name).first()
        if existing_org:
            raise HTTPException(
                status_code=400,
                detail="Organization name already exists"
            )
    
    # Update organization fields
    try:
        update_data = org_data.model_dump(exclude_unset=True)
        
        # Handle status conversion
        if "status" in update_data:
            try:
                update_data["status"] = OrganizationStatus(update_data["status"])
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid status value. Must be one of: {[s.value for s in OrganizationStatus]}"
                )
        
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        db.commit()
        db.refresh(organization)
        
        return _convert_organization_to_response(organization)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Organization update failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating organization: {str(e)}"
        )


@router.delete("/{org_id}")
async def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an organization (Super Admin only)"""
    
    # Validate UUID format
    try:
        uuid.UUID(org_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid organization_id format. Must be a valid UUID."
        )
    
    # Check if user is Super Admin
    user_role = db.query(Role).filter_by(id=current_user.system_role_id).first()
    if not user_role or user_role.name != RoleName.SUPER_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only Super Admins can delete organizations"
        )
    
    # Get organization
    organization = db.query(Organization).filter_by(id=org_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {org_id} not found"
        )
    
    try:
        # Delete associated memberships first
        db.query(OrganizationMembership).filter_by(organization_id=org_id).delete()
        
        # Delete organization
        db.delete(organization)
        db.commit()
        
        return {"message": "Organization deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting organization: {str(e)}"
        )