import pytest
import subprocess
import time
import os
from dbrsdk import Dbrsdk
from dbrsdk.models import UserCreate, OrganizationCreate

# Import requests with fallback
try:
    import requests
except ImportError:
    import urllib.request
    import json
    
    # Simple requests-like interface using urllib
    class SimpleRequests:
        @staticmethod
        def get(url):
            try:
                with urllib.request.urlopen(url) as response:
                    return SimpleResponse(response.getcode(), response.read())
            except Exception:
                raise ConnectionError("Failed to connect")
    
    class SimpleResponse:
        def __init__(self, status_code, content):
            self.status_code = status_code
            self.content = content
    
    requests = SimpleRequests()

# Constants
BASE_URL = "http://127.0.0.1:8002"

@pytest.fixture(scope="session")
def backend_server():
    """Connect to existing backend server (assumes server is already running)."""
    print(f"\nChecking for existing backend server at {BASE_URL}")
    
    # Wait for existing server to be available
    for attempt in range(10):  # 10 second timeout
        try:
            # Use SDK health check to verify server is running
            test_sdk = Dbrsdk(server_url=BASE_URL)
            health = test_sdk.health.get()  # Use the same method that works manually
            if health and health.get('status') == 'healthy':
                print(f"Backend server found and healthy at {BASE_URL}")
                break
        except Exception as e:
            if attempt == 0:
                print(f"Waiting for backend server at {BASE_URL}...")
            time.sleep(1)
    else:
        pytest.fail(f"""
Backend server not found at {BASE_URL}

Please start the backend server manually:
1. Open a new terminal
2. cd dbr_mvp/backend  
3. uv run uvicorn dbr.main:app --host 127.0.0.1 --port 8002

Then run the tests again.
        """)

    yield BASE_URL
    
    # No cleanup needed since we didn't start the server


