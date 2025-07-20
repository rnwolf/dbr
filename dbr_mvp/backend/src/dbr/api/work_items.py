# src/dbr/api/work_items.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from dbr.core.database import get_db
from dbr.models.work_item import WorkItem, WorkItemStatus, WorkItemPriority
from dbr.models.organization import Organization


router = APIRouter(prefix="/workitems", tags=["Work Items"])


# Pydantic schemas for request/response
class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title")
    completed: bool = Field(default=False, description="Task completion status")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Task title")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool


class WorkItemCreate(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    collection_id: Optional[str] = Field(None, description="Collection ID (optional)")
    title: str = Field(..., description="Work item title")
    description: Optional[str] = Field(None, description="Work item description")
    status: Optional[str] = Field(default="Backlog", description="Work item status")
    priority: Optional[str] = Field(default="medium", description="Work item priority")
    estimated_total_hours: float = Field(..., description="Estimated total hours")
    ccr_hours_required: Optional[Dict[str, float]] = Field(default_factory=dict, description="CCR hours required")
    estimated_sales_price: Optional[float] = Field(default=0.0, description="Estimated sales price")
    estimated_variable_cost: Optional[float] = Field(default=0.0, description="Estimated variable cost")
    tasks: Optional[List[TaskCreate]] = Field(default_factory=list, description="Initial tasks")
    responsible_user_id: Optional[str] = Field(None, description="Responsible user ID")
    url: Optional[str] = Field(None, description="External URL")


class WorkItemUpdate(BaseModel):
    collection_id: Optional[str] = Field(None, description="Collection ID")
    title: Optional[str] = Field(None, description="Work item title")
    description: Optional[str] = Field(None, description="Work item description")
    status: Optional[str] = Field(None, description="Work item status")
    priority: Optional[str] = Field(None, description="Work item priority")
    estimated_total_hours: Optional[float] = Field(None, description="Estimated total hours")
    ccr_hours_required: Optional[Dict[str, float]] = Field(None, description="CCR hours required")
    estimated_sales_price: Optional[float] = Field(None, description="Estimated sales price")
    estimated_variable_cost: Optional[float] = Field(None, description="Estimated variable cost")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="Tasks list")
    responsible_user_id: Optional[str] = Field(None, description="Responsible user ID")
    url: Optional[str] = Field(None, description="External URL")


class WorkItemResponse(BaseModel):
    id: str
    organization_id: str
    collection_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: str
    estimated_total_hours: float
    ccr_hours_required: Optional[Dict[str, float]]
    estimated_sales_price: Optional[float]
    estimated_variable_cost: Optional[float]
    throughput: float
    tasks: List[TaskResponse]
    progress_percentage: float
    responsible_user_id: Optional[str]
    url: Optional[str]
    created_date: str
    updated_date: str

    class Config:
        from_attributes = True


def _validate_organization_access(session: Session, organization_id: str) -> Organization:
    """Validate that the organization exists and user has access"""
    org = session.query(Organization).filter_by(id=organization_id).first()
    if not org:
        raise HTTPException(status_code=403, detail="Access denied to organization")
    return org


def _convert_work_item_to_response(work_item: WorkItem) -> Dict[str, Any]:
    """Convert WorkItem model to response dictionary"""
    
    # Convert tasks to response format
    tasks = []
    if work_item.tasks:
        for task in work_item.tasks:
            # Ensure task has an ID (generate one if missing)
            task_id = task.get("id")
            if task_id is None:
                # This shouldn't happen, but handle gracefully
                task_id = len(tasks) + 1
            
            tasks.append({
                "id": int(task_id),
                "title": task.get("title", ""),
                "completed": task.get("completed", False)
            })
    
    return {
        "id": work_item.id,
        "organization_id": work_item.organization_id,
        "collection_id": work_item.collection_id,
        "title": work_item.title,
        "description": work_item.description,
        "status": work_item.status.value,
        "priority": work_item.priority.value,
        "estimated_total_hours": work_item.estimated_total_hours,
        "ccr_hours_required": work_item.ccr_hours_required,
        "estimated_sales_price": work_item.estimated_sales_price,
        "estimated_variable_cost": work_item.estimated_variable_cost,
        "throughput": work_item.calculate_throughput(),
        "tasks": tasks,
        "progress_percentage": round(work_item.calculate_progress() * 100, 2),
        "responsible_user_id": None,  # TODO: Add when user assignment is implemented
        "url": None,  # TODO: Add when URL field is implemented
        "created_date": work_item.created_date.isoformat(),
        "updated_date": work_item.updated_date.isoformat()
    }


