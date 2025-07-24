#!/usr/bin/env python3
"""
Main application entry point.
"""
import customtkinter as ctk
from frontend.main_window import MainWindow
from utils.config import AppConfig


def main():
    """Initialize and run the application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
    ctk.set_default_color_theme(AppConfig.COLOR_THEME)

    # Create and run application
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
