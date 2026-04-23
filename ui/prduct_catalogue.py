#ui/product_catalogue.py
import customtkinter as ctk
from tkinter import ttk, messagebox


class ProductCataloguePage:
    def __init__(self, root, db, current_user):
        if current_user["role"] != "admin":
            messagebox.showerror("Access Denied", "Admins only")
            return

        self.root = root
        self.db = db

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_products()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Product Catalogue",
            font=("Arial", 18)
        ).pack(pady=10)

        # ===== FORM =====
        form = ctk.CTkFrame(self.frame)
        form.pack(pady=10, padx=10, fill="x")

        self.name = ctk.CTkEntry(form, placeholder_text="Product Name")
        self.brand = ctk.CTkEntry(form, placeholder_text="Brand")
        self.desc = ctk.CTkEntry(form, placeholder_text="Description")

        self.name.pack(side="left", padx=5, expand=True, fill="x")
        self.brand.pack(side="left", padx=5, expand=True, fill="x")
        self.desc.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            form,
            text="Add Product",
            command=self.create_product
        ).pack(side="left", padx=5)

        # ===== TABLE (TREEVIEW) =====
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Name", "Brand", "Description"),
            show="headings"
        )

        # Columns
        self.tree.heading("Name", text="Product Name")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Description", text="Description")

        self.tree.column("Name", anchor="w", width=200)
        self.tree.column("Brand", anchor="w", width=150)
        self.tree.column("Description", anchor="w", width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================
    # CREATE PRODUCT
    # =========================
    def create_product(self):
        try:
            name = self.name.get().strip()
            brand = self.brand.get().strip()
            desc = self.desc.get().strip()

            if not name or not brand:
                raise ValueError("Name and Brand are required")

            self.db.execute(
                """
                INSERT INTO products (name, brand, description)
                VALUES (%s, %s, %s)
                """,
                (name, brand, desc)
            )

            messagebox.showinfo("Success", "Product added")

            # Clear inputs
            self.name.delete(0, "end")
            self.brand.delete(0, "end")
            self.desc.delete(0, "end")

            self.load_products()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # LOAD PRODUCTS INTO TREE
    # =========================
    def load_products(self):
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        products = self.db.fetch_all(
            "SELECT id, name, brand, description FROM products ORDER BY name ASC"
        )

        # Insert rows
        for p in products:
            self.tree.insert(
                "",
                "end",
                iid=p["id"],  # useful for future actions (edit/delete)
                values=(
                    p["name"],
                    p["brand"],
                    p["description"]
                )
            )