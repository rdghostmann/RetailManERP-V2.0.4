# ui/stock.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.stock_service import StockService
from services.product_service import ProductService
from utils.validators import Validators


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

        # Get products safely
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

        # Table with Scrollbar
        tree_frame = ctk.CTkFrame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, columns=("Product", "IMEI", "Colour", "Qty"), show="headings")
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        for col in ("Product", "IMEI", "Colour", "Qty"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

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
            
            # Check if product exists
            product_list = self.product_service.get_all()
            product = next((p for p in product_list if p["name"] == product_name), None)

            if not product:
                raise ValueError("Product not found")

            self.stock_service.add_stock(
                self.user["id"], product["id"], imei, colour, 1
            )

            messagebox.showinfo("Success", "Stock added successfully")
            
            # Clear fields after success
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