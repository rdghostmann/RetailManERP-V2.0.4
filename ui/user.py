import customtkinter as ctk
from tkinter import ttk, messagebox


class UserPage:
    def __init__(self, root, db, current_user):
        if current_user["role"] != "admin":
            messagebox.showerror("Access Denied", "Admins only")
            return

        self.root = root
        self.db = db

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_users()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="User Management",
            font=("Arial", 18)
        ).pack(pady=10)

        # ===== FORM =====
        form = ctk.CTkFrame(self.frame)
        form.pack(pady=10, padx=10, fill="x")

        self.name = ctk.CTkEntry(form, placeholder_text="Name")
        self.phone = ctk.CTkEntry(form, placeholder_text="Phone")

        self.role = ctk.CTkComboBox(form, values=["admin", "staff"])
        self.role.set("staff")  # default

        self.name.pack(side="left", padx=5, expand=True, fill="x")
        self.phone.pack(side="left", padx=5, expand=True, fill="x")
        self.role.pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Create User",
            command=self.create_user
        ).pack(side="left", padx=5)

        # ===== TABLE =====
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Name", "Phone", "Role"),
            show="headings"
        )

        # Columns
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Role", text="Role")

        self.tree.column("Name", anchor="w", width=200)
        self.tree.column("Phone", anchor="center", width=150)
        self.tree.column("Role", anchor="center", width=100)

        # Scrollbar
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

            if not name or not phone:
                raise ValueError("Name and Phone are required")

            self.db.execute(
                """
                INSERT INTO users (name, phone, role)
                VALUES (%s, %s, %s)
                """,
                (name, phone, role)
            )

            messagebox.showinfo("Success", "User created")

            # Clear inputs
            self.name.delete(0, "end")
            self.phone.delete(0, "end")
            self.role.set("staff")

            self.load_users()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # LOAD USERS INTO TABLE
    # =========================
    def load_users(self):
        # Clear table
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
                iid=u["id"],  # enables future row actions
                values=(
                    u["name"],
                    u["phone"],
                    u["role"]
                )
            )