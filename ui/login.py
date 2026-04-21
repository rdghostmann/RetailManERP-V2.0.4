import customtkinter as ctk
from tkinter import messagebox
from services.auth_service import AuthService


class LoginWindow:
    def __init__(self, db):
        self.db = db
        self.auth = AuthService(db)

        self.root = ctk.CTk()
        self.root.title("RetailMan Login")
        self.root.geometry("400x350")

        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self.root, text="RetailMan V1.2", font=("Arial", 20)).pack(pady=20)

        self.name_entry = ctk.CTkEntry(self.root, placeholder_text="Name")
        self.name_entry.pack(pady=10)

        self.phone_entry = ctk.CTkEntry(self.root, placeholder_text="Phone")
        self.phone_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Login", command=self.handle_login).pack(pady=20)

    def handle_login(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        user = self.auth.login(name, phone)

        if not user:
            messagebox.showerror("Error", "User not found")
            return

        # First-time password setup
        if not user.get("password"):
            self.auth.set_password(user["id"], password)
            messagebox.showinfo("Success", "Password created. Login again.")
            return

        if not self.auth.verify_password(user, password):
            messagebox.showerror("Error", "Invalid password")
            return

        messagebox.showinfo("Success", f"Welcome {user['name']}")

        self.root.destroy()
        from ui.dashboard import Dashboard
        dashboard = Dashboard(self.db, user)
        dashboard.run()

    def run(self):
        self.root.mainloop()