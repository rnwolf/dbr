# src/dbr/models/role.py
from sqlalchemy import Column, String, Enum
from dbr.models.base import BaseModel
import enum


class RoleName(enum.Enum):
    """System role names enumeration"""
    SUPER_ADMIN = "Super Admin"
    ORGANIZATION_ADMIN = "Organization Admin"
    PLANNER = "Planner"
    WORKER = "Worker"
    VIEWER = "Viewer"


class Role(BaseModel):
    """Role model representing system-defined roles and permissions"""
    __tablename__ = "roles"
    
    # Role information
    name = Column(Enum(RoleName), nullable=False, unique=True)
    description = Column(String(500), nullable=False)
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name.value}')>"