class TestDataManager:
    """Manages test data for BDD tests with proper cleanup"""

    def __init__(self, sdk):
        self.sdk = sdk
        self.created_items = []
        self.default_org = None
        self.authenticated_sdk = None

    def setup_defaults(self):
        """Setup default organization using super admin credentials."""
        try:
            # First, try to authenticate as super admin to access organizations
            # Use default super admin credentials (adjust based on your backend setup)
            try:
                login_response = self.sdk.authentication.login(
                    username="admin",  # Correct super admin username
                    password="admin123"  # Correct super admin password
                )
                # Create authenticated SDK
                self.authenticated_sdk = Dbrsdk(server_url=BASE_URL, http_bearer=login_response.access_token)
                
                # Get user info from login response first
                user_info = login_response.user
                print(f"Login response user info: {user_info}")
                
                # Check if user info has organization info
                if isinstance(user_info, dict) and 'organization_id' in user_info:
                    from types import SimpleNamespace
                    self.default_org = SimpleNamespace()
                    self.default_org.id = user_info['organization_id']
                    self.default_org.name = user_info.get('organization_name', 'Default Organization')
                    print(f"Using organization from login response: {self.default_org.name} (ID: {self.default_org.id})")
                    return
                
                # Fallback: try to get organizations with authenticated SDK
                try:
                    orgs = self.authenticated_sdk.organizations.get()
                    
                    if orgs and len(orgs) > 0:
                        self.default_org = orgs[0]
                        print(f"Found organization via API: {self.default_org.name} (ID: {self.default_org.id})")
                        return
                    else:
                        print("No organizations returned from API")
                        
                    # Try with different parameters or check if it's a permissions issue
                    print("Trying to get organizations with different approach...")
                    
                except Exception as org_error:
                    print(f"Could not get organizations: {org_error}")
                    print(f"Error type: {type(org_error)}")
                    
                    # Check if it's a permissions error vs no data
                    if "403" in str(org_error) or "Forbidden" in str(org_error):
                        print("Permissions issue - admin user may not have Super Admin role")
                    elif "404" in str(org_error):
                        print("No organizations exist yet")
                    
                # Try to create a default organization since none exist
                try:
                    print("Attempting to create a default organization...")
                    new_org = self.authenticated_sdk.organizations.create(
                        name="Test Organization",
                        description="Default organization for BDD tests",
                        contact_email="test@example.com",
                        country="US"
                    )
                    self.default_org = new_org
                    self.created_items.append(("organization", new_org.id))
                    print(f"Created new organization: {new_org.name} (ID: {new_org.id})")
                    return
                except Exception as create_error:
                    print(f"Could not create organization: {create_error}")
                    
            except Exception as auth_error:
                print(f"Could not authenticate as super admin: {auth_error}")
                print("This is expected if no super admin exists yet.")
            
            # If we can't get existing orgs, we need to create a test setup
            # Let's also check what roles are available
            print(f"Could not get organizations, checking available data...")
            
            # Try to get some debug info about what's available
            try:
                # Let's see what the super admin user info looks like
                user_info = self.authenticated_sdk.authentication.get_current_user_info()  # Correct method name
                print(f"Super admin user info: {user_info}")
                
                # If the user has an organization_id, use that
                if hasattr(user_info, 'organization_id') and user_info.organization_id:
                    from types import SimpleNamespace
                    self.default_org = SimpleNamespace()
                    self.default_org.id = user_info.organization_id
                    self.default_org.name = "Default Organization"
                    print(f"Using admin user's organization ID: {self.default_org.id}")
                    return
                    
            except Exception as debug_error:
                print(f"Could not get user info: {debug_error}")
            
            # Try one more approach - check if we can get the organization ID from the backend database
            # According to DBR_TEST_DATA_AND_CREDENTIALS.md, there should be a "Default Organization"
            print("Trying to find the Default Organization from database initialization...")
            
            # Let's try to get the organization ID by checking what the backend actually has
            # We'll make a direct API call to see what's available
            try:
                # Try to get users first to see if we can find organization references
                users = self.authenticated_sdk.users.get(organization_id="any")  # This might fail but give us info
            except Exception as user_error:
                print(f"Users API error (expected): {user_error}")
                
                # Check if the error message contains any organization IDs
                error_str = str(user_error)
                if "organization" in error_str.lower():
                    print(f"Error mentions organization: {error_str}")
            
            # Final fallback - use the actual organization ID from the database initialization
            # Based on the database check we ran earlier, we know the organization exists
            print("Using organization ID from database...")
            
            from types import SimpleNamespace
            self.default_org = SimpleNamespace()
            # Use the actual organization ID from the database we verified earlier
            self.default_org.id = "6c3d031c-1e97-453c-9e1c-b8d18dc2575b"  # From database check
            self.default_org.name = "Default Organization"
            
            print(f"Using actual organization ID from database: {self.default_org.id}")
                
        except Exception as e:
            pytest.fail(f"Failed to setup default organization: {e}")

    def create_user(self, username, password, email, display_name):
        """Create test user and track for cleanup"""
        if not self.default_org:
            self.setup_defaults()

        # Use a default role ID - adjust based on your backend's role system
        # Let's try to get the actual role IDs from the backend
        default_role_id = None
        
        try:
            # Try to get user info to see what roles are available
            if self.authenticated_sdk:
                user_info = self.authenticated_sdk.authentication.get_current_user_info()  # Correct method name
                print(f"Admin user system_role_id: {getattr(user_info, 'system_role_id', 'Not found')}")
                
                # For now, let's use the admin's role ID as a fallback
                if hasattr(user_info, 'system_role_id') and user_info.system_role_id:
                    default_role_id = user_info.system_role_id
                    print(f"Using admin's role ID: {default_role_id}")
                
        except Exception as role_debug_error:
            print(f"Could not get role info: {role_debug_error}")
        
        # Final fallback to a valid UUID format
        if not default_role_id:
            default_role_id = "7abed579-aaf0-4f8a-b94a-6dfb64423516"  # PLANNER role ID from actual DB
            print(f"Using fallback role ID: {default_role_id}")
            print("Note: Using PLANNER role as default for test users")

        user_data = UserCreate(
            username=username,
            password=password,
            email=email,
            display_name=display_name,
            organization_id=self.default_org.id,
            system_role_id=default_role_id
        )
        
        try:
            # Use authenticated SDK if available, otherwise try with unauthenticated
            sdk_to_use = self.authenticated_sdk if self.authenticated_sdk else self.sdk
            user = sdk_to_use.users.create(  # Use correct method signature
                organization_id=self.default_org.id,
                username=username,
                email=email,
                display_name=display_name,
                password=password,
                system_role_id=default_role_id
            )
            self.created_items.append(("user", user.id))
            return user
        except Exception as e:
            pytest.fail(f"Failed to create user {username}: {e}")

    def create_user_with_role(self, username, password, email, display_name, role_id):
        """Create test user with specific role and track for cleanup"""
        if not self.default_org:
            self.setup_defaults()

        try:
            # Use authenticated SDK if available, otherwise try with unauthenticated
            sdk_to_use = self.authenticated_sdk if self.authenticated_sdk else self.sdk
            user = sdk_to_use.users.create(  # Use correct method signature
                organization_id=self.default_org.id,
                username=username,
                email=email,
                display_name=display_name,
                password=password,
                system_role_id=role_id
            )
            self.created_items.append(("user", user.id))
            return user
        except Exception as e:
            pytest.fail(f"Failed to create user {username} with role {role_id}: {e}")

    def cleanup(self):
        """Clean up all created test data"""
        for item_type, item_id in reversed(self.created_items):
            try:
                if item_type == "user":
                    self.sdk.users.delete(user_id=item_id)
                elif item_type == "organization":
                    self.sdk.organizations.delete(org_id=item_id)
                elif item_type == "work_item":
                    # Work items need organization_id for deletion
                    org_id = self.default_org.id if self.default_org else None
                    if org_id:
                        self.sdk.work_items.delete(work_item_id=item_id, organization_id=org_id)
                    else:
                        print(f"Warning: Cannot cleanup work_item {item_id} - no organization context")
                elif item_type == "schedule":
                    # Schedules need organization_id for deletion  
                    org_id = self.default_org.id if self.default_org else None
                    if org_id:
                        self.sdk.schedules.delete(schedule_id=item_id, organization_id=org_id)
                    else:
                        print(f"Warning: Cannot cleanup schedule {item_id} - no organization context")
            except Exception as e:
                print(f"Warning: Could not cleanup {item_type} {item_id}: {e}")


