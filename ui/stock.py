# ui/stock.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from services.stock_service import StockService
from services.product_service import ProductService
from utils.validators import Validators
import pandas as pd
from PIL import Image
from utils.resource_path import resource_path
from datetime import datetime

class StockPage:

    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.stock_service = StockService(db)
        self.product_service = ProductService(db)

        self.all_stock = []
        self.filtered_stock = []
        self.sort_column = None
        self.sort_reverse = False

        self.export_icon = ctk.CTkImage(
            Image.open(resource_path("public/export-xlsx.png")),
            size=(20, 20)
        )

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def validate_imei_input(self, value):
        return (value.isdigit() and len(value) <= 15) or value == ""

    def build_ui(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("Treeview", rowheight=28)

        ctk.CTkLabel(
            self.frame,
            text="Stock Management",
            font=("Arial", 16)
        ).pack(pady=10)

        # ===== FORM =====
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        products = self.product_service.get_all()
        self.product_map = {p["name"]: p["id"] for p in products} if products else {}

        self.product_var = ctk.StringVar()
        product_values = list(self.product_map.keys())

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=product_values if product_values else ["No Products"],
            variable=self.product_var
        )
        self.product_dropdown.pack(side="left", padx=5)

        if product_values:
            self.product_var.set(product_values[0])

        vcmd = (self.root.register(self.validate_imei_input), "%P")

        self.imei_entry = ctk.CTkEntry(
            form,
            placeholder_text="IMEI (15 digits)",
            validate="key",
            validatecommand=vcmd
        )
        self.imei_entry.pack(side="left", padx=5)

        self.colour_entry = ctk.CTkEntry(form, placeholder_text="Colour")
        self.colour_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Add Stock", command=self.add_stock)\
            .pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # ===== SEARCH =====
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search by Product, IMEI, Colour..."
        )
        search_entry.pack(fill="x", padx=5)

        search_entry.bind("<KeyRelease>", self.filter_table)

        # ===== TABLE =====
        tree_frame = ctk.CTkFrame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Product", "IMEI", "Colour", "Qty", "Date"),
            show="headings"
        )

        for col in ("Product", "IMEI", "Colour", "Qty", "Date"):
            self.tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_by_column(c)
            )
            self.tree.column(col, width=140, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_stock(self):
        try:
            product_name = self.product_var.get()
            imei = self.imei_entry.get().strip()
            colour = self.colour_entry.get().strip()

            if product_name not in self.product_map:
                raise ValueError("Invalid product")

            if len(imei) != 15:
                raise ValueError("IMEI must be 15 digits")

            Validators.validate_imei(imei)

            self.stock_service.add_stock(
                self.user["id"],
                self.product_map[product_name],
                imei,
                colour,
                1
            )

            messagebox.showinfo("Success", "Stock added")

            self.imei_entry.delete(0, "end")
            self.colour_entry.delete(0, "end")

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        data = self.stock_service.get_all_stock() or []
        self.all_stock = list(data)
        self.filtered_stock = self.all_stock.copy()
        self.display_table(self.filtered_stock)

    def format_date(self, value):
        if not value:
            return ""
        try:
            return value.strftime("%Y-%m-%d %H:%M")
        except:
            return str(value)

    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["name"],
                    row["imei"],
                    row["colour"],
                    row["quantity"],
                    self.format_date(row.get("created_at"))
                )
            )

    def filter_table(self, event=None):
        keyword = self.search_var.get().lower()

        self.filtered_stock = [
            row for row in self.all_stock
            if keyword in str(row["name"]).lower()
            or keyword in str(row["imei"]).lower()
            or keyword in str(row["colour"]).lower()
        ]

        self.display_table(self.filtered_stock)

    def sort_by_column(self, col):
        mapping = {
            "Product": "name",
            "IMEI": "imei",
            "Colour": "colour",
            "Qty": "quantity",
            "Date": "created_at"
        }

        db_col = mapping[col]

        if self.sort_column == db_col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = db_col
            self.sort_reverse = False

        self.filtered_stock.sort(
            key=lambda x: x.get(db_col) or "",
            reverse=self.sort_reverse
        )

        self.display_table(self.filtered_stock)

    def export_to_excel(self):
        try:
            data = self.filtered_stock or self.all_stock

            if not data:
                messagebox.showwarning("No Data", "No stock data")
                return

            df = pd.DataFrame(data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Exported")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))