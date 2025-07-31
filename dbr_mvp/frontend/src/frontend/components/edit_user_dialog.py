"""Dialog for editing an existing user."""

import customtkinter as ctk
from tkinter import messagebox


class EditUserDialog(ctk.CTkToplevel):
    """Dialog to edit an existing user."""

    def __init__(self, parent, dbr_service, user):
        super().__init__(parent)
        self.dbr_service = dbr_service
        self.parent = parent
        self.user = user

        self.title(f"Edit User: {user['username']}")
        self.geometry("450x400")
        self.grid_columnconfigure(1, weight=1)
        
        # Make the dialog resizable
        self.resizable(True, True)

        # Username
        self.username_label = ctk.CTkLabel(self, text="Username:")
        self.username_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.insert(0, user['username'])
        self.username_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # Role
        self.role_label = ctk.CTkLabel(self, text="Role:")
        self.role_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.role_combobox = ctk.CTkComboBox(
            self, values=self.dbr_service.get_available_roles()
        )
        self.role_combobox.set(user['role'])
        self.role_combobox.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        # Status
        self.status_label = ctk.CTkLabel(self, text="Status:")
        self.status_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.status_combobox = ctk.CTkComboBox(
            self, values=["Active", "Inactive", "Suspended"]
        )
        self.status_combobox.set(user['status'])
        self.status_combobox.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # Note about auto-generated fields
        self.note_label = ctk.CTkLabel(
            self, 
            text="Note: Display name and email will be auto-generated from username",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.note_label.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        # Cancel Button
        self.cancel_button = ctk.CTkButton(
            self.buttons_frame, text="Cancel", command=self.destroy
        )
        self.cancel_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Update Button
        self.update_button = ctk.CTkButton(
            self.buttons_frame, text="Update User", command=self.update_user
        )
        self.update_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    def update_user(self):
        """Callback to update the user."""
        username = self.username_entry.get().strip()
        role = self.role_combobox.get()
        status = self.status_combobox.get()

        if not username:
            messagebox.showerror(
                "Validation Error", "Username is required.", parent=self
            )
            return

        # Check if anything actually changed
        if (username == self.user['username'] and 
            role == self.user['role'] and 
            status == self.user['status']):
            messagebox.showinfo(
                "No Changes", "No changes were made to the user.", parent=self
            )
            return

        success, message = self.dbr_service.update_user(
            self.user['id'], 
            username=username if username != self.user['username'] else None,
            role=role if role != self.user['role'] else None,
            status=status if status != self.user['status'] else None
        )

        if success:
            messagebox.showinfo("Success", message, parent=self)
            self.parent.refresh_user_list()
            self.destroy()
        else:
            messagebox.showerror("Error", message, parent=self)