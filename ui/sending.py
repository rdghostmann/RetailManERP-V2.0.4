import customtkinter as ctk
from tkinter import ttk, messagebox

from services.sending_services import SendingService
from services.product_service import ProductService
from utils.validators import Validators


class SendingPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.sending_service = SendingService(db)
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
        self.qty_entry = ctk.CTkEntry(form, placeholder_text="Quantity")
        self.contact_entry = ctk.CTkEntry(form, placeholder_text="Customer Contact")
        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Description")

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )

        self.product_dropdown.pack(side="left", padx=5)
        self.qty_entry.pack(side="left", padx=5)
        self.contact_entry.pack(side="left", padx=5)
        self.desc_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Dispatch", command=self.dispatch).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("Product", "Qty", "Contact"), show="headings")
        for col in ("Product", "Qty", "Contact"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def dispatch(self):
        try:
            product = next(p for p in self.products if p["name"] == self.product_var.get())
            qty = int(self.qty_entry.get())

            Validators.validate_quantity(qty)

            self.sending_service.create_dispatch(
                self.user["id"],
                product["id"],
                qty,
                self.contact_entry.get(),
                self.desc_entry.get()
            )

            messagebox.showinfo("Success", "Dispatch recorded")
            self.load_table()

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.sending_service.get_all()

        for row in data:
            self.tree.insert("", "end", values=(
                row["product_id"],
                row["quantity"],
                row["customer_contact"]
            ))