# ui/users.py
import customtkinter as ctk
from tkinter import ttk, messagebox

class UserPage:
    def __init__(self, root, db, current_user):
        if current_user["role"] != "admin":
            messagebox.showerror("Access Denied", "Admins only")
            return

        self.root = root
        self.db = db
        self.current_user = current_user  # ✅ store current user

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_users()


        # =========================
        # INPUT VALIDATION
        # =========================
    def validate_phone_input(self, value):
        """
        Allow only digits and max length 11
        """
        if value == "":
            return True

        if not value.isdigit():
            return False

        if len(value) > 11:
            return False

        return True

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="User Management",
            font=("Arial", 16)
        ).pack(pady=10)

        # ===== FORM =====
        form = ctk.CTkFrame(self.frame)
        form.pack(pady=10, padx=10, fill="x")

        self.name = ctk.CTkEntry(form, placeholder_text="Name")
        
        # Register validation
        vcmd = (self.frame.register(self.validate_phone_input), "%P")

        self.phone = ctk.CTkEntry(
            form,
            placeholder_text="Phone",
            validate="key",
            validatecommand=vcmd
        )

        self.role = ctk.CTkComboBox(form, values=["admin", "staff"])
        self.role.set("staff")

        self.name.pack(side="left", padx=5, expand=True, fill="x")
        self.phone.pack(side="left", padx=5, expand=True, fill="x")
        self.role.pack(side="left", padx=5)

        # ➕ Create User Button
        ctk.CTkButton(
            form,
            text="Create User",
            command=self.create_user
        ).pack(side="left", padx=5)

        # ❌ Delete Button
        ctk.CTkButton(
            form,
            text="Delete Selected",
            fg_color="red",
            hover_color="#B91C1C",
            command=self.delete_user
        ).pack(side="left", padx=5)

        # ===== TABLE =====
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Name", "Phone", "Role"),
            show="headings"
        )

        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Role", text="Role")

        self.tree.column("Name", anchor="w", width=200)
        self.tree.column("Phone", anchor="center", width=150)
        self.tree.column("Role", anchor="center", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================
    # CREATE USER
    # =========================
    def create_user(self):
        try:
            name = self.name.get().strip()
            phone = self.phone.get().strip()
            role = self.role.get()

            # =========================
            # VALIDATION
            # =========================
            if not name:
                raise ValueError("Name is required")

            if not phone:
                raise ValueError("Phone is required")

            if not phone.isdigit():
                raise ValueError("Phone must contain only numbers")

            if len(phone) != 11:
                raise ValueError("Phone must be exactly 11 digits")

            # =========================
            # INSERT
            # =========================
            self.db.execute(
                """
                INSERT INTO users (name, phone, role)
                VALUES (%s, %s, %s)
                """,
                (name, phone, role)
            )

            messagebox.showinfo("Success", "User created")

            # Reset form
            self.name.delete(0, "end")
            self.phone.delete(0, "end")
            self.role.set("staff")

            # UX: focus back
            self.name.focus()

            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # DELETE USER
    # =========================
    def delete_user(self):
        try:
            selected = self.tree.selection()

            if not selected:
                raise ValueError("Please select a user to delete")

            user_id = selected[0]

            # 🚫 Prevent deleting yourself
            if str(self.current_user["id"]) == str(user_id):
                raise ValueError("You cannot delete your own account")

            confirm = messagebox.askyesno(
                "Confirm Delete",
                "Are you sure you want to delete this user?"
            )

            if not confirm:
                return

            self.db.execute(
                "DELETE FROM users WHERE id=%s",
                (user_id,)
            )

            messagebox.showinfo("Success", "User deleted successfully")

            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # LOAD USERS
    # =========================
    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        users = self.db.fetch_all(
            """
            SELECT id, name, phone, role
            FROM users
            ORDER BY name ASC
            """
        )

        for u in users:
            self.tree.insert(
                "",
                "end",
                iid=u["id"],
                values=(
                    u["name"],
                    u["phone"],
                    u["role"]
                )
            )