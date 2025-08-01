# src/dbr/api/users.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field, ConfigDict
import uuid

from dbr.core.database import get_db
from dbr.core.security import hash_password
from dbr.models.user import User
from dbr.models.organization import Organization
from dbr.models.role import Role
from dbr.models.organization_membership import OrganizationMembership, InvitationStatus

# Import auth dependency
try:
    from dbr.api.auth import get_current_user
except ImportError:
    # Handle circular import during testing
    def get_current_user():
        from dbr.api.auth import get_current_user as _get_current_user
        return _get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


# Pydantic schemas for request/response
class UserCreate(BaseModel):
    """Schema for creating a new user"""
    organization_id: str = Field(..., description="Organization ID")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")
    password: str = Field(..., min_length=6, description="Password")
    system_role_id: str = Field(..., description="System role ID")
    active_status: bool = Field(default=True, description="Active status")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    email: Optional[str] = Field(None, description="Email address")
    display_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Display name")
    system_role_id: Optional[str] = Field(None, description="System role ID")
    active_status: Optional[bool] = Field(None, description="Active status")


class UserResponse(BaseModel):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    email: str
    display_name: str
    active_status: bool
    system_role_id: str
    created_date: str
    updated_date: str


def _convert_user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        active_status=user.active_status,
        system_role_id=user.system_role_id,
        created_date=user.created_date.isoformat(),
        updated_date=user.updated_date.isoformat()
    )


@router.get("/", response_model=List[UserResponse])
async def get_users(
    organization_id: str = Query(..., description="Organization ID to filter users"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users (with organization filtering)"""
    
    # Validate UUID format
    try:
        uuid.UUID(organization_id)
    except ValueError:
        raise HTTPException(
            status_code=422, 
            detail="Invalid organization_id format. Must be a valid UUID."
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=404, 
            detail=f"Organization {organization_id} not found"
        )
    
    # Get users who are members of the organization
    users_query = db.query(User).join(
        OrganizationMembership,
        User.id == OrganizationMembership.user_id
    ).filter(
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.invitation_status == InvitationStatus.ACCEPTED
    )
    
    users = users_query.all()
    
    return [_convert_user_to_response(user) for user in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user"""
    
    # Validate UUID formats
    try:
        uuid.UUID(user_data.organization_id)
        uuid.UUID(user_data.system_role_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format for organization_id or system_role_id"
        )
    
    # Validate organization exists
    organization = db.query(Organization).filter_by(id=user_data.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {user_data.organization_id} not found"
        )
    
    # Validate role exists
    role = db.query(Role).filter_by(id=user_data.system_role_id).first()
    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role not found"
        )
    
    # Check for duplicate username
    existing_username = db.query(User).filter_by(username=user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Check for duplicate email
    existing_email = db.query(User).filter_by(email=user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    # Create new user
    try:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name,
            password_hash=hash_password(user_data.password),
            active_status=user_data.active_status,
            system_role_id=user_data.system_role_id
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create organization membership
        membership = OrganizationMembership(
            organization_id=user_data.organization_id,
            user_id=new_user.id,
            role_id=user_data.system_role_id,
            invitation_status=InvitationStatus.ACCEPTED,
            invited_by_user_id=current_user.id
        )
        
        db.add(membership)
        db.commit()
        
        return _convert_user_to_response(new_user)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User creation failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID"""
    
    # Validate UUID format
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid user_id format. Must be a valid UUID."
        )
    
    # Get user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    
    return _convert_user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user"""
    
    # Validate UUID format
    try:
        uuid.UUID(user_id)
        if user_data.system_role_id:
            uuid.UUID(user_data.system_role_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid UUID format"
        )
    
    # Get user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    
    # Validate role if provided
    if user_data.system_role_id:
        role = db.query(Role).filter_by(id=user_data.system_role_id).first()
        if not role:
            raise HTTPException(
                status_code=400,
                detail="Role not found"
            )
    
    # Check for duplicate email if email is being updated
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter_by(email=user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
    
    # Check for duplicate username if username is being updated
    if user_data.username and user_data.username != user.username:
        existing_username = db.query(User).filter_by(username=user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
    
    # Update user fields
    try:
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return _convert_user_to_response(user)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="User update failed due to constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user"""
    
    # Validate UUID format
    try:
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid user_id format. Must be a valid UUID."
        )
    
    # Get user
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    
    try:
        # Delete associated memberships first
        db.query(OrganizationMembership).filter_by(user_id=user_id).delete()
        
        # Delete user
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting user: {str(e)}"
        )