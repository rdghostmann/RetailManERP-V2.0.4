# ui/logs.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
from utils.excel_exporter import ExcelExporter
from tkinter import messagebox

from app.config import UIConfig


class LogsPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        # 🔐 Admin-only guard
        if self.user["role"] != "admin":
            messagebox.showerror("Access Denied", "You are not authorized to view logs.")
            return

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_logs()

    # ==============================
    # 🧱 UI LAYOUT
    # ==============================
    def build_ui(self):
        header = ctk.CTkLabel(
            self.frame,
            text="Compliance Logs (Audit Trail)",
            font=("Arial", 12)
        )
        header.pack(pady=10)

        # 🔍 Search + Export
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by user or action..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.load_logs
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="📥 Export Excel",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # ======================
        # 📊 TABLE (UPDATED)
        # ======================
        style = ttk.Style()

        style.configure(
            "Treeview",
            rowheight=28,
            font=("Arial", 12),
            foreground="black",          # ✅ Force black text
            fieldbackground="white"
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 12, "bold"),
            anchor="center"
        )

        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=("User", "Action", "Table", "Date"),
            show="headings"
        )

        for col in ("User", "Action", "Table", "Date"):
            self.tree.heading(col, text=col, anchor="center")   # ✅ Center header
            self.tree.column(col, width=160, anchor="center")   # ✅ Center cells

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 🎨 Row tag styles
        self.tree.tag_configure("danger", background="#ffe5e5", foreground="black")
        self.tree.tag_configure("info", background="#e1effe", foreground="black")

    # ==============================
    # 📥 LOAD LOGS
    # ==============================
    def load_logs(self):
        self.tree.delete(*self.tree.get_children())

        try:
            search = self.search_entry.get().strip()

            if search:
                query = """
                    SELECT l.*, u.name
                    FROM logs l
                    JOIN users u ON l.user_id = u.id
                    WHERE u.name LIKE %s OR l.action LIKE %s
                    ORDER BY l.id DESC
                """
                data = self.db.fetch_all(query, (f"%{search}%", f"%{search}%"))
            else:
                query = """
                    SELECT l.*, u.name
                    FROM logs l
                    JOIN users u ON l.user_id = u.id
                    ORDER BY l.id DESC
                """
                data = self.db.fetch_all(query)

            self.current_data = data or []

            for log in self.current_data:
                tag = "danger" if log["action"] == "DELETE" else "info"

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        log["name"],
                        log["action"],
                        log["table_name"],
                        self.format_date(log["created_at"])
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # 🗓 FORMAT DATE
    # ==============================
    def format_date(self, dt):
        try:
            if isinstance(dt, str):
                return dt
            return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(dt)

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "No system logs available")
                return

            df = pd.DataFrame([
                {
                    "Product": row.get("product_name"),
                    "IMEI": row.get("imei"),
                    "Colour": row.get("colour"),
                    "Quantity": row.get("quantity"),
                    "Sold By": row.get("sold_by"),
                    "Date": self.format_date(row.get("created_at"))
                }
                for row in self.all_data
            ])

            exporter = ExcelExporter("RetailMan_Reports.xlsx")
            exporter.export_sheet("System Logs", df)

            messagebox.showinfo(
                "Export Successful",
                "System Logs sheet updated in RetailMan_Reports.xlsx"
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ==============================
    # ▶ ENTRY POINT
    # ==============================
    def show(self):
        self.frame.pack(fill="both", expand=True)