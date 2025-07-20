# src/dbr/models/organization_membership.py
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel
import enum


class InvitationStatus(enum.Enum):
    """Organization membership invitation status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class OrganizationMembership(BaseModel):
    """Links users to organizations with specific roles"""
    __tablename__ = "organization_memberships"
    
    # Foreign key relationships
    organization_id = Column(String(36), ForeignKey('organizations.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    role_id = Column(String(36), ForeignKey('roles.id'), nullable=False)
    
    # Invitation workflow
    invitation_status = Column(Enum(InvitationStatus), nullable=False, default=InvitationStatus.PENDING)
    invited_by_user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    joined_date = Column(DateTime, nullable=True)
    
    # Relationships (can be added later when needed)
    # organization = relationship("Organization", back_populates="memberships")
    # user = relationship("User", back_populates="memberships")
    # role = relationship("Role", back_populates="memberships")
    # invited_by = relationship("User", foreign_keys=[invited_by_user_id])
    
    def __repr__(self):
        return f"<OrganizationMembership(id={self.id}, user_id={self.user_id}, org_id={self.organization_id}, status={self.invitation_status.value})>"