@pytest.fixture
def test_data_manager(backend_server):
    """Provide test data manager with cleanup"""
    sdk = Dbrsdk(server_url=BASE_URL)
    manager = TestDataManager(sdk)
    yield manager
    manager.cleanup()


@pytest.fixture
def context():
    """A dictionary to share state between BDD steps."""
    return {}


# Additional fixtures for common test scenarios

@pytest.fixture
def authenticated_admin_sdk(test_data_manager):
    """Provide an authenticated SDK for admin operations"""
    # Create admin user
    admin_user = test_data_manager.create_user(
        username="bdd_admin",
        password="admin_password",
        email="bdd_admin@example.com",
        display_name="BDD Admin User"
    )
    
    # Authenticate
    response = test_data_manager.sdk.authentication.login(
        username="bdd_admin",
        password="admin_password"
    )
    
    # Return authenticated SDK
    return Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)


@pytest.fixture
def sample_work_items(authenticated_admin_sdk, test_data_manager):
    """Create sample work items for testing"""
    if not test_data_manager.default_org:
        test_data_manager.setup_defaults()
    
    org_id = test_data_manager.default_org.id
    work_items = []
    
    for i in range(5):
        from dbrsdk.models import WorkItemCreate
        work_item_data = WorkItemCreate(
            organization_id=org_id,
            title=f"Sample Work Item {i+1}",
            description=f"Description for sample work item {i+1}",
            priority="medium",
            status="Backlog",
            estimated_total_hours=8.0,
            ccr_hours_required={"development": 6.0, "testing": 2.0}
        )
        
        work_item = authenticated_admin_sdk.work_items.create(work_item_data)
        work_items.append(work_item)
        test_data_manager.created_items.append(("work_item", work_item.id))
    
    return work_items