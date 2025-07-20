# src/dbr/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from dbr.models.base import BaseModel


class User(BaseModel):
    """User model representing application users"""
    __tablename__ = "users"
    
    # Basic user information
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    active_status = Column(Boolean, nullable=False, default=True)
    last_login_date = Column(DateTime, nullable=True)
    
    # Role relationship
    system_role_id = Column(String(36), ForeignKey('roles.id'), nullable=False)
    
    # Relationship to role (will be loaded when needed)
    # role = relationship("Role", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"