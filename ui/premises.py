# ui/premises.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.premises_service import PremisesService
from services.product_service import ProductService
import pandas as pd
from utils.excel_exporter import ExcelExporter


class PremisesPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.service = PremisesService(db)
        self.product_service = ProductService(db)

        self.fetched_product = None
        self.all_data = []

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Premises Sales",
            font=("Arial", 12)
        ).pack(pady=10)

        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.imei = ctk.CTkEntry(form, placeholder_text="Enter IMEI")
        self.imei.pack(side="left", padx=5)
        self.imei.bind("<KeyRelease>", lambda e: self.lookup_product())

        self.product_label = ctk.CTkLabel(
            form,
            text="No product selected",
            text_color="gray"
        )
        self.product_label.pack(side="left", padx=5)

        self.colour_var = ctk.StringVar()
        self.colour_dropdown = ctk.CTkComboBox(
            form,
            variable=self.colour_var,
            values=[]
        )
        self.colour_dropdown.pack(side="left", padx=5)

        self.customer = ctk.CTkEntry(form, placeholder_text="Customer")
        self.customer.pack(side="left", padx=5)

        self.phone = ctk.CTkEntry(form, placeholder_text="Phone")
        self.phone.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Sell", command=self.sell).pack(side="left", padx=5)

        ctk.CTkButton(
            self.frame,
            text="Export to Excel",
            command=self.export_to_excel,
            fg_color="#15803D"
        ).pack(pady=5)

        # ======================
        # TABLE (UPDATED)
        # ======================
        self.tree = ttk.Treeview(
            self.frame,
            columns=("BatchNo", "Product", "IMEI", "Colour", "Qty", "Customer", "Phone"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=140)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # DATA
    # =========================
    def load_table(self):
        self.all_data = self.service.get_all() or []
        self.display_table(self.all_data)

    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row.get("batch_no"),
                row.get("product_name", "Unknown"),
                row.get("imei"),
                row.get("colour"),
                row.get("quantity"),
                row.get("customer_name"),
                row.get("customer_phone")
            ))

    # =========================
    # BUSINESS
    # =========================
    def lookup_product(self):
        imei = self.imei.get().strip()
        if not imei:
            return

        product = self.product_service.get_by_imei(imei)

        if not product:
            self.product_label.configure(text="Not found", text_color="red")
            return

        stock = self.db.fetch_all(
            "SELECT colour FROM stock WHERE product_id=%s AND quantity > 0",
            (product["id"],)
        )

        colours = list({s["colour"] for s in stock})

        self.fetched_product = product
        self.colour_dropdown.configure(values=colours)
        if colours:
            self.colour_var.set(colours[0])

        self.product_label.configure(
            text=product["name"],
            text_color="green"
        )

    def sell(self):
        try:
            if not self.fetched_product:
                raise ValueError("Invalid product")

            self.service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                self.imei.get().strip(),
                self.colour_var.get(),
                1,
                self.customer.get().strip(),
                self.phone.get().strip()
            )

            messagebox.showinfo("Success", "Sale recorded")

            self.imei.delete(0, "end")
            self.customer.delete(0, "end")
            self.phone.delete(0, "end")

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # EXPORT
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No sales data available")
                return

            df = pd.DataFrame([
                {
                    "BatchNo": r.get("batch_no"),
                    "Product": r.get("product_name"),
                    "IMEI": r.get("imei"),
                    "Colour": r.get("colour"),
                    "Qty": r.get("quantity"),
                    "Customer": r.get("customer_name"),
                    "Phone": r.get("customer_phone")
                }
                for r in self.all_data
            ])

            exporter = ExcelExporter("RetailMan_Reports.xlsx")
            exporter.export_sheet("PremisesSales", df)

            messagebox.showinfo("Success", "Export completed")

        except Exception as e:
            messagebox.showerror("Error", str(e))