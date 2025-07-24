"""Page 2 - Settings and configuration."""

import customtkinter as ctk


class Page2(ctk.CTkFrame):
    """Page 2 containing application settings and configuration options."""

    def __init__(self, parent):
        super().__init__(parent)

        self._setup_page()
        self._create_settings_widgets()

    def _setup_page(self) -> None:
        """Setup the page layout."""
        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Application Settings", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(20, 30))

        # Settings frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def _create_settings_widgets(self) -> None:
        """Create settings controls."""
        # Grid settings section
        grid_frame = ctk.CTkFrame(self.settings_frame)
        grid_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            grid_frame,
            text="Grid Configuration",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(10, 20))

        # Grid size controls
        size_frame = ctk.CTkFrame(grid_frame)
        size_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(size_frame, text="Grid Size:").pack(side="left", padx=10)
        self.rows_entry = ctk.CTkEntry(size_frame, placeholder_text="Rows", width=80)
        self.rows_entry.pack(side="left", padx=5)
        self.cols_entry = ctk.CTkEntry(size_frame, placeholder_text="Cols", width=80)
        self.cols_entry.pack(side="left", padx=5)

        # Cell size
        cell_frame = ctk.CTkFrame(grid_frame)
        cell_frame.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(cell_frame, text="Cell Size:").pack(side="left", padx=10)
        self.cell_size_slider = ctk.CTkSlider(
            cell_frame, from_=50, to=200, number_of_steps=15
        )
        self.cell_size_slider.pack(side="left", padx=10, fill="x", expand=True)
        self.cell_size_label = ctk.CTkLabel(cell_frame, text="100px")
        self.cell_size_label.pack(side="left", padx=10)

        # Appearance settings
        appearance_frame = ctk.CTkFrame(self.settings_frame)
        appearance_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            appearance_frame,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(10, 20))

        # Theme selection
        theme_frame = ctk.CTkFrame(appearance_frame)
        theme_frame.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(theme_frame, text="Color Theme:").pack(side="left", padx=10)
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["blue", "green", "dark-blue"],
            command=self._on_theme_change,
        )
        self.theme_menu.pack(side="left", padx=10)

        # Apply button
        ctk.CTkButton(
            self.settings_frame,
            text="Apply Settings",
            command=self._apply_settings,
            height=40,
        ).pack(pady=20)

    def _on_theme_change(self, theme: str) -> None:
        """Handle theme change."""
        ctk.set_default_color_theme(theme)
        print(f"Theme changed to: {theme}")

    def _apply_settings(self) -> None:
        """Apply all settings."""
        print("Settings applied!")

        # Get values
        settings = {
            "rows": self.rows_entry.get(),
            "cols": self.cols_entry.get(),
            "cell_size": int(self.cell_size_slider.get()),
            "theme": self.theme_menu.get(),
        }

        print(f"Applied settings: {settings}")
