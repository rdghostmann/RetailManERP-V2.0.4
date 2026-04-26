# ui/plaza.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from services.plaza_service import PlazaService
from services.product_service import ProductService
from utils.validators import Validators
from PIL import Image
from utils.resource_path import resource_path
from utils.excel_exporter import ExcelExporter


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
        self.all_data = []
        self.product_cache = {}

        self.export_icon = ctk.CTkImage(
            Image.open(resource_path("public/export-xlsx.png")),
            size=(18, 18)
        )

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
            text="Plaza - Entry",
            font=("Arial", 12)
        ).pack(pady=10)

        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_product())

        self.product_info_label = ctk.CTkLabel(
            form, text="No product selected", text_color="gray"
        )
        self.product_info_label.pack(side="left", padx=5)

        self.colour_var = ctk.StringVar()
        self.colour_dropdown = ctk.CTkComboBox(form, variable=self.colour_var, values=[])
        self.colour_dropdown.pack(side="left", padx=5)

        self.customer_name = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_name.pack(side="left", padx=5)

        self.customer_phone = ctk.CTkEntry(form, placeholder_text="Phone")
        self.customer_phone.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Record Entry", command=self.record_sale)\
            .pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Mark as Sale",
            fg_color="#2563EB",
            command=self.mark_sale
        ).pack(side="left", padx=5)

        # ================= SEARCH =================
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Search..."
        )
        search_entry.pack(fill="x", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

        # ================= TABLE STYLE =================
        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        # ================= TABLE (UPDATED) =================
        columns = (
            "BatchNo",
            "ID",
            "Product",
            "IMEI",
            "Colour",
            "Qty",
            "Customer",
            "Phone",
            "Date"
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # DATA
    # =========================
    def load_table(self):
        self.all_data = self.plaza_service.get_all() or []

        self.display_table(self.all_data)

    def format_date(self, dt):
        if not dt:
            return "-"
        try:
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(dt)

    # =========================
    # DISPLAY (UPDATED)
    # =========================
    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row.get("batch_no", "-"),
                row.get("id"),
                row.get("product_name", "Unknown"),
                row.get("imei"),
                row.get("colour"),
                row.get("quantity"),
                row.get("customer_name"),
                row.get("customer_phone"),
                self.format_date(row.get("created_at"))
            ))

    # =========================
    # FILTER
    # =========================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower().strip()

        if not keyword:
            self.display_table(self.all_data)
            return

        filtered = [
            row for row in self.all_data
            if keyword in str(row.get("batch_no", "")).lower()
            or keyword in str(row.get("imei", "")).lower()
            or keyword in str(row.get("customer_name", "")).lower()
            or keyword in str(row.get("customer_phone", "")).lower()
        ]

        self.display_table(filtered)

    # =========================
    # BUSINESS LOGIC (UNCHANGED)
    # =========================
    def lookup_product(self):
        imei = self.imei_entry.get().strip()

        if not imei:
            self.reset_lookup()
            return

        try:
            product = self.product_service.get_by_imei(imei)

            if not product:
                self.product_info_label.configure(text="IMEI not found", text_color="red")
                return

            stock_records = self.db.fetch_all(
                "SELECT colour FROM stock WHERE product_id=%s AND quantity > 0",
                (product["id"],)
            )

            colours = list({s["colour"] for s in stock_records})

            self.fetched_product = product
            self.available_colours = colours

            self.colour_dropdown.configure(values=colours)
            if colours:
                self.colour_var.set(colours[0])

            self.product_info_label.configure(
                text=f"{product['name']} ({product['brand']})",
                text_color="green"
            )

        except Exception as e:
            self.product_info_label.configure(text=str(e), text_color="red")

    def reset_lookup(self):
        self.fetched_product = None
        self.available_colours = []
        self.colour_dropdown.configure(values=[])
        self.colour_var.set("")
        self.product_info_label.configure(text="No product selected", text_color="gray")

    def record_sale(self):
        try:
            if not self.fetched_product:
                raise ValueError("Invalid IMEI")

            Validators.validate_phone(self.customer_phone.get().strip())

            self.plaza_service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                self.imei_entry.get().strip(),
                self.colour_var.get(),
                self.quantity,
                self.customer_name.get().strip(),
                self.customer_phone.get().strip()
            )

            messagebox.showinfo("Success", "Entry recorded")

            self.imei_entry.delete(0, "end")
            self.customer_name.delete(0, "end")
            self.customer_phone.delete(0, "end")

            self.reset_lookup()
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mark_sale(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Select", "Select a record")
            return

        values = self.tree.item(selected[0])["values"]
        plaza_id = values[1]  # ID shifted because BatchNo added

        try:
            self.plaza_service.mark_as_sale(self.user["id"], plaza_id)

            messagebox.showinfo("Success", "Marked as completed sale")
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # EXPORT (UPDATED)
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No sales data available")
                return

            df = pd.DataFrame([
                {
                    "BatchNo": row.get("batch_no"),
                    "ID": row.get("id"),
                    "Product": row.get("product_name"),
                    "IMEI": row.get("imei"),
                    "Colour": row.get("colour"),
                    "Quantity": row.get("quantity"),
                    "Customer": row.get("customer_name"),
                    "Phone": row.get("customer_phone"),
                    "Date": self.format_date(row.get("created_at"))
                }
                for row in self.all_data
            ])

            exporter = ExcelExporter("RetailMan_Reports.xlsx")
            exporter.export_sheet("Plaza-Entry", df)

            messagebox.showinfo("Export Successful", "Plaza-Entry updated")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))