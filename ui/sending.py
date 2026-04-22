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
        self.customer_name_entry = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.contact_entry = ctk.CTkEntry(form, placeholder_text="Customer Contact")
        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Description")

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )

        self.product_dropdown.pack(side="left", padx=5)
        self.customer_name_entry.pack(side="left", padx=5)
        self.contact_entry.pack(side="left", padx=5)
        self.desc_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Dispatch", command=self.dispatch).pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("Product", "Customer", "Contact", "Description"), show="headings")
        for col in ("Product", "Customer", "Contact", "Description"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def dispatch(self):
        try:
            product = next(p for p in self.products if p["name"] == self.product_var.get())

            customer_name = self.customer_name_entry.get().strip()
            if not customer_name:
                raise ValueError("Customer name is required")

            contact = self.contact_entry.get().strip()
            if not contact:
                raise ValueError("Customer contact is required")

            Validators.validate_phone(contact)

            self.sending_service.create_dispatch(
                self.user["id"],
                product["id"],
                customer_name,
                contact,
                self.desc_entry.get().strip()
            )

            messagebox.showinfo("Success", "Dispatch recorded")
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.sending_service.get_all()

        for row in data:
            # Fetch product name
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )
            product_name = product["name"] if product else "Unknown"

            self.tree.insert("", "end", values=(
                product_name,
                row["customer_name"],
                row["customer_contact"],
                row["description"]
            ))