@router.get("", response_model=List[WorkItemResponse])
def get_work_items(
    organization_id: str = Query(..., description="Organization ID to filter by"),
    collection_id: Optional[str] = Query(None, description="Collection ID to filter by"),
    status: Optional[List[str]] = Query(None, description="Status to filter by"),
    priority: Optional[str] = Query(None, description="Priority to filter by"),
    sort: Optional[str] = Query(None, description="Sort field"),
    session: Session = Depends(get_db)
):
    """Get all work items with optional filtering"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Build query
    query = session.query(WorkItem).filter_by(organization_id=organization_id)
    
    # Apply filters
    if collection_id:
        query = query.filter_by(collection_id=collection_id)
    
    if status:
        # Convert string statuses to enum values
        status_enums = []
        for s in status:
            try:
                status_enums.append(WorkItemStatus(s))
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {s}")
        query = query.filter(WorkItem.status.in_(status_enums))
    
    if priority:
        try:
            priority_enum = WorkItemPriority(priority)
            query = query.filter_by(priority=priority_enum)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid priority: {priority}")
    
    # Apply sorting
    if sort:
        if sort == "title":
            query = query.order_by(WorkItem.title)
        elif sort == "created_date":
            query = query.order_by(WorkItem.created_date)
        elif sort == "priority":
            query = query.order_by(WorkItem.priority)
        elif sort == "status":
            query = query.order_by(WorkItem.status)
    
    work_items = query.all()
    
    # Convert to response format
    return [_convert_work_item_to_response(item) for item in work_items]


@router.post("", response_model=WorkItemResponse, status_code=201)
def create_work_item(
    work_item_data: WorkItemCreate,
    session: Session = Depends(get_db)
):
    """Create a new work item"""
    
    # Validate organization access
    _validate_organization_access(session, work_item_data.organization_id)
    
    # Convert string enums to enum objects
    try:
        status_enum = WorkItemStatus(work_item_data.status)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid status: {work_item_data.status}")
    
    try:
        priority_enum = WorkItemPriority(work_item_data.priority)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid priority: {work_item_data.priority}")
    
    # Create work item
    work_item = WorkItem(
        organization_id=work_item_data.organization_id,
        collection_id=work_item_data.collection_id,
        title=work_item_data.title,
        description=work_item_data.description,
        status=status_enum,
        priority=priority_enum,
        estimated_total_hours=work_item_data.estimated_total_hours,
        ccr_hours_required=work_item_data.ccr_hours_required,
        estimated_sales_price=work_item_data.estimated_sales_price,
        estimated_variable_cost=work_item_data.estimated_variable_cost
    )
    
    # Add initial tasks
    for task_data in work_item_data.tasks:
        work_item.add_task(task_data.title)
        if task_data.completed:
            # Find the task we just added and mark it completed
            if work_item.tasks:
                last_task = work_item.tasks[-1]
                work_item.complete_task(last_task["id"])
    
    session.add(work_item)
    session.commit()
    session.refresh(work_item)
    
    return _convert_work_item_to_response(work_item)


@router.get("/{work_item_id}", response_model=WorkItemResponse)
def get_work_item(
    work_item_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Get a specific work item by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get work item
    work_item = session.query(WorkItem).filter_by(
        id=work_item_id,
        organization_id=organization_id
    ).first()
    
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    return _convert_work_item_to_response(work_item)


@router.put("/{work_item_id}", response_model=WorkItemResponse)
def update_work_item(
    work_item_id: str,
    work_item_data: WorkItemUpdate,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Update a work item by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get work item
    work_item = session.query(WorkItem).filter_by(
        id=work_item_id,
        organization_id=organization_id
    ).first()
    
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Update fields
    update_data = work_item_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "status" and value is not None:
            try:
                work_item.status = WorkItemStatus(value)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid status: {value}")
        elif field == "priority" and value is not None:
            try:
                work_item.priority = WorkItemPriority(value)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid priority: {value}")
        elif field == "tasks" and value is not None:
            # Replace tasks entirely, ensuring each task has an ID
            processed_tasks = []
            for i, task_data in enumerate(value):
                if isinstance(task_data, dict):
                    # Ensure task has an ID
                    if "id" not in task_data or task_data["id"] is None:
                        task_data["id"] = i + 1
                    processed_tasks.append(task_data)
            work_item.tasks = processed_tasks
        else:
            setattr(work_item, field, value)
    
    session.commit()
    session.refresh(work_item)
    
    return _convert_work_item_to_response(work_item)


@router.delete("/{work_item_id}", status_code=204)
def delete_work_item(
    work_item_id: str,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Delete a work item by ID"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get work item
    work_item = session.query(WorkItem).filter_by(
        id=work_item_id,
        organization_id=organization_id
    ).first()
    
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    session.delete(work_item)
    session.commit()


@router.put("/{work_item_id}/tasks/{task_id}", response_model=WorkItemResponse)
def update_work_item_task(
    work_item_id: str,
    task_id: int,
    task_data: TaskUpdate,
    organization_id: str = Query(..., description="Organization ID to scope the request"),
    session: Session = Depends(get_db)
):
    """Update a specific task within a work item"""
    
    # Validate organization access
    _validate_organization_access(session, organization_id)
    
    # Get work item
    work_item = session.query(WorkItem).filter_by(
        id=work_item_id,
        organization_id=organization_id
    ).first()
    
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Find and update task
    task_found = False
    if work_item.tasks:
        for task in work_item.tasks:
            # Convert both to int for comparison (handle type mismatches)
            stored_task_id = task.get("id")
            if stored_task_id is not None and int(stored_task_id) == int(task_id):
                # Update task fields
                if task_data.title is not None:
                    task["title"] = task_data.title
                
                if task_data.completed is not None:
                    task["completed"] = task_data.completed
                
                task_found = True
                break
    
    if not task_found:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Force SQLAlchemy to detect the change in the JSON field by creating a new list
    work_item.tasks = list(work_item.tasks)
    
    # Mark the work item as updated and commit
    session.commit()
    session.refresh(work_item)
    
    return _convert_work_item_to_response(work_item)