import pytest
from frontend.main import main

def test_main_runs(mocker):
    """Test that the main function runs without errors."""
    mocker.patch('customtkinter.CTk.mainloop')
    main()
