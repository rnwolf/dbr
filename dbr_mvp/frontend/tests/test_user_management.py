"""Tests for user management features, following project testing guidelines."""

import pytest
from unittest.mock import Mock, patch

# Import the classes to be tested
from frontend.components.create_user_dialog import CreateUserDialog
from frontend.pages.user_management_page import UserManagementPage


# --- Fixtures for CreateUserDialog ---
@pytest.fixture
def mocked_create_user_dialog(mocker):
    """Fixture for a fully mocked CreateUserDialog instance."""
    mock_parent = Mock()
    mock_parent.refresh_user_list = Mock()
    mock_dbr_service = Mock()
    mock_dbr_service.get_available_roles.return_value = ["Planner", "Worker", "Viewer"]

    mocker.patch(
        "frontend.components.create_user_dialog.CreateUserDialog.__init__",
        return_value=None,
    )
    mock_messagebox = mocker.patch("frontend.components.create_user_dialog.messagebox")

    dialog = CreateUserDialog(mock_parent, mock_dbr_service)
    dialog.parent = mock_parent
    dialog.dbr_service = mock_dbr_service
    dialog.username_entry = Mock()
    dialog.password_entry = Mock()
    dialog.role_combobox = Mock()
    dialog.destroy = Mock()

    return dialog, mock_parent, mock_dbr_service, mock_messagebox


# --- Fixtures for UserManagementPage ---
@pytest.fixture
def mocked_user_management_page(mocker):
    """Fixture for a fully mocked UserManagementPage instance."""
    mock_parent = Mock()
    mock_dbr_service = Mock()

    # Mock the return value for get_users
    mock_dbr_service.get_users.return_value = [
        {"username": "testuser1", "role": "Planner", "status": "active"},
        {"username": "testuser2", "role": "Worker", "status": "inactive"},
    ]

    # Mock all the UI components that UserManagementPage uses
    mocker.patch(
        "frontend.pages.user_management_page.UserManagementPage.__init__",
        return_value=None,
    )
    mocker.patch("frontend.pages.user_management_page.ctk.CTkLabel")
    mocker.patch("frontend.pages.user_management_page.ctk.CTkButton")
    mocker.patch("frontend.pages.user_management_page.ctk.CTkFont")
    mocker.patch("frontend.pages.user_management_page.CreateUserDialog")

    page = UserManagementPage(mock_parent, mock_dbr_service)
    page.dbr_service = mock_dbr_service
    # Add a mock for the frame that will contain the user list
    page.user_list_frame = Mock()
    page.user_list_frame.winfo_children.return_value = []  # Return an empty list for the first call

    return page, mock_parent, mock_dbr_service


class TestCreateUserDialog:
    """Test cases for the CreateUserDialog component."""

    def test_user_creation_success(self, mocked_create_user_dialog):
        """Test successful user creation behavior."""
        dialog, parent, dbr_service, mock_messagebox = mocked_create_user_dialog
        dialog.username_entry.get.return_value = "newuser"
        dialog.password_entry.get.return_value = "password123"
        dialog.role_combobox.get.return_value = "Planner"
        dbr_service.create_user.return_value = (True, "User created successfully.")

        CreateUserDialog.create_user(dialog)

        dbr_service.create_user.assert_called_once_with(
            "newuser", "password123", "Planner"
        )
        mock_messagebox.showinfo.assert_called_once_with(
            "Success", "User created successfully."
        )
        parent.refresh_user_list.assert_called_once()
        dialog.destroy.assert_called_once()

    def test_user_creation_validation(self, mocked_create_user_dialog):
        """Test form validation for user creation."""
        dialog, _, _, mock_messagebox = mocked_create_user_dialog
        dialog.username_entry.get.return_value = ""
        dialog.password_entry.get.return_value = "password123"

        CreateUserDialog.create_user(dialog)

        mock_messagebox.showerror.assert_called_once_with(
            "Validation Error", "Username and password are required."
        )

    def test_user_creation_api_error(self, mocked_create_user_dialog):
        """Test handling of API errors during user creation."""
        dialog, _, dbr_service, mock_messagebox = mocked_create_user_dialog
        dialog.username_entry.get.return_value = "newuser"
        dialog.password_entry.get.return_value = "password123"
        dialog.role_combobox.get.return_value = "Planner"
        dbr_service.create_user.return_value = (False, "API Error")

        CreateUserDialog.create_user(dialog)

        mock_messagebox.showerror.assert_called_once_with("Error", "API Error")


class TestUserManagementPage:
    """Test cases for the UserManagementPage."""

    @patch("frontend.pages.user_management_page.ctk.CTkFrame")
    def test_user_list_display(self, mock_frame, mocked_user_management_page, mocker):
        """Test that the user list is displayed correctly on refresh."""
        page, _, dbr_service = mocked_user_management_page

        # Mock the label and button creation for the user rows
        mock_label = mocker.patch("frontend.pages.user_management_page.ctk.CTkLabel")
        mock_button = mocker.patch("frontend.pages.user_management_page.ctk.CTkButton")

        # Act
        UserManagementPage.refresh_user_list(page)

        # Assert
        dbr_service.get_users.assert_called_once()

        # Two users are returned from the service, so we expect 2 username labels, 2 role labels, etc.
        # Plus the header labels
        assert mock_label.call_count == 10  # Header(4) + User1(3) + User2(3)
        assert mock_button.call_count == 4  # User1(Edit, Remove) + User2(Edit, Remove)

    @patch("frontend.pages.user_management_page.ctk.CTkFrame")
    def test_user_list_refresh_clears_old_widgets(
        self, mock_frame, mocked_user_management_page
    ):
        """Test that refreshing the user list clears old widgets first."""
        page, _, _ = mocked_user_management_page

        # Simulate existing widgets in the frame
        mock_old_widget = Mock()
        page.user_list_frame.winfo_children.return_value = [mock_old_widget]

        # Act
        UserManagementPage.refresh_user_list(page)

        # Assert
        mock_old_widget.destroy.assert_called_once()
