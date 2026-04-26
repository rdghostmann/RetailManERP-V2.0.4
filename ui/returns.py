# ui/returns.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from PIL import Image

from services.returns_services import ReturnsService
from services.product_service import ProductService
from utils.resource_path import resource_path


class ReturnsPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.returns_service = ReturnsService(db)
        self.product_service = ProductService(db)

        self.all_data = []
        self.fetched_sale = None

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

        # ================= FORM =================
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_sale())

        self.sale_info_label = ctk.CTkLabel(form, text="No sale found", text_color="gray")
        self.sale_info_label.pack(side="left", padx=5)

        self.qty_entry = ctk.CTkEntry(form, width=60)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(side="left", padx=5)

        self.reason_entry = ctk.CTkEntry(form, placeholder_text="Reason for return")
        self.reason_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Record Return",
            command=self.record_return
        ).pack(side="left", padx=5)

        # ================= SEARCH =================
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search returns..."
        )
        search_entry.pack(fill="x", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

        # ================= TABLE =================
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Treeview", rowheight=28, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.tree = ttk.Treeview(
            table_frame,
            columns=(
                "BatchNo",
                "Product",
                "IMEI",
                "Colour",
                "Customer",
                "Qty",
                "Reason",
                "Date"
            ),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        self.tree.pack(fill="both", expand=True)

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
                row.get("batch_no"),
                row.get("product_name"),
                row.get("imei"),
                row.get("colour"),
                row.get("customer_name"),
                row.get("quantity"),
                row.get("reason"),
                self.format_date(row.get("created_at"))
            ))

    # =========================
    # SEARCH
    # =========================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower().strip()

        filtered = [
            r for r in self.all_data
            if keyword in str(r.get("batch_no", "")).lower()
            or keyword in str(r.get("product_name", "")).lower()
            or keyword in str(r.get("imei", "")).lower()
            or keyword in str(r.get("customer_name", "")).lower()
            or keyword in str(r.get("reason", "")).lower()
        ]

        self.display_table(filtered)

    # =========================
    # LOOKUP SALE
    # =========================
    def lookup_sale(self):
        imei = self.imei_entry.get().strip()

        if not imei:
            self.sale_info_label.configure(text="No sale found", text_color="gray")
            self.fetched_sale = None
            return

        sale = self.returns_service.get_plaza_sale_by_imei(imei)

        if not sale:
            self.sale_info_label.configure(text="Not found", text_color="red")
            self.fetched_sale = None
            return

        self.fetched_sale = sale
        self.sale_info_label.configure(
            text=f"{sale['product_name']} | {sale['customer_name']}",
            text_color="green"
        )

    # =========================
    # RECORD RETURN
    # =========================
    def record_return(self):
        try:
            if not self.fetched_sale:
                raise ValueError("Invalid IMEI selected")

            qty = int(self.qty_entry.get())

            self.returns_service.create_return(
                self.user["id"],
                self.fetched_sale["id"],
                qty,
                self.reason_entry.get().strip()
            )

            messagebox.showinfo("Success", "Return recorded")

            self.imei_entry.delete(0, "end")
            self.reason_entry.delete(0, "end")
            self.qty_entry.delete(0, "end")
            self.qty_entry.insert(0, "1")

            self.fetched_sale = None
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # EXPORT
    # =========================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No return data")
                return

            df = pd.DataFrame([
                {
                    "BatchNo": r.get("batch_no"),
                    "Product": r.get("product_name"),
                    "IMEI": r.get("imei"),
                    "Colour": r.get("colour"),
                    "Customer": r.get("customer_name"),
                    "Qty": r.get("quantity"),
                    "Reason": r.get("reason"),
                    "Date": self.format_date(r.get("created_at"))
                }
                for r in self.all_data
            ])

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )

            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Export completed")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))