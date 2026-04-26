# ui/product_catalogue.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from utils.excel_exporter import ExcelExporter
from tkinter import messagebox

class ProductCataloguePage:
    def __init__(self, root, db, current_user):
        self.root = root
        self.db = db
        self.user = current_user
        self.is_admin = self.user["role"] == "admin"

        self.all_products = []
        self.filtered_products = []
        self.sort_column = None
        self.sort_reverse = False

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
            font=("Arial", 12)
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

        # ✅ Admin controls
        if self.is_admin:
            ctk.CTkButton(
                form,
                text="Update Selected",
                fg_color="#2563EB",
                command=self.update_product
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                form,
                text="Delete Selected",
                fg_color="#DC2626",
                command=self.delete_product
            ).pack(side="left", padx=5)

        # ===== EXPORT =====
        ctk.CTkButton(
            self.frame,
            text="Export to Excel",
            command=self.export_to_excel,
            fg_color="#15803D"
        ).pack(pady=5)

        # ===== SEARCH =====
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search products..."
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_products)

            # ===== TABLE =====
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # =========================
        # 🎨 TREEVIEW STYLE (UPDATED)
        # =========================
        style = ttk.Style()

        style.theme_use("default")

        # Body
        style.configure(
            "Treeview",
            background="#1E1E1E",
            foreground="white",
            fieldbackground="#1E1E1E",
            rowheight=30,
            bordercolor="#404040",
            borderwidth=1,
            relief="solid"
        )

        # Header
        style.configure(
            "Treeview.Heading",
            background="#00509D",
            foreground="white",
            relief="flat",
            borderwidth=1
        )

        # Selected row
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")]
        )

        # =========================
        # TREEVIEW
        # =========================
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Name", "Brand", "Description"),
            show="headings"
        )

        # Center align ALL columns
        for col in ("Name", "Brand", "Description"):
            self.tree.heading(
                col,
                text=col,
                anchor="center",
                command=lambda c=col: self.sort_by_column(c)
            )

            self.tree.column(
                col,
                anchor="center",  # ✅ center text
                width=200
            )

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # =========================
    # CREATE
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
            self.clear_form()
            self.load_products()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # UPDATE
    # =========================
    def update_product(self):
        if not self.is_admin:
            messagebox.showerror("Access Denied", "Admins only")
            return

        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a product to update")
            return

        try:
            name = self.name.get().strip()
            brand = self.brand.get().strip()
            desc = self.desc.get().strip()

            self.db.execute(
                """
                UPDATE products
                SET name=%s, brand=%s, description=%s
                WHERE id=%s
                """,
                (name, brand, desc, int(selected))
            )

            messagebox.showinfo("Success", "Product updated")
            self.clear_form()
            self.load_products()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # DELETE
    # =========================
    def delete_product(self):
        if not self.is_admin:
            messagebox.showerror("Access Denied", "Admins only")
            return

        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Select", "Select a product to delete")
            return

        confirm = messagebox.askyesno("Confirm", "Delete this product?")
        if not confirm:
            return

        try:
            self.db.execute(
                "DELETE FROM products WHERE id=%s",
                (int(selected),)
            )

            messagebox.showinfo("Deleted", "Product removed")
            self.clear_form()
            self.load_products()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # SELECT
    # =========================
    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected, "values")

        self.name.delete(0, "end")
        self.brand.delete(0, "end")
        self.desc.delete(0, "end")

        self.name.insert(0, values[0])
        self.brand.insert(0, values[1])
        self.desc.insert(0, values[2])

    def clear_form(self):
        self.name.delete(0, "end")
        self.brand.delete(0, "end")
        self.desc.delete(0, "end")

    # =========================
    # LOAD
    # =========================
    def load_products(self):
        self.all_products = self.db.fetch_all(
            "SELECT id, name, brand, description FROM products ORDER BY name ASC"
        ) or []   # ✅ FIX HERE

        self.filtered_products = self.all_products.copy()
        self.display_products(self.filtered_products)

    def display_products(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for p in data:
            self.tree.insert(
                "",
                "end",
                iid=p["id"],
                values=(p["name"], p["brand"], p["description"])
            )

    # =========================
    # FILTER
    # =========================
    def filter_products(self, event=None):
        keyword = self.search_var.get().lower()

        self.filtered_products = [
            p for p in self.all_products
            if keyword in p["name"].lower()
            or keyword in p["brand"].lower()
            or keyword in (p["description"] or "").lower()
        ]

        self.display_products(self.filtered_products)

    # =========================
    # SORT
    # =========================
    def sort_by_column(self, col):
        mapping = {
            "Name": "name",
            "Brand": "brand",
            "Description": "description"
        }

        db_col = mapping[col]

        if self.sort_column == db_col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = db_col

        self.filtered_products = sorted(
            self.filtered_products,
            key=lambda x: (x[db_col] or "").lower(),
            reverse=self.sort_reverse
        )

        self.display_products(self.filtered_products)

    # =========================
    # EXPORT
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No sales data available")
                return

            df = pd.DataFrame([
                {
                    "Product": row.get("product_name"),
                    "IMEI": row.get("imei"),
                    "Colour": row.get("colour"),
                    "Quantity": row.get("quantity"),
                    "Sold By": row.get("sold_by"),
                    "Date": self.format_date(row.get("created_at"))
                }
                for row in self.all_data
            ])

            exporter = ExcelExporter("RetailMan_Reports.xlsx")
            exporter.export_sheet("ProductCatalog", df)

            messagebox.showinfo(
                "Export Successful",
                "ProductCatalog sheet updated in RetailMan_Reports.xlsx"
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e))