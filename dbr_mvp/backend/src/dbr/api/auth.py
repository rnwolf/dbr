# src/dbr/api/auth.py
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import jwt
import secrets
from dbr.core.database import get_db
from dbr.core.security import authenticate_user, get_user_by_username, get_user_by_email
from dbr.models.user import User
from dbr.models.organization_membership import OrganizationMembership
from dbr.models.role import Role


router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, this should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Dict[str, Any] = Field(..., description="User information")


class UserInfo(BaseModel):
    """User information model"""
    id: str
    username: str
    email: str
    display_name: Optional[str]
    active_status: bool


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user info"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token_payload: dict = Depends(verify_token),
    session: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    user_id = token_payload.get("sub")
    user = session.query(User).filter_by(id=user_id, active_status=True).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@router.post("/login", response_model=LoginResponse)
def login(
    login_request: LoginRequest,
    session: Session = Depends(get_db)
) -> LoginResponse:
    """
    Authenticate user and return JWT token
    
    Accepts either username or email address as the username field.
    """
    
    # Try to find user first (before authentication)
    user_to_check = None
    
    # Check if input looks like an email
    if "@" in login_request.username:
        user_to_check = get_user_by_email(session, login_request.username)
    else:
        user_to_check = get_user_by_username(session, login_request.username)
    
    # Check if user exists and is active before trying authentication
    if user_to_check and not user_to_check.active_status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    # Now try authentication
    user = None
    if "@" in login_request.username:
        user = authenticate_user(session, login_request.username, login_request.password)
    else:
        if user_to_check:
            user = authenticate_user(session, user_to_check.email, login_request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
        )
    
    # Update last login date
    user.last_login_date = datetime.now(timezone.utc)
    session.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username, "email": user.email},
        expires_delta=access_token_expires
    )
    
    # Prepare user info for response
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "active_status": user.active_status
    }
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_info
    )


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserInfo:
    """Get current user information"""
    return UserInfo(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        display_name=current_user.display_name,
        active_status=current_user.active_status
    )


@router.post("/logout")
def logout():
    """
    Logout endpoint (JWT tokens are stateless, so this is mainly for client-side cleanup)
    """
    return {"message": "Successfully logged out"}


# Dependency for role-based access control
def require_role(required_roles: list):
    """Dependency factory for role-based access control"""
    def role_checker(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_db)
    ):
        # Get user's roles across all organizations
        memberships = session.query(OrganizationMembership).filter_by(
            user_id=current_user.id,
            invitation_status="accepted"
        ).all()
        
        user_roles = []
        for membership in memberships:
            role = session.query(Role).filter_by(id=membership.role_id).first()
            if role:
                user_roles.append(role.name.value)
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        
        return current_user
    
    return role_checker