"""Main application window with tabbed navigation."""

import customtkinter as ctk
from typing import Optional
from .menu_bar import MenuBar
from .tab_navigation import TabNavigation
from .pages.page1 import Page1
from .pages.page2 import Page2
from .authentication_ui import UserContextWidget
from .dbr_service import DBRService
from utils.config import AppConfig


class MainWindow(ctk.CTk):
    """Main application window with menu bar, tab navigation, and content area."""

    def __init__(self, dbr_service: DBRService):
        super().__init__()
        
        self.dbr_service = dbr_service

        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.title(AppConfig.WINDOW_TITLE)
        self.geometry(f"{AppConfig.WINDOW_SIZE[0]}x{AppConfig.WINDOW_SIZE[1]}")
        self.minsize(*AppConfig.MIN_WINDOW_SIZE)

        # Center window on screen
        self._center_window()

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Menu bar
        self.menu_bar = MenuBar(self)

        # User context header
        self._create_user_context_header()

        # Tab navigation with pages
        self.tab_navigation = TabNavigation(self)

        # Create pages
        self.page1 = Page1(self.tab_navigation)
        self.page2 = Page2(self.tab_navigation)

        # Add pages to tab navigation
        self.tab_navigation.add_tab("Grid View", self.page1)
        self.tab_navigation.add_tab("Settings", self.page2)

        # Status bar
        self._create_status_bar()

    def _create_user_context_header(self) -> None:
        """Create user context display header."""
        self.header_frame = ctk.CTkFrame(self, height=80)
        
        # User context widget
        user_info = self.dbr_service.get_user_info() or {}
        user_role = self.dbr_service.get_user_role()
        org_info = self.dbr_service.get_current_organization() or {}
        org_name = org_info.get("name", "No Organization")
        
        self.user_context = UserContextWidget(
            self.header_frame, user_info, user_role, org_name
        )
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self.header_frame,
            text="Logout",
            command=self._on_logout,
            width=80,
            height=30
        )
        
        # Layout header
        self.user_context.pack(side="left", fill="y", padx=10)
        self.logout_button.pack(side="right", padx=10, pady=25)

    def _create_status_bar(self) -> None:
        """Create status bar with connection info."""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        
        # Connection status
        connection_status = self.dbr_service.get_connection_status()
        status_text = f"Connected to {connection_status['backend_url']} | Ready - Grid View Active"
        
        self.status_bar = ctk.CTkLabel(
            self.status_frame, 
            text=status_text, 
            height=30, 
            corner_radius=0
        )
        self.status_bar.pack(fill="x", padx=10)

    def _setup_layout(self) -> None:
        """Setup the layout of widgets."""
        self.menu_bar.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.tab_navigation.pack(fill="both", expand=True, padx=10, pady=(5, 5))
        self.status_frame.pack(fill="x", side="bottom")

    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Bind tab change events
        self.tab_navigation.bind_tab_change(self._on_tab_changed)

    def _on_tab_changed(self, tab_name: str) -> None:
        """Handle tab change events."""
        connection_status = self.dbr_service.get_connection_status()
        status_text = f"Connected to {connection_status['backend_url']} | Ready - {tab_name} Active"
        self.update_status(status_text)

    def _on_logout(self) -> None:
        """Handle logout button click."""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Logout", 
            "Are you sure you want to logout?",
            parent=self
        )
        
        if result:
            # Logout from service
            self.dbr_service.logout()
            
            # Close main window
            self._on_closing()

    def _on_closing(self) -> None:
        """Handle window closing event."""
        # Ensure clean logout
        if self.dbr_service.is_authenticated():
            self.dbr_service.logout()
        
        self.quit()
        self.destroy()

    def run(self) -> None:
        """Start the application main loop."""
        self.mainloop()

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.configure(text=message)

    def get_active_page(self) -> Optional[ctk.CTkFrame]:
        """Get the currently active page."""
        return self.tab_navigation.get_active_page()
