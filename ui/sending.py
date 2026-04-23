# ui/sending.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from services.sending_services import SendingService
from services.product_service import ProductService
from utils.validators import Validators
import pandas as pd
from PIL import Image


class SendingPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.sending_service = SendingService(db)
        self.product_service = ProductService(db)

        self.products = self.product_service.get_all()

        # ✅ Load export icon
        self.export_icon = ctk.CTkImage(
            Image.open("public/export-xlsx.png"),
            size=(20, 20)
        )

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Dispatch Management",
            font=("Arial", 18)
        ).pack(pady=10)
         
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.product_var = ctk.StringVar()

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )
        self.product_dropdown.pack(side="left", padx=5)

        self.customer_name_entry = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_name_entry.pack(side="left", padx=5)

        self.contact_entry = ctk.CTkEntry(form, placeholder_text="Customer Contact")
        self.contact_entry.pack(side="left", padx=5)

        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Description")
        self.desc_entry.pack(side="left", padx=5)

        # Dispatch Button
        ctk.CTkButton(
            form,
            text="Dispatch",
            command=self.dispatch
        ).pack(side="left", padx=5)

        # ✅ Export Button with icon
        ctk.CTkButton(
            form,
            text="  Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # Table
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "Customer", "Contact", "Description"),
            show="headings"
        )

        for col in ("Product", "Customer", "Contact", "Description"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

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

            # Clear inputs
            self.customer_name_entry.delete(0, "end")
            self.contact_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.sending_service.get_all()

        for row in data:
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

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            data = self.sending_service.get_all()

            if not data:
                messagebox.showwarning("No Data", "No sending data to export")
                return

            formatted_data = []

            for row in data:
                product = self.db.fetch_one(
                    "SELECT name FROM products WHERE id=%s",
                    (row["product_id"],)
                )
                product_name = product["name"] if product else "Unknown"

                formatted_data.append({
                    "Product": product_name,
                    "Customer": row["customer_name"],
                    "Contact": row["customer_contact"],
                    "Description": row["description"]
                })

            df = pd.DataFrame(formatted_data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel File"
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Sending data exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))