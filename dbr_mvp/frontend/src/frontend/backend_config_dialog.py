"""Dialog for configuring the backend URL."""

import customtkinter as ctk


class BackendConfigDialog(ctk.CTkToplevel):
    """A dialog to get the backend URL from the user."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("DBR Backend Configuration")
        self.geometry("400x200")
        self.url = None

        # If no parent, set this as the main window temporarily
        if parent is None:
            self.wm_title("DBR Backend Configuration")

        self.label = ctk.CTkLabel(self, text="Enter Backend URL:")
        self.label.pack(pady=20)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=10)
        self.entry.insert(0, "http://127.0.0.1:8000")

        self.button = ctk.CTkButton(self, text="Connect", command=self.connect)
        self.button.pack(pady=20)

        self.transient(parent)
        self.grab_set()
        self.wait_window()

    def connect(self):
        """Sets the URL and closes the dialog."""
        self.url = self.entry.get()
        self.destroy()

    def get_url(self):
        """Returns the entered URL."""
        return self.url
