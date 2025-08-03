"""Main application window with tabbed navigation."""

import customtkinter as ctk
from typing import Optional
from .menu_bar import MenuBar
from .tab_navigation import TabNavigation
from .authentication_ui import UserContextWidget
from .dbr_service import DBRService
from .pages.user_management_page import UserManagementPage
from utils.config import AppConfig


class MainWindow:
    """Main application window with menu bar, tab navigation, and content area."""

    def __init__(self, root: ctk.CTk, dbr_service: DBRService):
        self.root = root
        self.dbr_service = dbr_service

        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _setup_window(self) -> None:
        """Configure the main window."""
        self.root.title(AppConfig.WINDOW_TITLE)
        self.root.geometry(f"{AppConfig.WINDOW_SIZE[0]}x{AppConfig.WINDOW_SIZE[1]}")
        self.root.minsize(*AppConfig.MIN_WINDOW_SIZE)

        # Center window on screen
        self._center_window()

    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_widgets(self) -> None:
        """Create all widgets."""
        # Menu bar
        self.menu_bar = MenuBar(self.root)

        # User context header
        self._create_user_context_header()

        # Tab navigation with role-based pages
        self.tab_navigation = TabNavigation(self.root)

        # Create role-based navigation
        self._create_role_based_navigation()

        # Status bar
        self._create_status_bar()

    def _create_user_context_header(self) -> None:
        """Create user context display header."""
        self.header_frame = ctk.CTkFrame(self.root, height=80)

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
            height=30,
        )

        # Layout header
        self.user_context.pack(side="left", fill="y", padx=10)
        self.logout_button.pack(side="right", padx=10, pady=25)

    def _create_role_based_navigation(self) -> None:
        """Create navigation tabs based on user role and permissions."""
        user_role = self.dbr_service.get_user_role()

        # Define role-based tab configuration
        role_tabs = self._get_role_based_tabs(user_role)

        # Create placeholder pages for each tab
        self.pages = {}
        for tab_name in role_tabs:
            # For now, create simple placeholder pages
            # In future iterations, these will be proper DBR pages
            page = self._create_placeholder_page(tab_name)
            self.pages[tab_name] = page
            self.tab_navigation.add_tab(tab_name, page)

    def _get_role_based_tabs(self, user_role: str) -> list:
        """Get list of tabs based on user role and permissions."""
        if user_role == "Super Admin":
            return [
                "Organizations",
                "Users",
                "System",
                "Setup",
                "Work Items",
                "Collections",
                "Planning",
                "Buffer Boards",
                "Reports",
            ]
        elif user_role in ["Organization Admin", "Org Admin"]:
            return [
                "Setup",
                "Work Items",
                "Collections",
                "Planning",
                "Buffer Boards",
                "Reports",
            ]
        elif user_role == "Planner":
            return ["Work Items", "Collections", "Planning", "Buffer Boards", "Reports"]
        elif user_role == "Worker":
            return ["Work Items", "Buffer Boards", "Reports"]
        elif user_role == "Viewer":
            return ["Buffer Boards", "Reports"]
        else:
            # Default fallback for unknown roles
            return ["Buffer Boards", "Reports"]

    def _create_placeholder_page(self, tab_name: str) -> ctk.CTkFrame:
        """Create a page for a tab - either a real page or placeholder."""
        try:
            # Create actual pages for specific tabs
            if tab_name == "Users":
                # Create the actual UserManagementPage for Super Admin
                page = UserManagementPage(self.tab_navigation.content_frame, self.dbr_service)
                return page
            
            # Create placeholder for other tabs (for now)
            page = ctk.CTkFrame(self.tab_navigation.content_frame)
            
            # Add simple title
            title_label = ctk.CTkLabel(
                page, text=f"{tab_name} Page", font=ctk.CTkFont(size=20, weight="bold")
            )
            title_label.pack(pady=20)

            # Add simple description
            desc_label = ctk.CTkLabel(
                page,
                text=f"This is the {tab_name} page for role-based navigation.",
                font=ctk.CTkFont(size=12),
            )
            desc_label.pack(pady=10)

        except Exception as e:
            print(f"Error creating page for {tab_name}: {e}")
            # Fallback to basic frame if there's an error
            page = ctk.CTkFrame(self.tab_navigation.content_frame)

        return page

    def _get_tab_description(self, tab_name: str, user_role: str) -> str:
        """Get description for a tab based on role."""
        descriptions = {
            "Organizations": "Manage multiple organizations (Super Admin only)",
            "Users": "Global user management across organizations",
            "System": "System-wide settings and time progression controls",
            "Setup": "Organization setup: Users → CCRs → Time Units → Board Configuration",
            "Work Items": f"{'Manage' if user_role in ['Super Admin', 'Organization Admin', 'Org Admin', 'Planner'] else 'View assigned'} work items and tasks",
            "Collections": f"{'Manage' if user_role in ['Super Admin', 'Organization Admin', 'Org Admin', 'Planner'] else 'View'} projects, epics, and releases",
            "Planning": "Create and manage schedules with capacity validation",
            "Buffer Boards": f"{'Monitor and manage' if user_role != 'Viewer' else 'View'} DBR buffer zones and capability channels",
            "Reports": f"View analytics and metrics for {user_role.lower()} role",
        }
        return descriptions.get(tab_name, f"{tab_name} functionality for {user_role}")

    def _check_tab_permission(self, tab_name: str) -> bool:
        """Check if user has permission for a specific tab."""
        permission_map = {
            "Organizations": "*",  # Super Admin only
            "Users": "*",  # Super Admin only
            "System": "*",  # Super Admin only
            "Setup": "manage_organization",
            "Work Items": "manage_work_items",
            "Collections": "manage_collections",
            "Planning": "manage_schedules",
            "Buffer Boards": "view_schedules",
            "Reports": "view_analytics",
        }

        required_permission = permission_map.get(tab_name, "view_analytics")

        # Super Admin permission (*) check
        if required_permission == "*":
            return self.dbr_service.get_user_role() == "Super Admin"

        return self.dbr_service.has_permission(required_permission)

    def _create_status_bar(self) -> None:
        """Create status bar with connection info."""
        self.status_frame = ctk.CTkFrame(self.root, height=30, corner_radius=0)

        # Connection status
        connection_status = self.dbr_service.get_connection_status()
        user_role = self.dbr_service.get_user_role() or "Unknown"
        status_text = (
            f"Connected to {connection_status['backend_url']} | {user_role} - Ready"
        )

        self.status_bar = ctk.CTkLabel(
            self.status_frame, text=status_text, height=30, corner_radius=0
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
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

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
            "Logout", "Are you sure you want to logout?", parent=self.root
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

        self.root.quit()
        self.root.destroy()

    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()

    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_bar.configure(text=message)

    def get_active_page(self) -> Optional[ctk.CTkFrame]:
        """Get the currently active page."""
        return self.tab_navigation.get_active_page()
