# Backend User Management Endpoints Implementation Plan

## Overview

The frontend user management functionality is currently blocked because the backend lacks essential user, organization, and membership management endpoints. This document outlines the required backend implementation before frontend user management can function properly.

## Current State Analysis

### ✅ Existing Backend Endpoints:
- `/api/v1/auth/login` - User authentication
- `/api/v1/auth/me` - Get current user info
- `/api/v1/auth/logout` - User logout
- Work Items, Schedules, and System endpoints

### ❌ Missing Critical Endpoints:

#### User Management:
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

#### Organization Management:
- `GET /api/v1/organizations` - List organizations
- `POST /api/v1/organizations` - Create organization
- `GET /api/v1/organizations/{org_id}` - Get organization details
- `PUT /api/v1/organizations/{org_id}` - Update organization
- `DELETE /api/v1/organizations/{org_id}` - Delete organization

#### Organization Membership Management:
- `GET /api/v1/organizations/{org_id}/memberships` - List organization members
- `POST /api/v1/organizations/{org_id}/memberships` - Add user to organization
- `GET /api/v1/organizations/{org_id}/memberships/{user_id}` - Get membership details
- `PUT /api/v1/organizations/{org_id}/memberships/{user_id}` - Update user role in organization
- `DELETE /api/v1/organizations/{org_id}/memberships/{user_id}` - Remove user from organization

## Required Backend Implementation

### Phase 1: User Management Endpoints

#### 1.1 User API Routes (`src/dbr/api/users.py`)
```python
# New file needed
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users (with optional organization filtering)"""
    pass

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user"""
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    pass

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user"""
    pass

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user"""
    pass
```

#### 1.2 User Schemas (`src/dbr/schemas/user.py`)
```python
# New file needed
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_date: datetime
    updated_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Phase 2: Organization Management Endpoints

#### 2.1 Organization API Routes (`src/dbr/api/organizations.py`)
```python
# New file needed
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.organization import Organization
from ..schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of organizations (Super Admin sees all, others see their own)"""
    pass

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new organization (Super Admin only)"""
    pass

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization by ID"""
    pass

@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update organization"""
    pass

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete organization"""
    pass
```

#### 2.2 Organization Schemas (`src/dbr/schemas/organization.py`)
```python
# New file needed
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    id: str
    created_date: datetime
    updated_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Phase 3: Organization Membership Management Endpoints

#### 3.1 Membership API Routes (`src/dbr/api/memberships.py`)
```python
# New file needed
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.organization_membership import OrganizationMembership
from ..schemas.membership import MembershipCreate, MembershipUpdate, MembershipResponse

router = APIRouter(prefix="/organizations/{org_id}/memberships", tags=["Memberships"])

@router.get("/", response_model=List[MembershipResponse])
async def get_organization_memberships(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of organization members"""
    pass

