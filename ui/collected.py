#ui/collected.py
import customtkinter as ctk
from tkinter import ttk, messagebox
import pandas as pd
from utils.excel_exporter import ExcelExporter


class CollectedPage:
    def __init__(self, root, db, user):
        self.db = db
        self.user = user

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_data()

    # ==============================
    # UI
    # ==============================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Collected Devices",
            font=("Arial", 12)
        ).pack(pady=10)

        # TOP BAR
        top = ctk.CTkFrame(self.frame)
        top.pack(fill="x", padx=10, pady=5)

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            top,
            textvariable=self.search_var,
            placeholder_text="Search collected devices..."
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

        ctk.CTkButton(
            top,
            text="Export Excel",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="right", padx=5)

        # TABLE
        self.tree = ttk.Treeview(
        self.frame,
        columns=(
            "ID",
            "BatchNo",
            "Product",
            "Customer",
            "Contact",
            "Collector",
            "Collector Phone",
            "Date",
            "Status"
        ),
        show="headings"
    )


        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ==============================
    # LOAD DATA (FIXED QUERY)
    # ==============================
    def load_data(self):
        try:
            query = """
            SELECT 
                c.id,
                c.batch_no,
                p.name AS product_name,
                c.customer_name,
                c.customer_contact,
                c.collected_by_name,
                c.collected_by_phone,
                c.created_at,
                c.status
            FROM collected c
            LEFT JOIN products p ON c.product_id = p.id
            ORDER BY c.created_at DESC
            """

            self.all_data = self.db.fetch_all(query) or []
            self.display_table(self.all_data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # FORMAT DATE
    # ==============================
    def format_date(self, dt):
        if not dt:
            return "-"
        try:
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(dt)

    # ==============================
    # DISPLAY TABLE
    # ==============================
    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row.get("id"),
                row.get("batch_no"),
                row.get("product_name") or "Unknown",
                row.get("customer_name"),
                row.get("customer_contact"),
                row.get("collected_by_name"),
                row.get("collected_by_phone"),
                self.format_date(row.get("created_at")),
                row.get("status")
            ))

    # ==============================
    # SEARCH
    # ==============================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower()

        filtered = [
            row for row in self.all_data
            if keyword in str(row.get("product_name", "")).lower()
            or keyword in str(row.get("customer_name", "")).lower()
            or keyword in str(row.get("customer_contact", "")).lower()
            or keyword in str(row.get("collected_by_name", "")).lower()
            or keyword in str(row.get("collected_by_phone", "")).lower()
        ]

        self.display_table(filtered)

    # ==============================
    # EXPORT
    # ==============================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No collected data available")
                return

            df = pd.DataFrame([
                {
                    "Product": row.get("product_name"),
                    "Customer": row.get("customer_name"),
                    "Contact": row.get("customer_contact"),
                    "Collector": row.get("collected_by_name"),
                    "Collector Phone": row.get("collected_by_phone"),
                    "Status": row.get("status"),
                    "Date": self.format_date(row.get("created_at"))
                }
                for row in self.all_data
            ])

            exporter = ExcelExporter("RetailMan_Reports.xlsx")
            exporter.export_sheet("Collected", df)

            messagebox.showinfo(
                "Export Successful",
                "Collected sheet updated in RetailMan_Reports.xlsx"
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e))