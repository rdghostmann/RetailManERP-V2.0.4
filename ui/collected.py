#ui/collected.py
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd


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
            font=("Arial", 18)
        ).pack(pady=10)

        # ===== TOP BAR =====
        top = ctk.CTkFrame(self.frame)
        top.pack(fill="x", padx=10, pady=5)

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            top,
            textvariable=self.search_var,
            placeholder_text="🔍 Search collected devices..."
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

        # ===== TABLE =====
        self.tree = ttk.Treeview(
            self.frame,
            columns=(
                "ID",
                "Product",
                "Customer",
                "Contact",
                "Collector",
                "Collector Phone",
                "Description",
                "Date",
                "Status"
            ),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ==============================
    # LOAD DATA (OPTIMIZED)
    # ==============================
    def load_data(self):
        try:
            query = """
            SELECT 
                c.id,
                p.name AS product_name,
                c.customer_name,
                c.customer_contact,
                c.collected_by_name,
                c.collected_by_phone,
                c.description,
                c.created_at,
                c.status
            FROM collected c
            LEFT JOIN products p ON c.product_id = p.id
            ORDER BY c.created_at DESC
            """

            self.all_data = self.db.fetch_all(query)
            self.display_table(self.all_data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # DISPLAY TABLE
    # ==============================
    def display_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in data:
            self.tree.insert("", "end", values=(
                row["id"],
                row["product_name"] or "Unknown",
                row["customer_name"],
                row["customer_contact"],
                row["collected_by_name"],
                row["collected_by_phone"],
                row["description"],
                row["created_at"],
                row["status"]
            ))

    # ==============================
    # SEARCH
    # ==============================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower()

        filtered = [
            row for row in self.all_data
            if keyword in (row["product_name"] or "").lower()
            or keyword in row["customer_name"].lower()
            or keyword in row["customer_contact"].lower()
            or keyword in row["collected_by_name"].lower()
            or keyword in row["collected_by_phone"].lower()
            or keyword in (row["description"] or "").lower()
        ]

        self.display_table(filtered)

    # ==============================
    # EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            if not self.all_data:
                messagebox.showwarning("No Data", "Nothing to export")
                return

            formatted = []

            for row in self.all_data:
                formatted.append({
                    "Product": row["product_name"],
                    "Customer": row["customer_name"],
                    "Contact": row["customer_contact"],
                    "Collector": row["collected_by_name"],
                    "Collector Phone": row["collected_by_phone"],
                    "Description": row["description"],
                    "Date": row["created_at"],
                    "Status": row["status"]
                })

            df = pd.DataFrame(formatted)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel File"
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))