@router.post("/", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_organization(
    org_id: str,
    membership_data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add user to organization with role (invite/create user)"""
    pass

@router.get("/{user_id}", response_model=MembershipResponse)
async def get_membership(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific membership details"""
    pass

@router.put("/{user_id}", response_model=MembershipResponse)
async def update_membership(
    org_id: str,
    user_id: str,
    membership_data: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user role in organization"""
    pass

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_organization(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove user from organization"""
    pass
```

#### 3.2 Membership Schemas (`src/dbr/schemas/membership.py`)
```python
# New file needed
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..schemas.user import UserResponse
from ..schemas.role import RoleResponse

class MembershipBase(BaseModel):
    role_id: str
    is_active: bool = True

class MembershipCreate(BaseModel):
    user_id: Optional[str] = None  # If None, create new user
    username: Optional[str] = None  # For new user creation
    email: Optional[str] = None     # For new user creation
    password: Optional[str] = None  # For new user creation
    role_id: str

class MembershipUpdate(BaseModel):
    role_id: Optional[str] = None
    is_active: Optional[bool] = None

class MembershipResponse(MembershipBase):
    id: str
    organization_id: str
    user_id: str
    invited_by_user_id: str
    created_date: datetime
    updated_date: Optional[datetime] = None
    
    # Related objects
    user: UserResponse
    role: RoleResponse
    
    class Config:
        from_attributes = True
```

### Phase 4: Integration and Router Registration

#### 4.1 Update Main App (`src/dbr/main.py`)
```python
# Add these imports and router registrations
from .api import users, organizations, memberships

# Add to the app
app.include_router(users.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1") 
app.include_router(memberships.router, prefix="/api/v1")
```

#### 4.2 Permission System Updates
```python
# Update src/dbr/core/permissions.py
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.organization_membership import OrganizationMembership
from ..models.role import Role

def check_user_management_permission(current_user: User, db: Session, target_user_id: str = None):
    """Check if user can manage other users
    
    Rules:
    - Super Admin: Can manage all users globally
    - Organization Admin: Can manage users within their organizations only
    - Others: Cannot manage users
    """
    if is_super_admin(current_user, db):
        return True
    
    if target_user_id and is_organization_admin(current_user, db):
        # Check if target user is in any of current user's organizations
        return users_share_organization(current_user.id, target_user_id, db)
    
    return False

def check_organization_management_permission(current_user: User, db: Session, org_id: str = None):
    """Check if user can manage organization
    
    Rules:
    - Super Admin: Can manage all organizations
    - Organization Admin: Can manage only their own organizations
    - Others: Cannot manage organizations
    """
    if is_super_admin(current_user, db):
        return True
    
    if org_id and is_organization_admin(current_user, db):
        # Check if user is admin of this specific organization
        return is_admin_of_organization(current_user.id, org_id, db)
    
    return False

def check_membership_management_permission(current_user: User, db: Session, org_id: str):
    """Check if user can manage organization memberships
    
    Rules:
    - Super Admin: Can manage memberships in all organizations
    - Organization Admin: Can manage memberships ONLY in organizations they admin
    - Others: Cannot manage memberships
    """
    if is_super_admin(current_user, db):
        return True
    
    if is_organization_admin(current_user, db):
        # Must be admin of this specific organization
        return is_admin_of_organization(current_user.id, org_id, db)
    
    return False

def is_super_admin(user: User, db: Session) -> bool:
    """Check if user has Super Admin role"""
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id
    ).join(Role).filter(Role.name == "Super Admin").first()
    
    return membership is not None

def is_organization_admin(user: User, db: Session) -> bool:
    """Check if user has Organization Admin role in any organization"""
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user.id
    ).join(Role).filter(Role.name.in_(["Organization Admin", "Org Admin"])).first()
    
    return membership is not None

def is_admin_of_organization(user_id: str, org_id: str, db: Session) -> bool:
    """Check if user is admin of specific organization"""
    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.organization_id == org_id
    ).join(Role).filter(Role.name.in_(["Organization Admin", "Org Admin"])).first()
    
    return membership is not None

def users_share_organization(user1_id: str, user2_id: str, db: Session) -> bool:
    """Check if two users are in the same organization"""
    user1_orgs = db.query(OrganizationMembership.organization_id).filter(
        OrganizationMembership.user_id == user1_id
    ).subquery()
    
    user2_orgs = db.query(OrganizationMembership.organization_id).filter(
        OrganizationMembership.user_id == user2_id
    ).subquery()
    
    shared_org = db.query(user1_orgs).filter(
        user1_orgs.c.organization_id.in_(
            db.query(user2_orgs.c.organization_id)
        )
    ).first()
    
    return shared_org is not None

def get_user_administered_organizations(user_id: str, db: Session) -> List[str]:
    """Get list of organization IDs that user can administer"""
    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id
    ).join(Role).filter(Role.name.in_(["Super Admin", "Organization Admin", "Org Admin"])).all()
    
    if any(m.role.name == "Super Admin" for m in memberships):
        # Super Admin can administer all organizations
        from ..models.organization import Organization
        all_orgs = db.query(Organization.id).all()
        return [org.id for org in all_orgs]
    
    # Organization Admin can only administer their own organizations
    return [m.organization_id for m in memberships if m.role.name in ["Organization Admin", "Org Admin"]]
