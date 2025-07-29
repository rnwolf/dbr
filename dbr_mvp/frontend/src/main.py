#!/usr/bin/env python3
"""
Main application entry point.
"""
import customtkinter as ctk
import tkinter as tk
from frontend.main_window import MainWindow
from frontend.backend_config_dialog import BackendConfigDialog
from frontend.authentication_ui import AuthenticationManager
from utils.config import AppConfig


def main():
    """Initialize and run the application."""
    # Set appearance mode and color theme
    ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
    ctk.set_default_color_theme(AppConfig.COLOR_THEME)

    # Create and hide the root window to prevent "tk" window
    root = tk.Tk()
    root.title("DBR Buffer Management System")
    root.withdraw()  # Hide the root window
    
    try:
        # Get backend URL from user first
        config_dialog = BackendConfigDialog(None)
        backend_url = config_dialog.get_url()

        if backend_url:
            # Run authentication workflow
            auth_manager = AuthenticationManager(backend_url)
            authenticated_service = auth_manager.authenticate()
            
            if authenticated_service:
                # Don't destroy root - let MainWindow handle it
                # The MainWindow will create its own window and the root will be unused
                
                # Create and run the main application
                app = MainWindow(authenticated_service)
                app.run()
                
                # Clean up the hidden root after main app closes
                try:
                    if root.winfo_exists():
                        root.quit()
                        root.destroy()
                except:
                    pass
            else:
                print("Authentication cancelled or failed. Exiting application.")
                root.quit()
                root.destroy()
        else:
            print("Backend configuration cancelled. Exiting application.")
            root.quit()
            root.destroy()
    except Exception as e:
        print(f"Application error: {e}")
        try:
            if root.winfo_exists():
                root.quit()
                root.destroy()
        except:
            pass


if __name__ == "__main__":
    main()
