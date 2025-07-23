import pytest
import sys
from pathlib import Path

# Add src to path so we can import from it
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import main

def test_main_runs(mocker):
    """Test that the main function runs without errors."""
    mocker.patch('app.main_window.MainWindow.run')
    main()