```

## Security Model Implementation

### **Critical Security Requirements:**

#### **User Management Security:**
```python
# Example implementation in users.py
@router.get("/", response_model=List[UserResponse])
async def get_users(
    organization_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of users with proper security filtering"""
    
    if is_super_admin(current_user, db):
        # Super Admin sees all users
        if organization_id:
            # Filter by specific organization if requested
            return get_users_by_organization(organization_id, db)
        return get_all_users(db)
    
    elif is_organization_admin(current_user, db):
        # Org Admin sees only users in their administered organizations
        admin_orgs = get_user_administered_organizations(current_user.id, db)
        
        if organization_id:
            # Verify they can access this organization
            if organization_id not in admin_orgs:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view users in this organization"
                )
            return get_users_by_organization(organization_id, db)
        
        # Return users from all their administered organizations
        return get_users_by_organizations(admin_orgs, db)
    
    else:
        # Other roles cannot list users
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view users"
        )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create user with organization context validation"""
    
    # Only Super Admin and Org Admin can create users
    if not (is_super_admin(current_user, db) or is_organization_admin(current_user, db)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create users"
        )
    
    # Create the user
    new_user = create_user_in_db(user_data, db)
    
    # Note: User creation alone doesn't grant organization access
    # Organization membership must be created separately via membership endpoints
    
    return new_user
```

#### **Organization Membership Security:**
```python
# Example implementation in memberships.py
@router.post("/", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_user_to_organization(
    org_id: str,
    membership_data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add user to organization with strict permission checking"""
    
    # Check if current user can manage this organization's memberships
    if not check_membership_management_permission(current_user, db, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to manage memberships for organization {org_id}"
        )
    
    # Validate the organization exists and user has access
    org = get_organization_by_id(org_id, db)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # If creating a new user, validate permissions
    if not membership_data.user_id and membership_data.username:
        # Creating new user + membership
        if not (is_super_admin(current_user, db) or is_admin_of_organization(current_user.id, org_id, db)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create users for this organization"
            )
    
    # Create membership with proper audit trail
    membership = create_membership_in_db(
        org_id=org_id,
        membership_data=membership_data,
        invited_by_user_id=current_user.id,
        db=db
    )
    
    return membership

@router.put("/{user_id}", response_model=MembershipResponse)
async def update_membership(
    org_id: str,
    user_id: str,
    membership_data: MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user role with security validation"""
    
    # Check permission to manage this organization's memberships
    if not check_membership_management_permission(current_user, db, org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to manage memberships for this organization"
        )
    
    # Prevent self-role modification (security risk)
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot modify your own role"
        )
    
    # Validate membership exists
    membership = get_membership_by_ids(org_id, user_id, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found"
        )
    
    # Update membership
    updated_membership = update_membership_in_db(membership, membership_data, db)
    
    return updated_membership
```

#### **Role-Based Access Control Matrix:**

| Action | Super Admin | Org Admin | Planner | Worker | Viewer |
|--------|-------------|-----------|---------|---------|---------|
| **User Management** |
| List all users | ✅ Global | ✅ Own orgs only | ❌ | ❌ | ❌ |
| Create user | ✅ | ✅ | ❌ | ❌ | ❌ |
| Update user | ✅ Global | ✅ Own orgs only | ❌ | ❌ | ❌ |
| Delete user | ✅ Global | ✅ Own orgs only | ❌ | ❌ | ❌ |
| **Organization Management** |
| List organizations | ✅ All | ✅ Own only | ❌ | ❌ | ❌ |
| Create organization | ✅ | ❌ | ❌ | ❌ | ❌ |
| Update organization | ✅ All | ✅ Own only | ❌ | ❌ | ❌ |
| Delete organization | ✅ All | ✅ Own only | ❌ | ❌ | ❌ |
| **Membership Management** |
| List org members | ✅ All orgs | ✅ Own orgs only | ❌ | ❌ | ❌ |
| Add user to org | ✅ All orgs | ✅ Own orgs only | ❌ | ❌ | ❌ |
| Update user role | ✅ All orgs | ✅ Own orgs only | ❌ | ❌ | ❌ |
| Remove user from org | ✅ All orgs | ✅ Own orgs only | ❌ | ❌ | ❌ |

#### **Security Audit Requirements:**
- All user management actions must be logged with `invited_by_user_id`
- Role changes must be audited
- Organization access must be validated on every request
- Self-modification prevention (users can't change their own roles)
- Cascade deletion rules (what happens when user/org is deleted)

## Implementation Priority

### **CRITICAL - Must be implemented first:**
1. **User Management Endpoints** - Core user CRUD operations
2. **Organization Membership Endpoints** - User-to-organization assignment with roles

### **Important - Needed for full functionality:**
3. **Organization Management Endpoints** - For Super Admin organization management

### **Supporting - Required for proper operation:**
4. **Permission System Updates** - Role-based access control
5. **Schema Validation** - Proper request/response validation
6. **Error Handling** - Comprehensive error responses

## Database Schema Verification

Ensure these models exist and are properly configured:
- ✅ `User` model (exists)
- ✅ `Organization` model (exists) 
- ✅ `Role` model (exists)
- ✅ `OrganizationMembership` model (exists)

## Testing Requirements

Each endpoint needs:
- Unit tests for business logic
- Integration tests for API endpoints
- Permission/authorization tests
- Error handling tests

## Frontend Impact

Once backend endpoints are implemented:
1. **Regenerate SDK** from updated OpenAPI spec
2. **Update DBRService** to use real API calls instead of mock data
3. **Test user persistence** across app restarts
4. **Verify role-based permissions** work correctly

## Estimated Implementation Time

- **Phase 1 (Users)**: 2-3 days
- **Phase 2 (Organizations)**: 1-2 days  
- **Phase 3 (Memberships)**: 2-3 days
- **Phase 4 (Integration)**: 1 day
- **Testing**: 2-3 days

**Total: 8-12 days**

## Conclusion

The frontend user management functionality cannot work without these backend endpoints. This is a **blocking dependency** that must be resolved before any meaningful user management features can be completed.

**Recommendation**: Prioritize implementing Phase 1 (User Management) and Phase 3 (Memberships) as the minimum viable implementation to unblock frontend development.