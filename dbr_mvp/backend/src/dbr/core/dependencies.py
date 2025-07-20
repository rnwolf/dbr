# src/dbr/core/dependencies.py
from typing import List, Set
from sqlalchemy.orm import Session
from dbr.models.work_item_dependency import WorkItemDependency
from dbr.models.work_item import WorkItem, WorkItemStatus


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected"""
    pass


def validate_dependency(session: Session, dependency: WorkItemDependency) -> None:
    """Validate a dependency before creating it"""
    
    # Check for self-dependency
    if dependency.dependent_work_item_id == dependency.prerequisite_work_item_id:
        raise CircularDependencyError("Work item cannot depend on itself")
    
    # Check that both work items exist and are from the same organization
    dependent_item = session.query(WorkItem).filter_by(id=dependency.dependent_work_item_id).first()
    prerequisite_item = session.query(WorkItem).filter_by(id=dependency.prerequisite_work_item_id).first()
    
    if not dependent_item or not prerequisite_item:
        raise ValueError("Both work items must exist")
    
    if dependent_item.organization_id != prerequisite_item.organization_id:
        raise ValueError("Work items must be from different organizations")
    
    # Check for circular dependencies
    if _would_create_cycle(session, dependency.dependent_work_item_id, dependency.prerequisite_work_item_id):
        raise CircularDependencyError("This dependency would create a circular dependency")


def _would_create_cycle(session: Session, dependent_id: str, prerequisite_id: str) -> bool:
    """Check if adding a dependency would create a circular dependency"""
    
    # Use depth-first search to detect cycles
    visited = set()
    rec_stack = set()
    
    def has_cycle(work_item_id: str) -> bool:
        if work_item_id in rec_stack:
            return True
        
        if work_item_id in visited:
            return False
        
        visited.add(work_item_id)
        rec_stack.add(work_item_id)
        
        # Get all dependencies of this work item
        dependencies = session.query(WorkItemDependency).filter_by(
            dependent_work_item_id=work_item_id
        ).all()
        
        for dep in dependencies:
            if has_cycle(dep.prerequisite_work_item_id):
                return True
        
        rec_stack.remove(work_item_id)
        return False
    
    # Temporarily add the new dependency and check for cycles
    # Start from the prerequisite and see if we can reach the dependent
    temp_dependencies = session.query(WorkItemDependency).filter_by(
        dependent_work_item_id=prerequisite_id
    ).all()
    
    # Check if prerequisite already depends on dependent (directly or indirectly)
    return _can_reach(session, prerequisite_id, dependent_id, set())


def _can_reach(session: Session, start_id: str, target_id: str, visited: Set[str]) -> bool:
    """Check if start_id can reach target_id through dependencies"""
    if start_id == target_id:
        return True
    
    if start_id in visited:
        return False
    
    visited.add(start_id)
    
    # Get all prerequisites of start_id
    dependencies = session.query(WorkItemDependency).filter_by(
        dependent_work_item_id=start_id
    ).all()
    
    for dep in dependencies:
        if _can_reach(session, dep.prerequisite_work_item_id, target_id, visited):
            return True
    
    return False


def can_work_item_be_ready(session: Session, work_item_id: str) -> bool:
    """Check if a work item can be moved to Ready status based on dependencies"""
    
    # Get all dependencies for this work item
    dependencies = session.query(WorkItemDependency).filter_by(
        dependent_work_item_id=work_item_id
    ).all()
    
    # Check if all prerequisites are completed
    for dependency in dependencies:
        prerequisite = session.query(WorkItem).filter_by(
            id=dependency.prerequisite_work_item_id
        ).first()
        
        if not prerequisite or prerequisite.status != WorkItemStatus.DONE:
            return False
    
    return True


def get_work_item_dependencies(session: Session, work_item_id: str) -> List[WorkItemDependency]:
    """Get all dependencies for a work item"""
    return session.query(WorkItemDependency).filter_by(
        dependent_work_item_id=work_item_id
    ).all()


def get_work_item_dependents(session: Session, work_item_id: str) -> List[WorkItemDependency]:
    """Get all work items that depend on this work item"""
    return session.query(WorkItemDependency).filter_by(
        prerequisite_work_item_id=work_item_id
    ).all()


def get_dependency_chain(session: Session, work_item_id: str) -> List[str]:
    """Get the full dependency chain for a work item (all prerequisites recursively)"""
    chain = []
    visited = set()
    
    def _build_chain(current_id: str):
        if current_id in visited:
            return
        
        visited.add(current_id)
        
        dependencies = session.query(WorkItemDependency).filter_by(
            dependent_work_item_id=current_id
        ).all()
        
        for dep in dependencies:
            prerequisite_id = dep.prerequisite_work_item_id
            if prerequisite_id not in chain:
                chain.append(prerequisite_id)
            _build_chain(prerequisite_id)
    
    _build_chain(work_item_id)
    return chain


def get_blocked_work_items(session: Session, organization_id: str) -> List[WorkItem]:
    """Get all work items that are blocked by incomplete dependencies"""
    blocked_items = []
    
    # Get all work items that have dependencies
    work_items_with_deps = session.query(WorkItem).join(
        WorkItemDependency, WorkItem.id == WorkItemDependency.dependent_work_item_id
    ).filter(WorkItem.organization_id == organization_id).distinct().all()
    
    for item in work_items_with_deps:
        if not can_work_item_be_ready(session, item.id):
            blocked_items.append(item)
    
    return blocked_items


def remove_dependency(session: Session, dependency_id: str) -> bool:
    """Remove a dependency relationship"""
    dependency = session.query(WorkItemDependency).filter_by(id=dependency_id).first()
    if dependency:
        session.delete(dependency)
        session.commit()
        return True
    return False