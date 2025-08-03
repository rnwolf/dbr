import pytest
import customtkinter as ctk
import sys
import os
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture(scope="session", autouse=True)
def mock_dbrsdk():
    """Mock the entire dbrsdk to prevent import errors."""
    with patch.dict('sys.modules', {
        'dbrsdk': MagicMock(),
        'dbrsdk.models': MagicMock(),
    }) as mock:
        yield mock

@pytest.fixture(scope="session")
def root_app():
    app = ctk.CTk()
    yield app
    app.destroy()