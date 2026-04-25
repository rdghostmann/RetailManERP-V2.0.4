# ui/sending.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from services.sending_services import SendingService
from services.product_service import ProductService
from utils.validators import Validators
import pandas as pd
from PIL import Image
from utils.resource_path import resource_path
from datetime import datetime


class SendingPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.sending_service = SendingService(db)
        self.product_service = ProductService(db)

        self.products = self.product_service.get_all()

        self.export_icon = ctk.CTkImage(
            Image.open(resource_path("public/export-xlsx.png")),
            size=(20, 20)
        )

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    # ==============================
    # UI
    # ==============================
    def build_ui(self):

        ctk.CTkLabel(
            self.frame,
            text="Dispatch Management",
            font=("Arial", 16)
        ).pack(pady=10)

        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        self.product_var = ctk.StringVar()

        self.product_dropdown = ctk.CTkComboBox(
            form,
            values=[p["name"] for p in self.products],
            variable=self.product_var
        )
        self.product_dropdown.pack(side="left", padx=5)

        self.customer_name_entry = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_name_entry.pack(side="left", padx=5)

        self.contact_entry = ctk.CTkEntry(form, placeholder_text="Customer Contact")
        self.contact_entry.pack(side="left", padx=5)

        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Description")
        self.desc_entry.pack(side="left", padx=5)

        ctk.CTkButton(form, text="Dispatch", command=self.dispatch).pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text="Mark as Collected",
            fg_color="#F59E0B",
            command=self.open_collect_dialog
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # ======================
        # TABLE (CENTER ALIGNED)
        # ======================
        style = ttk.Style()

        # Base styling
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

        # Selection styling (optional but recommended)
        style.map(
            "Treeview",
            background=[("selected", "#1f538d")],
            foreground=[("selected", "white")]
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Product", "Customer", "Contact", "Description", "Date"),
            show="headings"
        )

        for col in ("ID", "Product", "Customer", "Contact", "Description", "Date"):
            self.tree.heading(col, text=col, anchor="center")   # ✅ Center header text
            self.tree.column(col, width=140, anchor="center")   # ✅ Center cell values

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ======================
        # SEARCH
        # ======================
        search_frame = ctk.CTkFrame(self.frame)
        search_frame.pack(fill="x", padx=10)

        self.search_var = ctk.StringVar()

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search dispatch..."
        )
        search_entry.pack(fill="x", padx=5)
        search_entry.bind("<KeyRelease>", self.filter_table)

    # ==============================
    # DISPATCH
    # ==============================
    def dispatch(self):
        try:
            product = next(p for p in self.products if p["name"] == self.product_var.get())

            self.sending_service.create_dispatch(
                self.user["id"],
                product["id"],
                self.customer_name_entry.get().strip(),
                self.contact_entry.get().strip(),
                self.desc_entry.get().strip()
            )

            messagebox.showinfo("Success", "Dispatch recorded")

            self.customer_name_entry.delete(0, "end")
            self.contact_entry.delete(0, "end")
            self.desc_entry.delete(0, "end")

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # TABLE
    # ==============================
    def load_table(self):
        self.all_data = self.sending_service.get_all()
        self.display_table(self.all_data)

    def format_date(self, dt):
        if not dt:
            return "-"
        return dt.strftime("%Y-%m-%d %H:%M")

    def display_table(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in data:
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )

            product_name = product["name"] if product else "Unknown"

            self.tree.insert("", "end", values=(
                row["id"],
                product_name,
                row["customer_name"],
                row["customer_contact"],
                row["description"],
                self.format_date(row.get("created_at"))
            ))

    # ==============================
    # SEARCH
    # ==============================
    def filter_table(self, event=None):
        keyword = self.search_var.get().lower()

        filtered = [
            row for row in self.all_data
            if keyword in row["customer_name"].lower()
            or keyword in row["customer_contact"].lower()
            or keyword in (row["description"] or "").lower()
        ]

        self.display_table(filtered)

    # ==============================
    # COLLECT FLOW
    # ==============================
    def open_collect_dialog(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Select", "Select a record first")
            return

        values = self.tree.item(selected[0])["values"]
        sending_id = values[0]

        dialog = ctk.CTkToplevel(self.frame)
        dialog.title("Mark as Collected")

        name_entry = ctk.CTkEntry(dialog, placeholder_text="Collector Name")
        name_entry.pack(pady=10)

        phone_entry = ctk.CTkEntry(dialog, placeholder_text="Collector Phone")
        phone_entry.pack(pady=10)

        def save():
            try:
                if not messagebox.askyesno("Confirm", "Mark as collected?"):
                    return

                self.sending_service.mark_as_collected(
                    self.user["id"],
                    sending_id,
                    name_entry.get().strip(),
                    phone_entry.get().strip()
                )

                messagebox.showinfo("Success", "Marked as collected")

                dialog.destroy()
                self.load_table()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    # ==============================
    # EXPORT
    # ==============================
    def export_to_excel(self):
        try:
            data = self.sending_service.get_all()

            if not data:
                messagebox.showwarning("No Data", "No data to export")
                return

            formatted = []

            for row in data:
                product = self.db.fetch_one(
                    "SELECT name FROM products WHERE id=%s",
                    (row["product_id"],)
                )

                formatted.append({
                    "Product": product["name"] if product else "Unknown",
                    "Customer": row["customer_name"],
                    "Contact": row["customer_contact"],
                    "Description": row["description"],
                    "Date": self.format_date(row.get("created_at"))
                })

            df = pd.DataFrame(formatted)

            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")

            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Exported")

        except Exception as e:
            messagebox.showerror("Error", str(e))