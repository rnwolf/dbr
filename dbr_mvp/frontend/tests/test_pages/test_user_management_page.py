import pytest
from unittest.mock import MagicMock, patch
from frontend.pages.user_management_page import UserManagementPage

@pytest.fixture
def mock_dbr_service(mocker):
    service = mocker.MagicMock()
    service.get_users.return_value = []
    return service

def test_user_management_page_init(root_app, mock_dbr_service):
    page = UserManagementPage(root_app, mock_dbr_service)
    assert page.title_label.cget("text") == "User Management"
    assert page.add_user_button.cget("text") == "Add User"
    mock_dbr_service.get_users.assert_called_once()

def test_open_add_user_dialog(root_app, mock_dbr_service):
    page = UserManagementPage(root_app, mock_dbr_service)
    with patch('frontend.pages.user_management_page.CreateUserDialog') as mock_dialog, \
         patch.object(page, 'wait_window') as mock_wait_window:
        page.open_add_user_dialog()
        mock_dialog.assert_called_once_with(page, mock_dbr_service)
        mock_wait_window.assert_called_once_with(mock_dialog.return_value)
