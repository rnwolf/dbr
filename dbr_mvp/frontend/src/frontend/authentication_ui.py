"""Authentication UI components for DBR application."""

import customtkinter as ctk
from typing import Optional, Dict, Any, List
import tkinter as tk
from tkinter import messagebox
from .dbr_service import DBRService


class LoginDialog(ctk.CTkToplevel):
    """Login dialog for user authentication."""

    def __init__(self, parent, backend_url: str):
        super().__init__(parent)
        
        self.backend_url = backend_url
        self.dbr_service = DBRService(backend_url)
        self.result = None
        self.user_info = None
        
        self._setup_dialog()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center on parent or screen
        self._center_dialog()
        
        # Focus on username field
        self.username_entry.focus()

    def _setup_dialog(self) -> None:
        """Configure the dialog window."""
        self.title("DBR Login - Buffer Management System")
        self.geometry("450x600")
        self.resizable(False, False)

    def _center_dialog(self) -> None:
        """Center the dialog on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all dialog widgets."""
        # Header
        self.header_label = ctk.CTkLabel(
            self, 
            text="DBR Buffer Management System",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Please log in to continue",
            font=ctk.CTkFont(size=14)
        )
        
        # Connection status
        self.connection_frame = ctk.CTkFrame(self)
        self.connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="Checking backend connection...",
            font=ctk.CTkFont(size=12)
        )
        
        # Login form
        self.form_frame = ctk.CTkFrame(self)
        
        self.username_label = ctk.CTkLabel(self.form_frame, text="Username:")
        self.username_entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Enter username",
            width=300
        )
        
        self.password_label = ctk.CTkLabel(self.form_frame, text="Password:")
        self.password_entry = ctk.CTkEntry(
            self.form_frame, 
            placeholder_text="Enter password",
            show="*",
            width=300
        )
        
        # Buttons
        self.button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.login_button = ctk.CTkButton(
            self.button_frame,
            text="Login",
            command=self._on_login_click,
            width=140
        )
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self._on_cancel_click,
            width=140,
            fg_color="gray"
        )
        
        # Test users help
        self.help_frame = ctk.CTkFrame(self)
        self.help_label = ctk.CTkLabel(
            self.help_frame,
            text="Test User Credentials:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        
        # Create test user buttons
        self.test_users_frame = ctk.CTkFrame(self.help_frame, fg_color="transparent")
        self._create_test_user_buttons()
        
        # Status/error message
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="red"
        )
        
        # Check backend connection
        self._check_backend_connection()

    def _create_test_user_buttons(self) -> None:
        """Create quick login buttons for test users."""
        test_users = self.get_test_user_hints()
        
        for i, user in enumerate(test_users):
            button = ctk.CTkButton(
                self.test_users_frame,
                text=f"{user['username']} ({user['role']})",
                command=lambda u=user: self._quick_login(u['username'], u['password']),
                width=200,
                height=30,
                font=ctk.CTkFont(size=11)
            )
            button.grid(row=i, column=0, padx=5, pady=2, sticky="w")

    def _setup_layout(self) -> None:
        """Setup the layout of widgets."""
        # Header
        self.header_label.pack(pady=(20, 5))
        self.subtitle_label.pack(pady=(0, 15))
        
        # Connection status
        self.connection_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.connection_label.pack(pady=10)
        
        # Form
        self.form_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.username_label.pack(anchor="w", padx=20, pady=(15, 5))
        self.username_entry.pack(padx=20, pady=(0, 10))
        
        self.password_label.pack(anchor="w", padx=20, pady=(0, 5))
        self.password_entry.pack(padx=20, pady=(0, 15))
        
        self.button_frame.pack(pady=(0, 15))
        self.login_button.pack(side="left", padx=(0, 10))
        self.cancel_button.pack(side="left")
        
        # Test users help
        self.help_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.help_label.pack(pady=(10, 5))
        self.test_users_frame.pack(pady=(0, 10))
        
        # Status
        self.status_label.pack(pady=(0, 20))

    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.password_entry.bind("<Return>", lambda e: self._on_login_click())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

    def _check_backend_connection(self) -> None:
        """Check backend connection and update status."""
        try:
            if self.dbr_service.health_check():
                self.connection_label.configure(
                    text=f"✅ Connected to {self.backend_url}",
                    text_color="green"
                )
            else:
                self.connection_label.configure(
                    text=f"❌ Cannot connect to {self.backend_url}",
                    text_color="red"
                )
        except Exception as e:
            self.connection_label.configure(
                text=f"❌ Connection error: {str(e)}",
                text_color="red"
            )

    def _on_login_click(self) -> None:
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self._show_status("Please enter both username and password", "red")
            return
        
        self._attempt_login(username, password)

    def _quick_login(self, username: str, password: str) -> None:
        """Handle quick login with test credentials."""
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)
        self._attempt_login(username, password)

    def _attempt_login(self, username: str, password: str) -> bool:
        """Attempt to login with provided credentials."""
        self._show_status("Logging in...", "blue")
        self.login_button.configure(state="disabled")
        
        try:
            # Update UI to show progress
            self.update()
            
            success = self.dbr_service.login(username, password)
            
            if success:
                # Store user information
                self.user_info = self.dbr_service.get_user_info()
                self.result = self.dbr_service
                
                self._show_status("Login successful!", "green")
                
                # Close dialog after short delay
                self.after(500, self._close_success)
                return True
            else:
                self._show_status("Invalid username or password", "red")
                return False
                
        except Exception as e:
            self._show_status(f"Login error: {str(e)}", "red")
            return False
        finally:
            self.login_button.configure(state="normal")

    def _close_success(self) -> None:
        """Close dialog on successful login."""
        self.grab_release()
        self.destroy()

    def _on_cancel_click(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.grab_release()
        self.destroy()

    def _show_status(self, message: str, color: str = "black") -> None:
        """Show status message."""
        self.status_label.configure(text=message, text_color=color)

    def get_test_user_hints(self) -> List[Dict[str, str]]:
        """Get test user credential hints based on actual database users."""
        return [
            {"username": "admin", "password": "admin123", "role": "Organization Admin"},
            {"username": "orgadmin", "password": "orgadmin123", "role": "Organization Admin"},
            {"username": "planner", "password": "planner123", "role": "Planner"},
            {"username": "testuser", "password": "testpassword123", "role": "Planner"},
            {"username": "viewer2", "password": "viewer123", "role": "Viewer"},
        ]


class UserContextWidget(ctk.CTkFrame):
    """Widget to display current user context."""

    def __init__(self, parent, user_info: Dict[str, Any], user_role: str, organization_name: str):
        super().__init__(parent)
        
        self.user_info = user_info
        self.user_role = user_role
        self.organization_name = organization_name
        
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """Create context display widgets."""
        # User info
        display_name = self.user_info.get("display_name", self.user_info.get("username", "Unknown"))
        
        self.user_label = ctk.CTkLabel(
            self,
            text=f"👤 {display_name}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        
        self.role_label = ctk.CTkLabel(
            self,
            text=f"🔑 {self.user_role or 'No Role'}",
            font=ctk.CTkFont(size=11)
        )
        
        self.org_label = ctk.CTkLabel(
            self,
            text=f"🏢 {self.organization_name}",
            font=ctk.CTkFont(size=11)
        )

    def _setup_layout(self) -> None:
        """Setup widget layout."""
        self.user_label.pack(anchor="w", padx=10, pady=(5, 2))
        self.role_label.pack(anchor="w", padx=10, pady=2)
        self.org_label.pack(anchor="w", padx=10, pady=(2, 5))

    def get_display_text(self) -> str:
        """Get formatted display text for testing."""
        display_name = self.user_info.get("display_name", self.user_info.get("username", "Unknown"))
        return f"{display_name} - {self.user_role} - {self.organization_name}"


class AuthenticationManager:
    """Manages the complete authentication workflow."""

    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    def authenticate(self) -> Optional[DBRService]:
        """Run authentication workflow and return authenticated service."""
        try:
            # Create and show login dialog
            dialog = LoginDialog(None, self.backend_url)
            dialog.wait_window()  # Wait for dialog to close
            
            # Return authenticated service if login was successful
            if dialog.result:
                return dialog.result
            else:
                return None
                
        except Exception as e:
            messagebox.showerror("Authentication Error", f"Authentication failed: {str(e)}")
            return None

    def show_login_dialog(self, parent=None) -> Optional[DBRService]:
        """Show login dialog and return result."""
        dialog = LoginDialog(parent, self.backend_url)
        dialog.wait_window()
        return dialog.result