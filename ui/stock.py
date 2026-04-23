# ui/stock.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from services.stock_service import StockService
from services.product_service import ProductService
from utils.validators import Validators
import pandas as pd


class StockPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.stock_service = StockService(db)
        self.product_service = ProductService(db)

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        # Products
        products = self.product_service.get_all()
        product_names = [p["name"] for p in products] if products else ["No Products"]

        self.product_var = ctk.StringVar()
        self.product_dropdown = ctk.CTkComboBox(form, values=product_names, variable=self.product_var)
        self.product_dropdown.pack(side="left", padx=5)

        self.imei_entry = ctk.CTkEntry(form, placeholder_text="IMEI")
        self.imei_entry.pack(side="left", padx=5)

        self.colour_entry = ctk.CTkEntry(form, placeholder_text="Colour")
        self.colour_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Add Stock", command=self.add_stock).pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="📥 Export Excel",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # Table
        tree_frame = ctk.CTkFrame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Product", "IMEI", "Colour", "Qty"),
            show="headings"
        )

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for col in ("Product", "IMEI", "Colour", "Qty"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_stock(self):
        try:
            product_name = self.product_var.get()
            imei = self.imei_entry.get().strip()
            colour = self.colour_entry.get().strip()

            if not product_name:
                raise ValueError("Please select a product")
            if not imei:
                raise ValueError("IMEI is required")
            if not colour:
                raise ValueError("Colour is required")

            Validators.validate_imei(imei)

            product_list = self.product_service.get_all()
            product = next((p for p in product_list if p["name"] == product_name), None)

            if not product:
                raise ValueError("Product not found")

            self.stock_service.add_stock(
                self.user["id"], product["id"], imei, colour, 1
            )

            messagebox.showinfo("Success", "Stock added successfully")

            self.imei_entry.delete(0, 'end')
            self.colour_entry.delete(0, 'end')

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.stock_service.get_all_stock()

        for row in data:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["product_name"],
                    row["imei"],
                    row["colour"],
                    row["quantity"]
                )
            )

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            data = self.stock_service.get_all_stock()

            if not data:
                messagebox.showwarning("No Data", "No stock data to export")
                return

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Rename columns for clean Excel output
            df = df.rename(columns={
                "product_name": "Product",
                "imei": "IMEI",
                "colour": "Colour",
                "quantity": "Quantity"
            })

            # File dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel File"
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Data exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))