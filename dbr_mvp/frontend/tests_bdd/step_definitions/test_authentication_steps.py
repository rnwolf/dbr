from pytest_bdd import scenarios, given, when, then, parsers
from dbrsdk import Dbrsdk
from ..conftest import backend_server, test_data_manager, context


# Constants
BASE_URL = "http://127.0.0.1:8002"

# Scenarios
scenarios('../features/authentication.feature')


@given('a running backend server')
def running_backend_server(backend_server):
    """Check that the backend server is running."""
    pass


@given(parsers.parse('a registered user with username "{username}", password "{password}", email "{email}" and display name "{display_name}"'
))
def registered_user(test_data_manager, username, password, email, display_name, context):
    """Create a registered user and log in to get a token for the data manager."""
    import uuid
    unique_username = f"{username}_{str(uuid.uuid4())[:8]}"
    unique_email = f"{str(uuid.uuid4())[:8]}_{email}"
    
    # Use create_user_with_role method with default planner role
    user = test_data_manager.create_user_with_role(
        username=unique_username,
        password=password,
        email=unique_email,
        display_name=display_name,
        role_name="planner"  # Default role for authentication tests
    )
    
    # Store user credentials in context for later authentication
    context["test_username"] = unique_username
    context["test_password"] = password
    context["test_user"] = user


@when(parsers.parse('the user authenticates with username "{username}" and password "{password}"'
))
def authenticate_user(username, password, context):
    """Authenticate the user."""
    sdk = Dbrsdk(server_url=BASE_URL)
    
    # Use the actual test user credentials from context, not the template ones from feature file
    actual_username = context.get("test_username", username)
    actual_password = context.get("test_password", password)
    
    try:
        response = sdk.authentication.login(username=actual_username, password=actual_password)
        context["token"] = response.access_token
        context["login_success"] = True
    except Exception as e:
        context["login_error"] = str(e)
        context["login_success"] = False


@then('the user should receive an access token')
def received_access_token(context):
    """Check that an access token was received."""
    assert context.get("login_success", False), f"Login failed: {context.get('login_error', 'Unknown error')}"
    assert context.get("token") is not None, "Access token should be received"


@then('the user information should be retrieved successfully')
def retrieved_user_information(context):
    """Check that user information can be retrieved."""
    token = context.get("token")
    assert token is not None, "Token should be available for user info retrieval"
    
    try:
        sdk = Dbrsdk(server_url=BASE_URL, http_bearer=token)
        user_info = sdk.authentication.get_current_user_info()
        assert user_info is not None, "User information should be retrieved"
        
        # Verify the user info contains expected fields
        assert hasattr(user_info, 'username'), "User info should contain username"
        assert hasattr(user_info, 'email'), "User info should contain email"
        
        context["user_info_success"] = True
        context["user_info"] = user_info
    except Exception as e:
        context["user_info_error"] = str(e)
        context["user_info_success"] = False
        raise AssertionError(f"Failed to retrieve user information: {e}")
