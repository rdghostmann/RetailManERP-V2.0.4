import customtkinter as ctk
from tkinter import ttk, messagebox

from services.plaza_services import PlazaService
from services.product_service import ProductService
from utils.validators import Validators


class PlazaPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.plaza_service = PlazaService(db)
        self.product_service = ProductService(db)

        self.products = self.product_service.get_all()

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.product_var = ctk.StringVar()
        self.imei_entry = ctk.CTkEntry(form, placeholder_text="IMEI")
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Quantity")
        self.customer_name = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_phone = ctk.CTkEntry(form, placeholder_text="Phone")

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )

        self.product_dropdown.pack(side="left", padx=5)
        self.imei_entry.pack(side="left", padx=5)
        self.qty_entry.pack(side="left", padx=5)
        self.customer_name.pack(side="left", padx=5)
        self.customer_phone.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Record Sale", command=self.record_sale).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("Product", "IMEI", "Qty", "Customer"), show="headings")
        for col in ("Product", "IMEI", "Qty", "Customer"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def record_sale(self):
        try:
            product = next(p for p in self.products if p["name"] == self.product_var.get())

            imei = self.imei_entry.get()
            qty = int(self.qty_entry.get())

            Validators.validate_imei(imei)
            Validators.validate_quantity(qty)

            # ⚠️ Deduct stock BEFORE recording sale
            stock = self.db.execute(
                "SELECT quantity FROM stock WHERE imei=%s",
                (imei,),
                fetchone=True
            )

            if not stock or stock["quantity"] < qty:
                raise ValueError("Insufficient stock")

            self.db.execute(
                "UPDATE stock SET quantity = quantity - %s WHERE imei=%s",
                (qty, imei)
            )

            self.plaza_service.record_sale(
                self.user["id"],
                product["id"],
                imei,
                qty,
                self.customer_name.get(),
                self.customer_phone.get()
            )

            messagebox.showinfo("Success", "Sale recorded")
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.plaza_service.get_all()

        for row in data:
            self.tree.insert("", "end", values=(
                row["product_id"],
                row["imei"],
                row["quantity"],
                row["customer_name"]
            ))