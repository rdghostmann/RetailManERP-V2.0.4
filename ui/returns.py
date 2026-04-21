import customtkinter as ctk
from tkinter import ttk, messagebox

from services.returns_services import ReturnsService
from services.product_service import ProductService
from utils.validators import Validators


class ReturnsPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.returns_service = ReturnsService(db)
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
        self.colour_entry = ctk.CTkEntry(form, placeholder_text="Colour")
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Quantity")
        self.reason_entry = ctk.CTkEntry(form, placeholder_text="Reason")

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )

        self.product_dropdown.pack(side="left", padx=5)
        self.imei_entry.pack(side="left", padx=5)
        self.colour_entry.pack(side="left", padx=5)
        self.qty_entry.pack(side="left", padx=5)
        self.reason_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Record Return", command=self.record_return).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("Product", "IMEI", "Qty", "Reason"), show="headings")
        for col in ("Product", "IMEI", "Qty", "Reason"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def record_return(self):
        try:
            product = next(p for p in self.products if p["name"] == self.product_var.get())

            imei = self.imei_entry.get()
            qty = int(self.qty_entry.get())

            Validators.validate_imei(imei)
            Validators.validate_quantity(qty)

            self.returns_service.create_return(
                self.user["id"],
                product["id"],
                imei,
                self.colour_entry.get(),
                qty,
                self.reason_entry.get()
            )

            messagebox.showinfo("Success", "Return recorded")
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.returns_service.get_all()

        for row in data:
            self.tree.insert("", "end", values=(
                row["product_id"],
                row["imei"],
                row["quantity"],
                row["reason"]
            ))