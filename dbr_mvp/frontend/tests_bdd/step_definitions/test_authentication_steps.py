from pytest_bdd import scenarios, given, when, then, parsers
from dbrsdk import Dbrsdk


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
def registered_user(test_data_manager, username, password, email, display_name):
    """Create a registered user and log in to get a token for the data manager."""
    import uuid
    unique_username = f"{username}_{str(uuid.uuid4())[:8]}"
    unique_email = f"{str(uuid.uuid4())[:8]}_{email}"
    user = test_data_manager.create_user(unique_username, password, unique_email, display_name)
    response = test_data_manager.sdk.authentication.login(username=unique_username, password=password)
    test_data_manager.sdk = Dbrsdk(server_url=BASE_URL, http_bearer=response.access_token)


@when(parsers.parse('the user authenticates with username "{username}" and password "{password}"'
))
def authenticate_user(username, password, context):
    """Authenticate the user."""
    sdk = Dbrsdk(server_url=BASE_URL)
    response = sdk.authentication.login(username=username, password=password)
    context["token"] = response.access_token


@then('the user should receive an access token')
def received_access_token(context):
    """Check that an access token was received."""
    assert context["token"] is not None


@then('the user information should be retrieved successfully')
def retrieved_user_information(context):
    """Check that user information can be retrieved."""
    sdk = Dbrsdk(server_url=BASE_URL, http_bearer=context["token"])
    user_info = sdk.authentication.get_current_user_info()
    assert user_info is not None
