"""Service layer for interacting with the DBR backend."""

from dbrsdk import Dbrsdk
from dbrsdk.models import LoginRequest

class DBRService:
    """A service class to encapsulate DBR SDK interactions."""

    def __init__(self, base_url: str):
        """Initializes the DBRService."""
        self.client = Dbrsdk(server_url=base_url)
        self._token = None

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

    def login(self, username, password) -> bool:
        """Logs in the user and stores the token."""
        try:
            login_request = LoginRequest(username=username, password=password)
            response = self.client.authentication.login(login_request)
            if response and hasattr(response, 'access_token') and response.access_token:
                self._token = response.access_token
                return True
            return False
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def get_token(self) -> str:
        """Returns the stored token."""
        return self._token
