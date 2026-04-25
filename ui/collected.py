#ui/collected.py
import customtkinter as ctk
from tkinter import ttk

class CollectedPage:
    def __init__(self, root, db, user):
        self.db = db
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.frame,
            text="Collected Devices",
            font=("Arial", 18)
        ).pack(pady=10)

        self.tree = ttk.Treeview(
            self.frame,
            columns=(
                "Product", "Customer", "Contact",
                "Collector", "Collector Phone",
                "Description", "Date"
            ),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_data()

    def load_data(self):
        data = self.db.fetch_all("SELECT * FROM collected")

        for row in data:
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )

            self.tree.insert("", "end", values=(
                product["name"] if product else "Unknown",
                row["customer_name"],
                row["customer_contact"],
                row["collected_by_name"],
                row["collected_by_phone"],
                row["description"],
                row["created_at"]
            ))