# ui/plaza.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from services.plaza_services import PlazaService
from services.product_service import ProductService
from utils.validators import Validators
from PIL import Image
from utils.resource_path import resource_path


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
            text="Plaza - Record Sales",
            font=("Arial", 18)
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

        ctk.CTkButton(form, text="Record Sale", command=self.record_sale)\
            .pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # ===== SEARCH =====
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Search sales (product, IMEI, customer...)"
        )
        search_entry.pack(fill="x", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

        # ===== TABLE =====
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Qty", "Customer", "Phone", "Date"),
            show="headings"
        )

        # ===== TABLE =====
        style = ttk.Style()
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 12)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            anchor="center"
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Qty", "Customer", "Phone", "Date"),
            show="headings"
        )

        for col in ("Product", "IMEI", "Colour", "Qty", "Customer", "Phone", "Date"):
            self.tree.heading(col, text=col, anchor="center")   # ✅ Center header
            self.tree.column(col, width=130, anchor="center")   # ✅ Center cell content

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # DATA
    # =========================
    def load_table(self):
        self.all_data = self.plaza_service.get_all() or []

        # Cache product names
        product_ids = {row["product_id"] for row in self.all_data}

        for pid in product_ids:
            if pid not in self.product_cache:
                product = self.db.fetch_one(
                    "SELECT name FROM products WHERE id=%s",
                    (pid,)
                )
                self.product_cache[pid] = product["name"] if product else "Unknown"

        self.display_table(self.all_data)

    def format_date(self, dt):
        if not dt:
            return "-"
        try:
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(dt)

    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                self.product_cache.get(row["product_id"], "Unknown"),
                row["imei"],
                row["colour"],
                row["quantity"],
                row["customer_name"],
                row["customer_phone"],
                self.format_date(row.get("created_at"))
            ))

    def filter_table(self, event=None):
        keyword = self.search_var.get().lower().strip()

        if not keyword:
            self.display_table(self.all_data)
            return

        filtered = [
            row for row in self.all_data
            if keyword in self.product_cache.get(row["product_id"], "").lower()
            or keyword in str(row["imei"]).lower()
            or keyword in str(row["customer_name"]).lower()
            or keyword in str(row["customer_phone"]).lower()
        ]

        self.display_table(filtered)

    # =========================
    # BUSINESS LOGIC
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

            # ✅ FIX: fetch colour using product_id (NOT imei)
            stock_records = self.db.fetch_all(
                "SELECT colour FROM stock WHERE product_id=%s AND quantity > 0",
                (product["id"],)
            )

            colours = list({s["colour"] for s in stock_records})

            if not colours:
                self.product_info_label.configure(text="No stock available", text_color="red")
                return

            self.fetched_product = product
            self.available_colours = colours

            self.colour_dropdown.configure(values=colours)
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

            name = self.customer_name.get().strip()
            phone = self.customer_phone.get().strip()

            if not name:
                raise ValueError("Customer name required")

            Validators.validate_phone(phone)

            self.plaza_service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                self.imei_entry.get().strip(),
                self.colour_var.get(),
                self.quantity,
                name,
                phone
            )

            messagebox.showinfo("Success", "Sale recorded")

            self.imei_entry.delete(0, "end")
            self.customer_name.delete(0, "end")
            self.customer_phone.delete(0, "end")

            self.reset_lookup()
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # EXPORT
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No sales data to export")
                return

            formatted_data = [
                {
                    "Product": self.product_cache.get(row["product_id"], "Unknown"),
                    "IMEI": row["imei"],
                    "Colour": row["colour"],
                    "Quantity": row["quantity"],
                    "Customer": row["customer_name"],
                    "Phone": row["customer_phone"],
                    "Date": self.format_date(row.get("created_at"))
                }
                for row in self.all_data
            ]

            df = pd.DataFrame(formatted_data)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Sales exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))