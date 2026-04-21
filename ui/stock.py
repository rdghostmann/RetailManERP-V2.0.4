import customtkinter as ctk
from tkinter import ttk, messagebox
from services.stock_service import StockService
from services.product_service import ProductService
from utils.validators import Validators
from app.config import InventoryConfig


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
        # Form
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.product_var = ctk.StringVar()
        self.imei_entry = ctk.CTkEntry(form, placeholder_text="IMEI")
        self.colour_entry = ctk.CTkEntry(form, placeholder_text="Colour")
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Quantity")

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.product_service.get_all()],
            variable=self.product_var
        )

        self.product_dropdown.pack(side="left", padx=5)
        self.imei_entry.pack(side="left", padx=5)
        self.colour_entry.pack(side="left", padx=5)
        self.qty_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Add Stock", command=self.add_stock).pack(side="left", padx=5)

        # Table
        self.tree = ttk.Treeview(self.frame, columns=("Product", "IMEI", "Colour", "Qty"), show="headings")
        for col in ("Product", "IMEI", "Colour", "Qty"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_stock(self):
        try:
            product_name = self.product_var.get()

            if not product_name:
                raise ValueError("Select a product")

            imei = self.imei_entry.get()
            colour = self.colour_entry.get()
            qty_raw = self.qty_entry.get()

            if not qty_raw.isdigit():
                raise ValueError("Quantity must be a number")

            quantity = int(qty_raw)

            Validators.validate_imei(imei)
            Validators.validate_quantity(quantity)

            product_list = self.product_service.get_all()

            product = next(
                (p for p in product_list if p["name"] == product_name),
                None
            )

            if not product:
                raise ValueError("Product not found")

            self.stock_service.add_stock(
                self.user["id"],
                product["id"],
                imei,
                colour,
                quantity
            )

            messagebox.showinfo("Success", "Stock added successfully")
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.stock_service.get_aggregated_stock()

        for row in data:
            qty = row["total_quantity"]

            # 🔴 Low stock alert
            tag = "low" if qty < InventoryConfig.LOW_STOCK_THRESHOLD else ""

            self.tree.insert(
                "",
                "end",
                values=(row["product_id"], "-", row["colour"], qty),
                tags=(tag,)
            )

        self.tree.tag_configure("low", background="red")