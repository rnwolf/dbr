# src/dbr/models/ccr_user_association.py
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel


class CCRUserAssociation(BaseModel):
    """Association between CCRs and Users with capacity contributions"""
    __tablename__ = "ccr_user_associations"
    
    # Foreign key relationships
    ccr_id = Column(String(36), ForeignKey('ccrs.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # Capacity and skill information
    capacity_contribution = Column(Float, nullable=False)  # Hours per time unit this user contributes
    skill_level = Column(String(50), nullable=True)  # junior, mid, senior, expert, etc.
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships (can be added later when needed)
    # ccr = relationship("CCR", back_populates="user_associations")
    # user = relationship("User", back_populates="ccr_associations")
    
    def __repr__(self):
        return f"<CCRUserAssociation(id={self.id}, ccr_id={self.ccr_id}, user_id={self.user_id}, capacity={self.capacity_contribution})>"