# ui/login.py
import customtkinter as ctk
from tkinter import messagebox
from services.auth_service import AuthService
from utils.session_manager import SessionManager  # ✅ ADD THIS

class LoginWindow:
    def __init__(self, db):
        self.db = db
        self.auth = AuthService(db)

        self.root = ctk.CTk()
        self.root.title("RetailMan ERP Login")
        self.root.geometry("400x350")

        self.build_ui()

 # Phone validation function
    def validate_phone_input(self, value):
        return value.isdigit() and len(value) <= 11 or value == ""
        
    def build_ui(self):
        ctk.CTkLabel(self.root, text="RetailMan V1.2", font=("Arial", 12)).pack(pady=20)

        self.name_entry = ctk.CTkEntry(self.root, placeholder_text="Name")
        self.name_entry.pack(pady=10)

        # Register validation
        vcmd = (self.root.register(self.validate_phone_input), "%P")

        self.phone_entry = ctk.CTkEntry(
            self.root,
            placeholder_text="Phone (11 digits)",
            validate="key",
            validatecommand=vcmd
        )
        self.phone_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.root, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.root, text="Login", command=self.handle_login).pack(pady=20)

    def handle_login(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        try:
            result = self.auth.login(name, phone, password)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        status = result.get("status")
        user = result.get("user")

        # First-time password setup
        if status == "SET_PASSWORD":
            self.auth.set_password(user["id"], password)
            messagebox.showinfo("Success", "Password created. Login again.")
            self.name_entry.delete(0, 'end')
            self.phone_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            return

        # ✅ SUCCESS LOGIN → CREATE SESSION
        if status == "SUCCESS":
            SessionManager.login(user)  # 🔥 KEY LINE

            messagebox.showinfo("Success", f"Welcome {user['name']}")

            self.root.destroy()

            from ui.dashboard import Dashboard
            dashboard = Dashboard(self.db, user)  # (optional: later remove user param)
            dashboard.run()

        else:
            messagebox.showerror("Error", "Login failed")

    def run(self):
        self.root.mainloop()