import customtkinter as ctk
from tkinter import messagebox
from utils.validators import Validators
import bcrypt


class ProfilePage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        # 🔐 Admin-only access
        if self.user["role"] != "admin":
            messagebox.showerror("Access Denied", "Only admin can access settings")
            return

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Admin Settings / Profile",
            font=("Arial", 12, "bold")
        ).pack(pady=15)

        # =========================
        # PROFILE INFO SECTION
        # =========================
        profile_frame = ctk.CTkFrame(self.frame)
        profile_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(profile_frame, text=f"Name: {self.user.get('name', 'Admin')}").pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(profile_frame, text=f"Email: {self.user.get('email', '-')}", text_color="gray").pack(anchor="w", padx=10)

        # =========================
        # PHONE UPDATE SECTION
        # =========================
        phone_frame = ctk.CTkFrame(self.frame)
        phone_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(phone_frame, text="Update Phone", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        self.phone_entry = ctk.CTkEntry(phone_frame, placeholder_text="New phone number")
        self.phone_entry.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            phone_frame,
            text="Update Phone",
            fg_color="#2563EB",
            command=self.update_phone
        ).pack(pady=10)

        # =========================
        # PASSWORD SECTION
        # =========================
        pass_frame = ctk.CTkFrame(self.frame)
        pass_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(pass_frame, text="Change Password", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        self.old_password = ctk.CTkEntry(pass_frame, placeholder_text="Current password", show="*")
        self.old_password.pack(fill="x", padx=10, pady=5)

        self.new_password = ctk.CTkEntry(pass_frame, placeholder_text="New password", show="*")
        self.new_password.pack(fill="x", padx=10, pady=5)

        self.confirm_password = ctk.CTkEntry(pass_frame, placeholder_text="Confirm new password", show="*")
        self.confirm_password.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            pass_frame,
            text="Change Password",
            fg_color="#DC2626",
            command=self.update_password
        ).pack(pady=10)

    # =========================
    # PHONE UPDATE
    # =========================
    def update_phone(self):
        try:
            phone = self.phone_entry.get().strip()

            Validators.validate_phone(phone)

            self.db.execute(
                "UPDATE users SET phone=%s WHERE id=%s",
                (phone, self.user["id"])
            )

            messagebox.showinfo("Success", "Phone updated successfully")

            self.user["phone"] = phone

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # PASSWORD UPDATE
    # =========================
    def update_password(self):
        try:
            old = self.old_password.get().strip()
            new = self.new_password.get().strip()
            confirm = self.confirm_password.get().strip()

            if not old or not new or not confirm:
                raise ValueError("All password fields are required")

            if new != confirm:
                raise ValueError("Passwords do not match")

            # fetch user password hash
            user = self.db.fetch_one(
                "SELECT password FROM users WHERE id=%s",
                (self.user["id"],)
            )

            if not user:
                raise ValueError("User not found")

            # verify old password
            if not bcrypt.checkpw(old.encode(), user["password"].encode()):
                raise ValueError("Current password is incorrect")

            # hash new password
            hashed = bcrypt.hashpw(new.encode(), bcrypt.gensalt())

            self.db.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                (hashed.decode(), self.user["id"])
            )

            messagebox.showinfo("Success", "Password updated successfully")

            # clear fields
            self.old_password.delete(0, "end")
            self.new_password.delete(0, "end")
            self.confirm_password.delete(0, "end")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # SHOW
    # =========================
    def show(self):
        self.frame.pack(fill="both", expand=True)