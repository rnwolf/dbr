from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from dbr.core.database import get_db
from dbr.models.collection import Collection, CollectionStatus
from dbr.models.organization import Organization
from dbr.models.organization_membership import OrganizationMembership, InvitationStatus
from dbr.models.user import User
from dbr.models.role import Role, RoleName

# Import auth dependency
try:
    from dbr.api.auth import get_current_user
except ImportError:
    # Handle circular import during testing
    def get_current_user():
        from dbr.api.auth import get_current_user as _get_current_user
        return _get_current_user

# API Router
router = APIRouter(prefix="/collections", tags=["Collections"])

# Pydantic schemas for request/response
class CollectionCreate(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    status: Optional[CollectionStatus] = Field(CollectionStatus.PLANNING, description="Collection status")
    estimated_sales_price: Optional[float] = Field(0.0, description="Estimated sales price")
    estimated_variable_cost: Optional[float] = Field(0.0, description="Estimated variable cost")


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    status: Optional[CollectionStatus] = Field(None, description="Collection status")
    estimated_sales_price: Optional[float] = Field(None, description="Estimated sales price")
    estimated_variable_cost: Optional[float] = Field(None, description="Estimated variable cost")


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    status: str  # String representation of enum
    estimated_sales_price: Optional[float]
    estimated_variable_cost: Optional[float]
    throughput: float
    created_date: str
    updated_date: str


def _validate_organization_access(session: Session, organization_id: str) -> Organization:
    """Validate that the organization exists and user has access"""
    org = session.query(Organization).filter_by(id=organization_id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Access denied to organization")
    return org


def _check_collection_access_permissions(current_user: User, session: Session, organization_id: str, operation: str = "read") -> None:
    """Check if user has appropriate permissions for collection operations"""
    # Get user's system role
    user_role = session.query(Role).filter_by(id=current_user.system_role_id).first()
    
    # Super Admin has access to everything
    if user_role and user_role.name == RoleName.SUPER_ADMIN:
        return
    
    # Check organization membership
    membership = session.query(OrganizationMembership).filter_by(
        user_id=current_user.id,
        organization_id=organization_id,
        invitation_status=InvitationStatus.ACCEPTED
    ).first()
    
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to organization")
    
    # Get user's role in the organization
    member_role = session.query(Role).filter_by(id=membership.role_id).first()
    
    if not member_role:
        raise HTTPException(status_code=403, detail="Invalid role assignment")
    
    # Check permissions based on operation
    if operation in ["create", "update", "delete"]:
        # Only Planners and Org Admins can modify collections
        if member_role.name not in [RoleName.PLANNER, RoleName.ORGANIZATION_ADMIN]:
            raise HTTPException(status_code=403, detail="Insufficient permissions for collection management")
    elif operation == "read":
        # All organization members can view collections
        if member_role.name not in [RoleName.PLANNER, RoleName.ORGANIZATION_ADMIN, RoleName.WORKER, RoleName.VIEWER]:
            raise HTTPException(status_code=403, detail="Insufficient permissions to view collections")


def _convert_collection_to_response(collection: Collection) -> Dict[str, Any]:
    """Convert Collection model to response dictionary"""
    return {
        "id": collection.id,
        "organization_id": collection.organization_id,
        "name": collection.name,
        "description": collection.description,
        "status": collection.status.value,
        "estimated_sales_price": collection.estimated_sales_price,
        "estimated_variable_cost": collection.estimated_variable_cost,
        "throughput": collection.calculate_throughput(),
        "created_date": collection.created_date.isoformat(),
        "updated_date": collection.updated_date.isoformat()
    }


@router.get("/", response_model=List[CollectionResponse])
def get_collections(
    organization_id: str = Query(..., description="Organization ID to filter by"),
    status: Optional[str] = Query(None, description="Filter by collection status"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all collections for an organization"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Check user permissions
    _check_collection_access_permissions(current_user, session, organization_id, "read")
    
    # Build query
    query = session.query(Collection).filter_by(organization_id=organization_id)
    
    # Apply status filter if provided
    if status:
        try:
            status_enum = CollectionStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
    
    collections = query.all()
    
    # Convert to response format
    return [_convert_collection_to_response(collection) for collection in collections]


@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: CollectionCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new collection"""
    
    # Validate organization access
    _validate_organization_access(session, collection_data.organization_id)
    
    # Check user permissions for creation
    _check_collection_access_permissions(current_user, session, collection_data.organization_id, "create")
    
    # Create collection
    new_collection = Collection(
        organization_id=collection_data.organization_id,
        name=collection_data.name,
        description=collection_data.description,
        status=collection_data.status or CollectionStatus.PLANNING,
        estimated_sales_price=collection_data.estimated_sales_price,
        estimated_variable_cost=collection_data.estimated_variable_cost
    )
    
    session.add(new_collection)
    session.commit()
    session.refresh(new_collection)
    
    return _convert_collection_to_response(new_collection)


@router.get("/{collection_id}", response_model=CollectionResponse)
def get_collection(
    collection_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific collection by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Check user permissions
    _check_collection_access_permissions(current_user, session, organization_id, "read")
    
    # Get collection
    collection = session.query(Collection).filter_by(
        id=collection_id,
        organization_id=organization_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return _convert_collection_to_response(collection)


@router.put("/{collection_id}", response_model=CollectionResponse)
def update_collection(
    collection_id: str,
    collection_data: CollectionUpdate,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a collection by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Check user permissions for updates
    _check_collection_access_permissions(current_user, session, organization_id, "update")
    
    # Get collection
    collection = session.query(Collection).filter_by(
        id=collection_id,
        organization_id=organization_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Update fields
    update_data = collection_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value is not None:
            # Handle enum conversion
            try:
                collection.status = CollectionStatus(value)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {value}")
        else:
            setattr(collection, field, value)
    
    session.commit()
    session.refresh(collection)
    
    return _convert_collection_to_response(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a collection by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Check user permissions for deletion
    _check_collection_access_permissions(current_user, session, organization_id, "delete")
    
    # Get collection
    collection = session.query(Collection).filter_by(
        id=collection_id,
        organization_id=organization_id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check if collection has associated work items
    from dbr.models.work_item import WorkItem
    work_items_count = session.query(WorkItem).filter_by(collection_id=collection_id).count()
    
    if work_items_count > 0:
        raise HTTPException(
            status_code=409, 
            detail=f"Cannot delete collection. It contains {work_items_count} work item(s). Remove work items first or set their collection_id to null."
        )
    
    # Delete collection
    session.delete(collection)
    session.commit()