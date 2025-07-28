#!/usr/bin/env python3
"""
Main application entry point.
"""
import customtkinter as ctk
from frontend.main_window import MainWindow
from frontend.backend_config_dialog import BackendConfigDialog
from frontend.authentication_ui import AuthenticationManager
from utils.config import AppConfig


def main():
    """Initialize and run the application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
    ctk.set_default_color_theme(AppConfig.COLOR_THEME)

    # Get backend URL from user
    config_dialog = BackendConfigDialog(None)
    backend_url = config_dialog.get_url()

    if backend_url:
        # Run authentication workflow
        auth_manager = AuthenticationManager(backend_url)
        authenticated_service = auth_manager.authenticate()
        
        if authenticated_service:
            # Create and run application with authenticated service
            app = MainWindow(authenticated_service)
            app.run()
        else:
            print("Authentication cancelled or failed. Exiting application.")


if __name__ == "__main__":
    main()
