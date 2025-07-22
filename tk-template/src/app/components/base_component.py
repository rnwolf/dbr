"""Base class for CustomTkinter components."""

import customtkinter as ctk


class BaseComponent(ctk.CTkFrame):
    """Base class for CustomTkinter components to provide common functionality."""

    def __init__(self, parent: ctk.CTk, **kwargs) -> None:
        """Initializes the BaseComponent."""
        super().__init__(parent, **kwargs)