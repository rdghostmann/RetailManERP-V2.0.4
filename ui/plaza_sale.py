#ui/plaza_sale.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from utils.excel_exporter import ExcelExporter
from services.plaza_service import PlazaService


class PlazaSalePage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.service = PlazaService(db)
        self.all_data = []

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):

        ctk.CTkLabel(
            self.frame,
            text="Plaza Sales (Finalized)",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        top = ctk.CTkFrame(self.frame)
        top.pack(fill="x", padx=10)

        self.search_var = ctk.StringVar()

        entry = ctk.CTkEntry(
            top,
            textvariable=self.search_var,
            placeholder_text="Search..."
        )
        entry.pack(side="left", fill="x", expand=True)
        entry.bind("<KeyRelease>", self.filter_table)

        ctk.CTkButton(
            top,
            text="Export Excel",
            fg_color="#16A34A",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # TABLE
        columns = ("BatchNo","Product","IMEI","Colour","Qty","Sold By","Date")

        self.tree = ttk.Treeview(
            self.frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=130)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = ctk.CTkLabel(self.frame, text="Loading...", text_color="gray")
        self.status.pack()

    def load_table(self):
        try:
            data = self.service.get_all_sales()

            if not data:
                self.status.configure(text="No sales records")
                return

            self.all_data = data
            self.display(data)

            self.status.configure(text=f"{len(data)} records")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row.get("batch_no","-"),
                row.get("product_name"),
                row.get("imei"),
                row.get("colour"),
                row.get("quantity"),
                row.get("sold_by"),
                self.format_date(row.get("created_at"))
            ))

    def filter_table(self, e=None):
        k = self.search_var.get().lower()

        if not k:
            self.display(self.all_data)
            return

        self.display([
            r for r in self.all_data
            if k in str(r.get("product_name","")).lower()
            or k in str(r.get("imei","")).lower()
        ])

    def format_date(self, dt):
        try:
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(dt) if dt else "-"

    def export_to_excel(self):
        if not self.all_data:
            messagebox.showwarning("No Data","Nothing to export")
            return

        df = pd.DataFrame([{
            "BatchNo": r.get("batch_no"),
            "Product": r.get("product_name"),
            "IMEI": r.get("imei"),
            "Colour": r.get("colour"),
            "Qty": r.get("quantity"),
            "Sold By": r.get("sold_by"),
            "Date": self.format_date(r.get("created_at"))
        } for r in self.all_data])

        exporter = ExcelExporter("RetailMan_Reports.xlsx")
        exporter.export_sheet("PlazaSales", df)

        messagebox.showinfo("Success","Excel updated")