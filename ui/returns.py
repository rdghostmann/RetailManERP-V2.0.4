# ui/returns.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from PIL import Image

from services.returns_services import ReturnsService
from services.product_service import ProductService
from utils.validators import Validators
from utils.resource_path import resource_path


class ReturnsPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.returns_service = ReturnsService(db)
        self.product_service = ProductService(db)

        self.fetched_sale = None
        self.all_data = []

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
            text="Plaza Returns Management",
            font=("Arial", 16)
        ).pack(pady=10)

        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_sale())

        self.sale_info_label = ctk.CTkLabel(form, text="No sale found", text_color="gray")
        self.sale_info_label.pack(side="left", padx=5)

        self.return_qty_entry = ctk.CTkEntry(form, width=80)
        self.return_qty_entry.insert(0, "1")
        self.return_qty_entry.configure(state="disabled")
        self.return_qty_entry.pack(side="left", padx=5)

        self.reason_entry = ctk.CTkEntry(form, placeholder_text="Reason for return")
        self.reason_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Record Return",
            command=self.record_return
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # SEARCH
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="🔍 Search returns..."
        )
        search_entry.pack(fill="x", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

       # ===== TABLE =====
        style = ttk.Style()

        # Base table styling
        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 12)
        )

        # Header styling
        style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            anchor="center"
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Customer", "Returned Qty", "Reason", "Date"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="center")   # ✅ center header
            self.tree.column(col, width=130, anchor="center")   # ✅ center cell content

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # FORMAT DATE
    # =========================
    def format_date(self, dt):
        if not dt:
            return "-"
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%d %H:%M")

    # =========================
    # LOOKUP
    # =========================
    def lookup_sale(self):
        imei = self.imei_entry.get().strip()

        if not imei:
            self.fetched_sale = None
            self.sale_info_label.configure(text="No sale found", text_color="gray")
            return

        try:
            sale = self.returns_service.get_plaza_sale_by_imei(imei)

            if not sale:
                self.fetched_sale = None
                self.sale_info_label.configure(text="IMEI not found in sales", text_color="red")
                return

            self.fetched_sale = sale
            self.sale_info_label.configure(
                text=f"{sale['product_name']} | {sale['colour']} | {sale['customer_name']}",
                text_color="green"
            )

        except Exception as e:
            self.sale_info_label.configure(text=str(e), text_color="red")

    # =========================
    # RECORD RETURN
    # =========================
    def record_return(self):
        try:
            if not self.fetched_sale:
                raise ValueError("Invalid IMEI")

            self.returns_service.create_return(
                self.user["id"],
                self.fetched_sale["id"],
                1,
                self.reason_entry.get().strip()
            )

            messagebox.showinfo("Success", "Return recorded")

            self.imei_entry.delete(0, "end")
            self.reason_entry.delete(0, "end")
            self.fetched_sale = None

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # LOAD TABLE
    # =========================
    def load_table(self):
        self.all_data = self.returns_service.get_all() or []
        self.display_table(self.all_data)

    # =========================
    # DISPLAY TABLE
    # =========================
    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row["product_name"],
                row["imei"],
                row["colour"],
                row["customer_name"],
                row["quantity"],
                row["reason"],
                self.format_date(row.get("created_at"))  # ✅ DATE
            ))

    # =========================
    # FILTER
    # =========================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower()

        filtered = [
            row for row in self.all_data
            if keyword in row["product_name"].lower()
            or keyword in row["imei"].lower()
            or keyword in row["customer_name"].lower()
            or keyword in (row["reason"] or "").lower()
        ]

        self.display_table(filtered)

    # =========================
    # EXPORT
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No return data")
                return

            formatted = [{
                "Product": r["product_name"],
                "IMEI": r["imei"],
                "Colour": r["colour"],
                "Customer": r["customer_name"],
                "Returned Qty": r["quantity"],
                "Reason": r["reason"],
                "Date": self.format_date(r.get("created_at"))
            } for r in self.all_data]

            df = pd.DataFrame(formatted)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))