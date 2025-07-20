# src/dbr/core/security.py
import hashlib
import secrets
from typing import Optional
from sqlalchemy.orm import Session


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    
    # Hash the password with salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Return salt + hash (salt is first 32 characters)
    return salt + password_hash


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    if len(hashed_password) < 32:
        return False
    
    # Extract salt (first 32 characters) and hash (rest)
    salt = hashed_password[:32]
    stored_hash = hashed_password[32:]
    
    # Hash the provided password with the stored salt
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Compare hashes
    return password_hash == stored_hash


def authenticate_user(session: Session, email: str, password: str) -> Optional['User']:
    """Authenticate a user by email and password"""
    from dbr.models.user import User
    
    # Find user by email
    user = session.query(User).filter_by(email=email, active_status=True).first()
    
    if user is None:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def get_user_by_email(session: Session, email: str) -> Optional['User']:
    """Get a user by email address"""
    from dbr.models.user import User
    
    return session.query(User).filter_by(email=email, active_status=True).first()


def get_user_by_username(session: Session, username: str) -> Optional['User']:
    """Get a user by username"""
    from dbr.models.user import User
    
    return session.query(User).filter_by(username=username, active_status=True).first()