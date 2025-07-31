"""Page for user management tasks."""

import customtkinter as ctk
from frontend.components.create_user_dialog import CreateUserDialog
from frontend.components.edit_user_dialog import EditUserDialog


class UserManagementPage(ctk.CTkFrame):
    """User management page."""

    def __init__(self, parent, dbr_service):
        super().__init__(parent)
        self.dbr_service = dbr_service

        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self, text="User Management", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.create_user_button = ctk.CTkButton(
            self, text="Create New User", command=self.open_create_user_dialog
        )
        self.create_user_button.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.user_list_frame = ctk.CTkFrame(self)
        self.user_list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        self.refresh_user_list()

    def open_create_user_dialog(self):
        """Opens the dialog to create a new user."""
        dialog = CreateUserDialog(self, self.dbr_service)
        dialog.grab_set()

    def refresh_user_list(self):
        """Refreshes the list of users."""
        # Clear existing user widgets
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        # Create table headers
        headers = ["Username", "Role", "Status", "Actions"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                self.user_list_frame, text=header, font=ctk.CTkFont(weight="bold")
            )
            header_label.grid(row=0, column=i, padx=10, pady=5)

        # Fetch and display users
        users = self.dbr_service.get_users()
        for i, user in enumerate(users, start=1):
            username_label = ctk.CTkLabel(self.user_list_frame, text=user["username"])
            username_label.grid(row=i, column=0, padx=10, pady=5)

            role_label = ctk.CTkLabel(self.user_list_frame, text=user["role"])
            role_label.grid(row=i, column=1, padx=10, pady=5)

            status_label = ctk.CTkLabel(self.user_list_frame, text=user["status"])
            status_label.grid(row=i, column=2, padx=10, pady=5)

            actions_frame = ctk.CTkFrame(self.user_list_frame)
            actions_frame.grid(row=i, column=3, padx=10, pady=5)

            edit_button = ctk.CTkButton(
                actions_frame, text="Edit", command=lambda u=user: self.edit_user(u)
            )
            edit_button.pack(side="left", padx=5)

            remove_button = ctk.CTkButton(
                actions_frame, text="Remove", command=lambda u=user: self.remove_user(u)
            )
            remove_button.pack(side="left", padx=5)

    def edit_user(self, user):
        """Callback to edit a user."""
        print(f"Editing user: {user['username']}")
        # Create and show edit dialog
        dialog = EditUserDialog(self, self.dbr_service, user)
        dialog.grab_set()

    def remove_user(self, user):
        """Callback to remove a user."""
        from tkinter import messagebox
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to remove user '{user['username']}'?\n\nThis action cannot be undone.",
            parent=self
        )
        
        if result:
            success, message = self.dbr_service.remove_user(user['id'])
            if success:
                messagebox.showinfo("Success", message, parent=self)
                self.refresh_user_list()
            else:
                messagebox.showerror("Error", message, parent=self)
