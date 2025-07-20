# src/dbr/models/ccr.py
from sqlalchemy import Column, String, Enum, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Session
from dbr.models.base import BaseModel
import enum
from typing import List, Dict, Any


class CCRType(enum.Enum):
    """CCR type enumeration"""
    SKILL_BASED = "skill_based"
    TEAM_BASED = "team_based"
    EQUIPMENT_BASED = "equipment_based"


class CCR(BaseModel):
    """CCR (Capacity Constrained Resource) model"""
    __tablename__ = "ccrs"
    
    # Basic CCR information
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    ccr_type = Column(Enum(CCRType), nullable=False)
    
    # Capacity configuration
    capacity_per_time_unit = Column(Float, nullable=False)
    time_unit = Column(String(20), nullable=False, default="week")  # week, day, month
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="ccrs")
    # user_associations = relationship("CCRUserAssociation", back_populates="ccr")
    
    def get_daily_capacity(self) -> float:
        """Get capacity per day"""
        if self.time_unit == "day":
            return self.capacity_per_time_unit
        elif self.time_unit == "week":
            return self.capacity_per_time_unit / 7
        elif self.time_unit == "month":
            return self.capacity_per_time_unit / 30
        return self.capacity_per_time_unit
    
    def get_weekly_capacity(self) -> float:
        """Get capacity per week"""
        if self.time_unit == "day":
            return self.capacity_per_time_unit * 7
        elif self.time_unit == "week":
            return self.capacity_per_time_unit
        elif self.time_unit == "month":
            return self.capacity_per_time_unit / 4.33
        return self.capacity_per_time_unit
    
    def get_monthly_capacity(self) -> float:
        """Get capacity per month"""
        if self.time_unit == "day":
            return self.capacity_per_time_unit * 30
        elif self.time_unit == "week":
            return self.capacity_per_time_unit * 4.33
        elif self.time_unit == "month":
            return self.capacity_per_time_unit
        return self.capacity_per_time_unit
    
    def calculate_total_demand(self, session: Session, work_items: List) -> float:
        """Calculate total demand from work items for this CCR"""
        total_demand = 0.0
        ccr_key = self.name.lower().replace(" ", "_")
        
        for work_item in work_items:
            if work_item.ccr_hours_required:
                demand = work_item.ccr_hours_required.get(ccr_key, 0.0)
                total_demand += demand
        
        return total_demand
    
    def calculate_utilization(self, session: Session, work_items: List) -> float:
        """Calculate utilization percentage for this CCR"""
        total_demand = self.calculate_total_demand(session, work_items)
        if self.capacity_per_time_unit == 0:
            return 0.0
        return total_demand / self.capacity_per_time_unit
    
    def get_available_capacity(self, session: Session, work_items: List) -> float:
        """Get available capacity (negative if over capacity)"""
        total_demand = self.calculate_total_demand(session, work_items)
        return self.capacity_per_time_unit - total_demand
    
    def can_schedule_work_items(self, session: Session, work_items: List) -> bool:
        """Check if work items can be scheduled within capacity"""
        return self.get_available_capacity(session, work_items) >= 0
    
    def get_associated_users(self, session: Session) -> List:
        """Get all users associated with this CCR"""
        from dbr.models.ccr_user_association import CCRUserAssociation
        from dbr.models.user import User
        
        associations = session.query(CCRUserAssociation).filter_by(
            ccr_id=self.id, is_active=True
        ).all()
        
        users = []
        for assoc in associations:
            user = session.query(User).filter_by(id=assoc.user_id).first()
            if user:
                users.append(user)
        
        return users
    
    def calculate_capacity_from_users(self, session: Session) -> float:
        """Calculate total capacity from associated users"""
        from dbr.models.ccr_user_association import CCRUserAssociation
        
        associations = session.query(CCRUserAssociation).filter_by(
            ccr_id=self.id, is_active=True
        ).all()
        
        total_capacity = sum(assoc.capacity_contribution for assoc in associations)
        return total_capacity
    
    def get_users_by_skill_level(self, session: Session, skill_level: str) -> List:
        """Get users associated with this CCR by skill level"""
        from dbr.models.ccr_user_association import CCRUserAssociation
        from dbr.models.user import User
        
        associations = session.query(CCRUserAssociation).filter_by(
            ccr_id=self.id, skill_level=skill_level, is_active=True
        ).all()
        
        users = []
        for assoc in associations:
            user = session.query(User).filter_by(id=assoc.user_id).first()
            if user:
                users.append(user)
        
        return users
    
    def validate_capacity_against_users(self, session: Session) -> bool:
        """Validate that CCR capacity matches user capacity contributions"""
        user_capacity = self.calculate_capacity_from_users(session)
        return abs(self.capacity_per_time_unit - user_capacity) < 0.01  # Allow small floating point differences
    
    def get_analytics(self, session: Session) -> Dict[str, Any]:
        """Get comprehensive analytics for this CCR"""
        from dbr.models.work_item import WorkItem
        
        # Get all work items in the organization that require this CCR
        ccr_key = self.name.lower().replace(" ", "_")
        all_work_items = session.query(WorkItem).filter_by(organization_id=self.organization_id).all()
        
        # Filter work items that require this CCR
        requiring_work_items = []
        for item in all_work_items:
            if item.ccr_hours_required and ccr_key in item.ccr_hours_required:
                requiring_work_items.append(item)
        
        total_demand = self.calculate_total_demand(session, requiring_work_items)
        utilization = self.calculate_utilization(session, requiring_work_items)
        available_capacity = self.get_available_capacity(session, requiring_work_items)
        
        return {
            "ccr_name": self.name,
            "ccr_type": self.ccr_type.value,
            "capacity": self.capacity_per_time_unit,
            "time_unit": self.time_unit,
            "total_demand": total_demand,
            "utilization": utilization,
            "available_capacity": available_capacity,
            "is_over_capacity": available_capacity < 0,
            "work_items_count": len(all_work_items),
            "work_items_requiring_ccr": len(requiring_work_items),
            "associated_users_count": len(self.get_associated_users(session)),
            "user_capacity": self.calculate_capacity_from_users(session),
        }
    
    @staticmethod
    def get_organization_ccr_analytics(session: Session, organization_id: str) -> Dict[str, Any]:
        """Get organization-wide CCR analytics"""
        ccrs = session.query(CCR).filter_by(organization_id=organization_id, is_active=True).all()
        
        ccr_utilization = {}
        total_capacity = 0.0
        total_demand = 0.0
        
        for ccr in ccrs:
            analytics = ccr.get_analytics(session)
            ccr_key = ccr.name.lower().replace(" ", "_")
            ccr_utilization[ccr_key] = analytics
            total_capacity += analytics["capacity"]
            total_demand += analytics["total_demand"]
        
        return {
            "organization_id": organization_id,
            "ccr_count": len(ccrs),
            "ccr_utilization": ccr_utilization,
            "total_capacity": total_capacity,
            "total_demand": total_demand,
            "overall_utilization": total_demand / total_capacity if total_capacity > 0 else 0.0,
        }
    
    @staticmethod
    def identify_bottlenecks(session: Session, organization_id: str, threshold: float = 1.0) -> List['CCR']:
        """Identify CCRs that are bottlenecks (utilization >= threshold)"""
        ccrs = session.query(CCR).filter_by(organization_id=organization_id, is_active=True).all()
        bottlenecks = []
        
        for ccr in ccrs:
            analytics = ccr.get_analytics(session)
            if analytics["utilization"] >= threshold:
                bottlenecks.append(ccr)
        
        # Sort by utilization (highest first)
        bottlenecks.sort(key=lambda c: c.get_analytics(session)["utilization"], reverse=True)
        return bottlenecks
    
    def __repr__(self):
        return f"<CCR(id={self.id}, name='{self.name}', type='{self.ccr_type.value}', capacity={self.capacity_per_time_unit})>"