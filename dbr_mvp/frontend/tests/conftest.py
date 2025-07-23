"""Pytest configuration and fixtures."""

import pytest
import tkinter as tk
import customtkinter as ctk
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def mock_tk():
    """Mock tkinter to avoid GUI during tests."""
    with patch("tkinter.Tk"), patch("customtkinter.CTk"):
        yield


@pytest.fixture
def sample_app():
    """Create a sample application for testing."""
    with patch("customtkinter.CTk"):
        from app.main_window import MainWindow

        app = MainWindow()
        yield app


@pytest.fixture
def mock_messagebox():
    """Mock messagebox for testing."""
    with patch("tkinter.messagebox") as mock_mb:
        yield mock_mb


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set test mode
    os.environ["TESTING"] = "1"
    yield
    # Cleanup
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
