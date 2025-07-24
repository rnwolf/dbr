"""Application menu bar."""

from tkinter import messagebox
import customtkinter as ctk
from typing import Callable, Dict


class MenuBar(ctk.CTkFrame):
    """Custom menu bar using CustomTkinter components."""

    def __init__(self, parent):
        super().__init__(parent, height=40, corner_radius=0)
        self.parent = parent

        self._create_menus()
        self._setup_layout()

    def _create_menus(self) -> None:
        """Create menu buttons and dropdowns."""
        # File menu
        self.file_menu = self._create_menu_button("File", self._get_file_menu_items())

        # Edit menu
        self.edit_menu = self._create_menu_button("Edit", self._get_edit_menu_items())

        # View menu
        self.view_menu = self._create_menu_button("View", self._get_view_menu_items())

        # Help menu
        self.help_menu = self._create_menu_button("Help", self._get_help_menu_items())

    def _create_menu_button(
        self, text: str, menu_items: Dict[str, Callable]
    ) -> ctk.CTkOptionMenu:
        """Create a menu button with dropdown options."""
        menu_button = ctk.CTkOptionMenu(
            self,
            values=list(menu_items.keys()),
            command=lambda choice: menu_items[choice](),
            width=80,
            height=30,
        )
        menu_button.set(text)
        return menu_button

    def _get_file_menu_items(self) -> Dict[str, Callable]:
        """Get file menu items."""
        return {
            "New": self._file_new,
            "Open": self._file_open,
            "Save": self._file_save,
            "Exit": self._file_exit,
        }

    def _get_edit_menu_items(self) -> Dict[str, Callable]:
        """Get edit menu items."""
        return {
            "Undo": self._edit_undo,
            "Redo": self._edit_redo,
            "Cut": self._edit_cut,
            "Copy": self._edit_copy,
            "Paste": self._edit_paste,
        }

    def _get_view_menu_items(self) -> Dict[str, Callable]:
        """Get view menu items."""
        return {
            "Zoom In": self._view_zoom_in,
            "Zoom Out": self._view_zoom_out,
            "Reset Zoom": self._view_reset_zoom,
            "Toggle Theme": self._view_toggle_theme,
        }

    def _get_help_menu_items(self) -> Dict[str, Callable]:
        """Get help menu items."""
        return {
            "Documentation": self._help_docs,
            "Keyboard Shortcuts": self._help_shortcuts,
            "About": self._help_about,
        }

    def _setup_layout(self) -> None:
        """Setup menu layout."""
        self.file_menu.pack(side="left", padx=5, pady=5)
        self.edit_menu.pack(side="left", padx=5, pady=5)
        self.view_menu.pack(side="left", padx=5, pady=5)
        self.help_menu.pack(side="right", padx=5, pady=5)

    # File menu handlers
    def _file_new(self) -> None:
        """Handle File -> New."""
        print("File -> New clicked")

    def _file_open(self) -> None:
        """Handle File -> Open."""
        print("File -> Open clicked")

    def _file_save(self) -> None:
        """Handle File -> Save."""
        print("File -> Save clicked")

    def _file_exit(self) -> None:
        """Handle File -> Exit."""
        self.parent.quit()

    # Edit menu handlers
    def _edit_undo(self) -> None:
        """Handle Edit -> Undo."""
        print("Edit -> Undo clicked")

    def _edit_redo(self) -> None:
        """Handle Edit -> Redo."""
        print("Edit -> Redo clicked")

    def _edit_cut(self) -> None:
        """Handle Edit -> Cut."""
        print("Edit -> Cut clicked")

    def _edit_copy(self) -> None:
        """Handle Edit -> Copy."""
        print("Edit -> Copy clicked")

    def _edit_paste(self) -> None:
        """Handle Edit -> Paste."""
        print("Edit -> Paste clicked")

    # View menu handlers
    def _view_zoom_in(self) -> None:
        """Handle View -> Zoom In."""
        print("View -> Zoom In clicked")

    def _view_zoom_out(self) -> None:
        """Handle View -> Zoom Out."""
        print("View -> Zoom Out clicked")

    def _view_reset_zoom(self) -> None:
        """Handle View -> Reset Zoom."""
        print("View -> Reset Zoom clicked")

    def _view_toggle_theme(self) -> None:
        """Handle View -> Toggle Theme."""
        current_mode = ctk.get_appearance_mode()
        new_mode = "light" if current_mode == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)

    # Help menu handlers
    def _help_docs(self) -> None:
        """Handle Help -> Documentation."""
        messagebox.showinfo("Documentation", "Opening documentation...")

    def _help_shortcuts(self) -> None:
        """Handle Help -> Keyboard Shortcuts."""
        shortcuts = """
Keyboard Shortcuts:
Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl+X - Cut
Ctrl+C - Copy
Ctrl+V - Paste
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)

    def _help_about(self) -> None:
        """Handle Help -> About."""
        messagebox.showinfo("About", "CustomTkinter Application v1.0")
