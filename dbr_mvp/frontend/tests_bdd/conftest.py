import pytest
import time
import uuid
from dbrsdk import Dbrsdk
from dbrsdk.models import UserCreate, OrganizationCreate, MembershipCreate

# Constants
BASE_URL = "http://127.0.0.1:8002"

@pytest.fixture(scope="session")
def backend_server():
    """Connect to existing backend server (assumes server is already running)."""
    print(f"\nChecking for existing backend server at {BASE_URL}")
    for attempt in range(10):
        try:
            test_sdk = Dbrsdk(server_url=BASE_URL)
            health = test_sdk.health.get()
            if health and health.get('status') == 'healthy':
                print(f"Backend server found and healthy at {BASE_URL}")
                break
        except Exception:
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

@pytest.fixture(scope="session")
def super_admin_sdk():
    """Provide an authenticated SDK for the super admin."""
    sdk = Dbrsdk(server_url=BASE_URL)
    try:
        login_response = sdk.authentication.login(username="admin", password="admin123")
        return Dbrsdk(server_url=BASE_URL, http_bearer=login_response.access_token)
    except Exception as e:
        pytest.fail(f"Failed to authenticate as super admin: {e}")

@pytest.fixture(scope="session")
def roles(super_admin_sdk):
    """Fixture to get all roles from the backend."""
    try:
        orgs = super_admin_sdk.organizations.get()
        default_org = next((org for org in orgs if org.name == "Default Organization"), None)
        if not default_org:
            pytest.fail("Default Organization not found.")

        users = super_admin_sdk.users.get(organization_id=default_org.id)
        
        role_map = {}
        for user in users:
            if user.username == "admin":
                role_map["SUPER_ADMIN"] = user.system_role_id
            elif user.username == "orgadmin":
                role_map["ORGANIZATION_ADMIN"] = user.system_role_id
            elif user.username == "planner":
                role_map["PLANNER"] = user.system_role_id
            elif user.username == "worker":
                role_map["WORKER"] = user.system_role_id
            elif user.username == "viewer":
                role_map["VIEWER"] = user.system_role_id
        
        if len(role_map) < 5:
            pytest.fail("Failed to map all roles from test users.")
            
        return role_map
    except Exception as e:
        pytest.fail(f"Failed to retrieve roles: {e}")

@pytest.fixture
def test_organization(super_admin_sdk):
    """Create a new organization for the test session and clean it up afterward."""
    unique_id = str(uuid.uuid4())[:8]
    try:
        organization = super_admin_sdk.organizations.create(
            name=f"Test Org_{unique_id}",
            description="A test organization for BDD",
            contact_email=f"test_{unique_id}@example.com",
            country="US",
            subscription_level="basic"
        )
        yield organization
        # Cleanup
        try:
            super_admin_sdk.organizations.delete(org_id=organization.id)
        except Exception as e:
            print(f"Warning: Could not cleanup organization {organization.id}: {e}")
    except Exception as e:
        pytest.fail(f"Failed to create test organization: {e}")


@pytest.fixture
def org_admin_user(super_admin_sdk, test_organization, roles):
    """Create an organization admin for the test organization."""
    unique_id = str(uuid.uuid4())[:8]
    try:
        user = super_admin_sdk.users.create(
            organization_id=test_organization.id,
            username=f"org_admin_{unique_id}",
            password="org_admin_password",
            email=f"org_admin_{unique_id}@example.com",
            display_name="Org Admin",
            system_role_id=roles["ORGANIZATION_ADMIN"]
        )
        yield user
        # Cleanup
        try:
            super_admin_sdk.users.delete(user_id=user.id)
        except Exception as e:
            print(f"Warning: Could not cleanup org_admin_user {user.id}: {e}")
    except Exception as e:
        pytest.fail(f"Failed to create org_admin_user: {e}")

@pytest.fixture
def authenticated_org_admin_sdk(org_admin_user):
    """Provide an authenticated SDK for the organization admin."""
    sdk = Dbrsdk(server_url=BASE_URL)
    try:
        login_response = sdk.authentication.login(
            username=org_admin_user.username,
            password="org_admin_password"
        )
        return Dbrsdk(server_url=BASE_URL, http_bearer=login_response.access_token)
    except Exception as e:
        pytest.fail(f"Failed to authenticate as org_admin_user: {e}")

class TestDataManager:
    """Manages test data for BDD tests with proper cleanup"""

    def __init__(self, sdk, org_id, roles):
        self.sdk = sdk
        self.org_id = org_id
        self.roles = roles
        self.created_items = []

    def create_user_with_role(self, username, password, email, display_name, role_name):
        """Create test user with specific role and track for cleanup"""
        role_id = self.roles.get(role_name.upper())
        if not role_id:
            pytest.fail(f"Role '{role_name}' not found in roles fixture.")

        try:
            user = self.sdk.users.create(
                organization_id=self.org_id,
                username=username,
                email=email,
                display_name=display_name,
                password=password,
                system_role_id=role_id
            )
            self.created_items.append(("user", user.id))
            return user
        except Exception as e:
            pytest.fail(f"Failed to create user {username} with role {role_name}: {e}")

    def cleanup(self):
        """Clean up all created test data"""
        for item_type, item_id in reversed(self.created_items):
            try:
                if item_type == "user":
                    self.sdk.users.delete(user_id=item_id)
                # Add other cleanup logic as needed
            except Exception as e:
                print(f"Warning: Could not cleanup {item_type} {item_id}: {e}")

@pytest.fixture
def test_data_manager(authenticated_org_admin_sdk, test_organization, roles):
    """Provide test data manager with cleanup"""
    manager = TestDataManager(authenticated_org_admin_sdk, test_organization.id, roles)
    yield manager
    manager.cleanup()

@pytest.fixture
def context():
    """A dictionary to share state between BDD steps."""
    return {}

@pytest.fixture
def created_user(test_data_manager):
    """Fixture to create and clean up a user with a specific role."""
    created_users = []

    def _create_user(role_name: str):
        import uuid
        unique_id = str(uuid.uuid4())[:8]

        user = test_data_manager.create_user_with_role(
            username=f"{role_name}_{unique_id}",
            password=f"{role_name}_password",
            email=f"{role_name}_{unique_id}@example.com",
            display_name=f"{role_name.title()} User",
            role_name=role_name
        )
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup is handled by the test_data_manager fixture

@pytest.fixture
def planner_user(created_user):
    """Create a planner user."""
    return created_user("planner")

@pytest.fixture
def worker_user(created_user):
    """Create a worker user."""
    return created_user("worker")

@pytest.fixture
def viewer_user(created_user):
    """Create a viewer user."""
    return created_user("viewer")

@pytest.fixture
def org_admin_user_fixture(created_user):
    """Create an organization admin user."""
    return created_user("organization_admin")