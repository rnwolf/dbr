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
            # Assuming the health check endpoint is under an 'api_health' group in the SDK
            response = self.client.api_health.get()
            # The actual response structure will depend on the OpenAPI spec.
            # We'll assume a simple successful status for now.
            if response and getattr(response, 'status', None) == 'ok':
                print("Backend health check successful.")
                return True
            print("Backend health check failed: Invalid response.")
            return False
        except Exception as e:
            print(f"Backend health check failed: {e}")
            return False

    def login(self, username, password) -> bool:
        """Logs in the user and stores the token."""
        try:
            login_request = LoginRequest(username=username, password=password)
            response = self.client.authentication.login(login_request)
            if response and response.access_token:
                self._token = response.access_token
                return True
            return False
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def get_token(self) -> str:
        """Returns the stored token."""
        return self._token
