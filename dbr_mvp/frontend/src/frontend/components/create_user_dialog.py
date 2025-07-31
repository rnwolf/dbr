"""Dialog for creating a new user."""

import customtkinter as ctk
from tkinter import messagebox


class CreateUserDialog(ctk.CTkToplevel):
    """Dialog to create a new user."""

    def __init__(self, parent, dbr_service):
        super().__init__(parent)
        self.dbr_service = dbr_service
        self.parent = parent

        self.title("Create New User")
        self.geometry("400x300")
        self.grid_columnconfigure(1, weight=1)

        # Username
        self.username_label = ctk.CTkLabel(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # Password
        self.password_label = ctk.CTkLabel(self, text="Temporary Password:")
        self.password_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Role
        self.role_label = ctk.CTkLabel(self, text="Role:")
        self.role_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.role_combobox = ctk.CTkComboBox(
            self, values=self.dbr_service.get_available_roles()
        )
        self.role_combobox.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # Create Button
        self.create_button = ctk.CTkButton(
            self, text="Create User", command=self.create_user
        )
        self.create_button.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def create_user(self):
        """Callback to create the user."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_combobox.get()

        if not username or not password:
            messagebox.showerror(
                "Validation Error", "Username and password are required."
            )
            return

        success, message = self.dbr_service.create_user(username, password, role)

        if success:
            messagebox.showinfo("Success", message)
            self.parent.refresh_user_list()
            self.destroy()
        else:
            messagebox.showerror("Error", message)
