from tkinter import ttk, messagebox
import customtkinter as ctk

class UserManagementPage(ctk.CTkFrame):
    def __init__(self, parent, dbr_service):
        super().__init__(parent)
        self.dbr_service = dbr_service

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="User Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.add_user_button = ctk.CTkButton(self, text="Add User", command=self.open_add_user_dialog)
        self.add_user_button.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        self.user_list_frame = ctk.CTkFrame(self)
        self.user_list_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.load_users()

    def load_users(self):
        # Clear existing user list
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()

        users = self.dbr_service.get_users()

        # Create table headers
        headers = ["Username", "Email", "Role", "Status"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(self.user_list_frame, text=header, font=ctk.CTkFont(weight="bold"))
            header_label.grid(row=0, column=i, padx=10, pady=10)

        # Populate user data
        for i, user in enumerate(users):
            ctk.CTkLabel(self.user_list_frame, text=user.get("username")).grid(row=i + 1, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.user_list_frame, text=user.get("email")).grid(row=i + 1, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.user_list_frame, text=user.get("role")).grid(row=i + 1, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.user_list_frame, text=user.get("status")).grid(row=i + 1, column=3, padx=10, pady=5)

    def open_add_user_dialog(self):
        dialog = CreateUserDialog(self, self.dbr_service)
        self.wait_window(dialog)
        self.load_users()

    def refresh_user_list(self):
        self.load_users()

class CreateUserDialog(ctk.CTkToplevel):
    def __init__(self, parent, dbr_service):
        super().__init__(parent)
        self.dbr_service = dbr_service
        self.title("Create New User")
        self.geometry("400x300")

        self.username_label = ctk.CTkLabel(self, text="Username")
        self.username_label.pack(pady=(20, 5))
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.pack(pady=5, padx=20, fill="x")

        self.password_label = ctk.CTkLabel(self, text="Temporary Password")
        self.password_label.pack(pady=(10, 5))
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=5, padx=20, fill="x")

        self.role_label = ctk.CTkLabel(self, text="Role")
        self.role_label.pack(pady=(10, 5))
        self.role_combobox = ctk.CTkComboBox(self, values=["Planner", "Worker", "Viewer"])
        self.role_combobox.pack(pady=5, padx=20, fill="x")

        self.create_button = ctk.CTkButton(self, text="Create User", command=self.create_user)
        self.create_button.pack(pady=20)

    def create_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_combobox.get()

        if not username or not password:
            messagebox.showerror("Validation Error", "Username and password are required.")
            return

        success, message = self.dbr_service.create_user(username, password, role)

        if success:
            messagebox.showinfo("Success", message)
            self.destroy()
        else:
            messagebox.showerror("Error", message)