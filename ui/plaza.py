# ui/plaza.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

from services.plaza_services import PlazaService
from services.product_service import ProductService
from utils.validators import Validators
from PIL import Image


class PlazaPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.plaza_service = PlazaService(db)
        self.product_service = ProductService(db)

        self.fetched_product = None
        self.available_colours = []
        self.quantity = 1

        # ✅ Load export icon
        self.export_icon = ctk.CTkImage(
            Image.open("public/export-xlsx.png"),
            size=(18, 18)
        )

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Plaza - Record Sales",
            font=("Arial", 18)
        ).pack(pady=10)
         
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_product())

        self.product_info_label = ctk.CTkLabel(form, text="No product selected", text_color="gray")
        self.product_info_label.pack(side="left", padx=5)

        self.colour_var = ctk.StringVar()
        self.colour_dropdown = ctk.CTkComboBox(form, variable=self.colour_var, values=[])
        self.colour_dropdown.pack(side="left", padx=5)

        self.customer_name = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_name.pack(side="left", padx=5)

        self.customer_phone = ctk.CTkEntry(form, placeholder_text="Phone")
        self.customer_phone.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Record Sale", command=self.record_sale).pack(side="left", padx=5)

        # ✅ Export Button with Image
        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # Table
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Qty", "Customer", "Phone"),
            show="headings"
        )

        for col in ("Product", "IMEI", "Colour", "Qty", "Customer", "Phone"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def lookup_product(self):
        imei = self.imei_entry.get().strip()

        if not imei:
            self.fetched_product = None
            self.available_colours = []
            self.colour_dropdown.configure(values=[])
            self.colour_var.set("")
            self.product_info_label.configure(text="No product selected", text_color="gray")
            return

        try:
            product = self.product_service.get_by_imei(imei)

            if not product:
                self.product_info_label.configure(text="IMEI not found", text_color="red")
                return

            stock_records = self.db.fetch_all(
                "SELECT DISTINCT colour FROM stock WHERE imei=%s AND quantity > 0",
                (imei,)
            )

            self.available_colours = [s["colour"] for s in stock_records]

            if not self.available_colours:
                self.product_info_label.configure(text="No stock available", text_color="red")
                return

            self.fetched_product = product
            self.colour_dropdown.configure(values=self.available_colours)
            self.colour_var.set(self.available_colours[0])

            self.product_info_label.configure(
                text=f"{product['name']} ({product['brand']})",
                text_color="green"
            )

        except Exception as e:
            self.product_info_label.configure(text=str(e), text_color="red")

    def record_sale(self):
        try:
            if not self.fetched_product:
                raise ValueError("Invalid IMEI")

            colour = self.colour_var.get()
            imei = self.imei_entry.get().strip()

            Validators.validate_phone(self.customer_phone.get())

            self.plaza_service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                imei,
                colour,
                self.quantity,
                self.customer_name.get().strip(),
                self.customer_phone.get().strip()
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
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )
            product_name = product["name"] if product else "Unknown"

            self.tree.insert("", "end", values=(
                product_name,
                row["imei"],
                row["colour"],
                row["quantity"],
                row["customer_name"],
                row["customer_phone"]
            ))

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            data = self.plaza_service.get_all()

            if not data:
                messagebox.showwarning("No Data", "No sales data to export")
                return

            formatted_data = []

            for row in data:
                product = self.db.fetch_one(
                    "SELECT name FROM products WHERE id=%s",
                    (row["product_id"],)
                )

                formatted_data.append({
                    "Product": product["name"] if product else "Unknown",
                    "IMEI": row["imei"],
                    "Colour": row["colour"],
                    "Quantity": row["quantity"],
                    "Customer": row["customer_name"],
                    "Phone": row["customer_phone"]
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

            messagebox.showinfo("Success", "Sales exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))