#!/usr/bin/env python3
"""
Main application entry point.
"""
import customtkinter as ctk
from frontend.main_window import MainWindow
from frontend.backend_config_dialog import BackendConfigDialog
from frontend.dbr_service import DBRService
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
        # Initialize DBR Service and perform health check
        dbr_service = DBRService(backend_url)
        if dbr_service.health_check():
            # Create and run application
            app = MainWindow()
            app.run()


if __name__ == "__main__":
    main()
