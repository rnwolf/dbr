"""Tab navigation component for switching between pages."""

import customtkinter as ctk
from typing import Dict, Callable, Optional, Any


class TabNavigation(ctk.CTkFrame):
    """Tab navigation component with dynamic page switching."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Tab management
        self._tabs: Dict[str, ctk.CTkFrame] = {}
        self._tab_buttons: Dict[str, ctk.CTkButton] = {}
        self._active_tab: Optional[str] = None
        self._tab_change_callback: Optional[Callable[[str], None]] = None

        self._setup_navigation()

    def _setup_navigation(self) -> None:
        """Setup the tab navigation structure."""
        # Tab button frame (top)
        self.tab_button_frame = ctk.CTkFrame(self, height=50)
        self.tab_button_frame.pack(fill="x", padx=0, pady=(0, 5))
        self.tab_button_frame.pack_propagate(False)

        # Content frame (main area)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True)

    def add_tab(self, tab_name: str, tab_content: ctk.CTkFrame) -> None:
        """Add a new tab with content."""
        # Create tab button
        tab_button = ctk.CTkButton(
            self.tab_button_frame,
            text=tab_name,
            command=lambda: self._switch_tab(tab_name),
            width=120,
            height=35,
        )

        # Store references
        self._tab_buttons[tab_name] = tab_button
        self._tabs[tab_name] = tab_content

        # Pack the button
        tab_button.pack(side="left", padx=5, pady=7)

        # Place content in content frame (initially hidden)
        tab_content.place(in_=self.content_frame, x=0, y=0, relwidth=1, relheight=1)
        tab_content.place_forget()

        # If this is the first tab, make it active
        if self._active_tab is None:
            self._switch_tab(tab_name)

    def _switch_tab(self, tab_name: str) -> None:
        """Switch to the specified tab."""
        if tab_name not in self._tabs:
            return

        # Hide current tab content
        if self._active_tab and self._active_tab in self._tabs:
            self._tabs[self._active_tab].place_forget()
            # Reset previous button appearance
            self._tab_buttons[self._active_tab].configure(fg_color=("gray75", "gray25"))

        # Show new tab content
        self._tabs[tab_name].place(
            in_=self.content_frame, x=0, y=0, relwidth=1, relheight=1
        )

        # Update button appearance
        self._tab_buttons[tab_name].configure(fg_color=("gray85", "gray15"))

        # Update active tab
        self._active_tab = tab_name

        # Call callback if set
        if self._tab_change_callback:
            self._tab_change_callback(tab_name)

    def bind_tab_change(self, callback: Callable[[str], None]) -> None:
        """Bind a callback for tab change events."""
        self._tab_change_callback = callback

    def get_active_tab_name(self) -> Optional[str]:
        """Get the name of the currently active tab."""
        return self._active_tab

    def get_active_page(self) -> Optional[ctk.CTkFrame]:
        """Get the currently active page content."""
        if self._active_tab:
            return self._tabs.get(self._active_tab)
        return None

    def remove_tab(self, tab_name: str) -> None:
        """Remove a tab and its content."""
        if tab_name not in self._tabs:
            return

        # Remove button
        if tab_name in self._tab_buttons:
            self._tab_buttons[tab_name].destroy()
            del self._tab_buttons[tab_name]

        # Remove content
        self._tabs[tab_name].destroy()
        del self._tabs[tab_name]

        # If this was the active tab, switch to another
        if self._active_tab == tab_name:
            self._active_tab = None
            if self._tabs:
                self._switch_tab(list(self._tabs.keys())[0])
