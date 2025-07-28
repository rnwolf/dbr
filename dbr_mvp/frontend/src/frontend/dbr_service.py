"""Service layer for interacting with the DBR backend."""

from typing import Optional, Dict, Any, List
from dbrsdk import Dbrsdk


class DBRService:
    """A service class to encapsulate DBR SDK interactions with frontend-specific features."""

    def __init__(self, base_url: str):
        """Initializes the DBRService."""
        self.base_url = base_url
        self.client = Dbrsdk(server_url=base_url)
        self._token = None
        self._user_info = None
        self._current_organization = None
        self._user_role = None
        self._authenticated_client = None

    def health_check(self) -> bool:
        """Performs a health check against the backend using the SDK."""
        try:
            response = self.client.health.get()
            if isinstance(response, dict) and response.get('status') == 'healthy':
                print("Backend health check successful.")
                return True
            print(f"Backend health check failed: Invalid response: {response}")
            return False
        except Exception as e:
            print(f"Backend health check failed: {e}")
            return False

    def login(self, username: str, password: str) -> bool:
        """Logs in the user and stores authentication context."""
        try:
            response = self.client.authentication.login(username=username, password=password)
            
            if response and hasattr(response, 'access_token') and response.access_token:
                self._token = response.access_token
                
                # Extract user information from login response
                if hasattr(response, 'user') and response.user:
                    self._user_info = response.user
                
                # Role information is not included in login response
                # We'll need to fetch it separately or get it from user memberships
                self._user_role = None  # Will be set by _fetch_user_role()
                
                # Create authenticated client for future API calls
                self._authenticated_client = Dbrsdk(
                    server_url=self.base_url,
                    http_bearer=self._token
                )
                
                # Fetch additional user information including role
                self._fetch_user_role()
                
                # Auto-select organization context (Default Organization for now)
                self._setup_organization_context()
                
                print(f"Login successful for user: {username}")
                return True
            return False
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def logout(self) -> None:
        """Clears authentication context and logs out the user."""
        self._token = None
        self._user_info = None
        self._current_organization = None
        self._user_role = None
        self._authenticated_client = None
        print("User logged out successfully.")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated."""
        return self._token is not None and self._authenticated_client is not None

    def get_token(self) -> Optional[str]:
        """Returns the stored token."""
        return self._token

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Returns the current user information."""
        return self._user_info

    def get_user_role(self) -> Optional[str]:
        """Returns the current user's role."""
        return self._user_role

    def get_current_organization(self) -> Optional[Dict[str, Any]]:
        """Returns the current organization context."""
        return self._current_organization

    def _fetch_user_role(self) -> None:
        """Fetch user role information from backend."""
        try:
            if not self._authenticated_client:
                return
            
            # Try to get current user info which might include role details
            # Note: The backend /auth/me endpoint may not include role info
            # For now, we'll try to infer role from user info or set a default
            
            # Check if user info has system_role_id or other role indicators
            if self._user_info:
                user_id = self._user_info.get('id')
                username = self._user_info.get('username', '')
                
                # For now, map usernames to roles based on actual database users
                # In a real implementation, this would query the backend for role info
                role_mapping = {
                    'admin': 'Organization Admin',
                    'orgadmin': 'Organization Admin',
                    'planner': 'Planner',
                    'testuser': 'Planner',
                    'testuser_workitems': 'Planner',
                    'testuser_system': 'Planner',
                    'viewer': 'Viewer',
                    'viewer2': 'Viewer'
                }
                
                self._user_role = role_mapping.get(username, 'Unknown Role')
                print(f"User role determined: {self._user_role}")
            
        except Exception as e:
            print(f"Failed to fetch user role: {e}")
            self._user_role = 'Unknown Role'

    def _setup_organization_context(self) -> None:
        """Setup organization context after login."""
        try:
            if not self._authenticated_client:
                return
                
            # For now, assume single organization (Default Organization)
            # In future, this could query user's organizations and allow selection
            self._current_organization = {
                "id": "default-org-id",
                "name": "Default Organization",
                "auto_selected": True
            }
            print(f"Organization context set to: {self._current_organization['name']}")
            
        except Exception as e:
            print(f"Failed to setup organization context: {e}")

    def has_permission(self, permission: str) -> bool:
        """Check if current user has specific permission based on role."""
        if not self._user_role:
            return False
            
        # Role-based permission mapping
        role_permissions = {
            "Super Admin": ["*"],  # All permissions
            "Org Admin": [
                "manage_users", "manage_ccrs", "manage_schedules", 
                "manage_work_items", "manage_collections", "view_analytics"
            ],
            "Planner": [
                "manage_schedules", "manage_work_items", "manage_collections", 
                "view_analytics"
            ],
            "Worker": [
                "update_work_items", "view_schedules", "view_work_items"
            ],
            "Viewer": [
                "view_schedules", "view_work_items", "view_collections", 
                "view_analytics"
            ]
        }
        
        user_permissions = role_permissions.get(self._user_role, [])
        
        # Super Admin has all permissions
        if "*" in user_permissions:
            return True
            
        return permission in user_permissions

    def get_authenticated_client(self) -> Optional[Dbrsdk]:
        """Returns the authenticated SDK client for API calls."""
        return self._authenticated_client

    def get_connection_status(self) -> Dict[str, Any]:
        """Get comprehensive connection and authentication status."""
        return {
            "backend_url": self.base_url,
            "backend_healthy": self.health_check(),
            "authenticated": self.is_authenticated(),
            "user": self._user_info,
            "role": self._user_role,
            "organization": self._current_organization,
            "token_available": self._token is not None
        }
