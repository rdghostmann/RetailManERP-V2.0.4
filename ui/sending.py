# ui/sending.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.sending_services import SendingService
from services.product_service import ProductService
import pandas as pd
from utils.excel_exporter import ExcelExporter
from PIL import Image
from utils.resource_path import resource_path


class SendingPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.sending_service = SendingService(db)
        self.product_service = ProductService(db)

        self.products = self.product_service.get_all()
        self.all_data = []

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
            font=("Arial", 12)
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

        self.desc_entry = ctk.CTkEntry(form, placeholder_text="Description (UI only)")
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
            text="Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # ======================
        # TABLE
        # ======================
        self.tree = ttk.Treeview(
            self.frame,
            columns=("BatchNo", "ID", "Product", "Customer", "Contact", "Date"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ==============================
    # DATA
    # ==============================
    def format_date(self, dt):
        if not dt:
            return "-"
        try:
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return str(dt)

    def load_table(self):
        self.all_data = self.sending_service.get_all() or []
        self.display_table(self.all_data)

    def display_table(self, data):
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", "end", values=(
                row.get("batch_no"),
                row.get("id"),
                row.get("product_name", "Unknown"),
                row.get("customer_name"),
                row.get("customer_contact"),
                self.format_date(row.get("created_at"))
            ))

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
    # COLLECT
    # ==============================
    def open_collect_dialog(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Select", "Select a record first")
            return

        values = self.tree.item(selected[0])["values"]
        sending_id = values[1]

        dialog = ctk.CTkToplevel(self.frame)
        dialog.title("Collect")

        name = ctk.CTkEntry(dialog, placeholder_text="Collector Name")
        name.pack(pady=10)

        phone = ctk.CTkEntry(dialog, placeholder_text="Collector Phone")
        phone.pack(pady=10)

        def save():
            try:
                self.sending_service.mark_as_collected(
                    self.user["id"],
                    sending_id,
                    name.get().strip(),
                    phone.get().strip()
                )

                messagebox.showinfo("Success", "Collected")
                dialog.destroy()
                self.load_table()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    # ==============================
    # EXPORT
    # ==============================
    def export_to_excel(self):
        if not self.all_data:
            messagebox.showwarning("No Data", "No data available")
            return

        df = pd.DataFrame([
            {
                "BatchNo": r.get("batch_no"),
                "Product": r.get("product_name"),
                "Customer": r.get("customer_name"),
                "Contact": r.get("customer_contact"),
                "Date": self.format_date(r.get("created_at"))
            }
            for r in self.all_data
        ])

        ExcelExporter("RetailMan_Reports.xlsx").export_sheet("Sending", df)

        messagebox.showinfo("Success", "Export completed")