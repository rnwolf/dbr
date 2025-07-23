"""Main application window with tabbed navigation."""

import customtkinter as ctk
from typing import Optional
from .menu_bar import MenuBar
from .tab_navigation import TabNavigation
from .pages.page1 import Page1
from .pages.page2 import Page2
from utils.config import AppConfig


class MainWindow(ctk.CTk):
    """Main application window with menu bar, tab navigation, and content area."""

    def __init__(self):
        super().__init__()

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

        # Tab navigation with pages
        self.tab_navigation = TabNavigation(self)

        # Create pages
        self.page1 = Page1(self.tab_navigation)
        self.page2 = Page2(self.tab_navigation)

        # Add pages to tab navigation
        self.tab_navigation.add_tab("Grid View", self.page1)
        self.tab_navigation.add_tab("Settings", self.page2)

        # Status bar
        self.status_bar = ctk.CTkLabel(
            self, text="Ready - Grid View Active", height=30, corner_radius=0
        )

    def _setup_layout(self) -> None:
        """Setup the layout of widgets."""
        self.menu_bar.pack(fill="x", padx=0, pady=0)
        self.tab_navigation.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.status_bar.pack(fill="x", side="bottom")

    def _bind_events(self) -> None:
        """Bind event handlers."""
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Bind tab change events
        self.tab_navigation.bind_tab_change(self._on_tab_changed)

    def _on_tab_changed(self, tab_name: str) -> None:
        """Handle tab change events."""
        self.update_status(f"Ready - {tab_name} Active")

    def _on_closing(self) -> None:
        """Handle window closing event."""
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
