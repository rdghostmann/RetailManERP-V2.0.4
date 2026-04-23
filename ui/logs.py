# ui/logs.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

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
            font=("Arial", 18)
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

        # 📊 Logs Table (Record ID removed)
        self.tree = ttk.Treeview(
            self.frame,
            columns=("User", "Action", "Table", "Date"),
            show="headings"
        )

        for col in ("User", "Action", "Table", "Date"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # 🎨 Styling
        self.tree.tag_configure("danger", background="#ffe5e5")
        self.tree.tag_configure("info", background="#e1effe")

    # ==============================
    # 📥 LOAD LOGS
    # ==============================
    def load_logs(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

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

            self.current_data = data  # store for export

            for log in data:
                tag = "danger" if log["action"] == "DELETE" else "info"

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        log["name"],
                        log["action"],
                        log["table_name"],
                        log["created_at"]
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            if not hasattr(self, "current_data") or not self.current_data:
                messagebox.showwarning("No Data", "No logs available to export")
                return

            df = pd.DataFrame(self.current_data)

            # Clean columns
            df = df.rename(columns={
                "name": "User",
                "action": "Action",
                "table_name": "Table",
                "created_at": "Date"
            })[["User", "Action", "Table", "Date"]]

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Logs File"
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Logs exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ==============================
    # ▶ ENTRY POINT
    # ==============================
    def show(self):
        self.frame.pack(fill="both", expand=True)