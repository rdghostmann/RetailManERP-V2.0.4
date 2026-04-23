# ui/returns.py
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from PIL import Image

from services.returns_services import ReturnsService
from services.product_service import ProductService
from utils.validators import Validators


class ReturnsPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.returns_service = ReturnsService(db)
        self.product_service = ProductService(db)

        self.fetched_sale = None

        # ✅ Load export icon
        self.export_icon = ctk.CTkImage(
            Image.open("public/export-xlsx.png"),
            size=(18, 18)
        )

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        # Form
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        # IMEI input
        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_sale())

        # Sale info
        self.sale_info_label = ctk.CTkLabel(form, text="No sale found", text_color="gray")
        self.sale_info_label.pack(side="left", padx=5)

        # 🔒 Fixed quantity = 1
        self.return_qty_entry = ctk.CTkEntry(form, width=80)
        self.return_qty_entry.insert(0, "1")
        self.return_qty_entry.configure(state="disabled")
        self.return_qty_entry.pack(side="left", padx=5)

        # Reason
        self.reason_entry = ctk.CTkEntry(form, placeholder_text="Reason for return")
        self.reason_entry.pack(side="left", padx=5)

        # Record button
        ctk.CTkButton(
            form,
            text="Record Return",
            command=self.record_return
        ).pack(side="left", padx=5)

        # ✅ Export Button with Image
        ctk.CTkButton(
            form,
            text=" Export Excel",
            image=self.export_icon,
            compound="left",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.export_to_excel
        ).pack(side="left", padx=5)

        # Table
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Customer", "Returned Qty", "Reason"),
            show="headings"
        )

        for col in ("Product", "IMEI", "Colour", "Customer", "Returned Qty", "Reason"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

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
            sale_text = f"{sale['product_name']} | {sale['colour']} | {sale['customer_name']} | Qty: {sale['quantity']}"
            self.sale_info_label.configure(text=sale_text, text_color="green")

        except Exception as e:
            self.fetched_sale = None
            self.sale_info_label.configure(text=f"Error: {str(e)}", text_color="red")

    def record_return(self):
        try:
            if not self.fetched_sale:
                raise ValueError("Please enter a valid product IMEI")

            return_qty = 1
            Validators.validate_quantity(return_qty)

            self.returns_service.create_return(
                self.user["id"],
                self.fetched_sale["id"],
                return_qty,
                self.reason_entry.get().strip()
            )

            messagebox.showinfo("Success", "Return recorded successfully")

            # Reset form
            self.imei_entry.delete(0, "end")
            self.reason_entry.delete(0, "end")
            self.fetched_sale = None
            self.sale_info_label.configure(text="No sale found", text_color="gray")

            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.returns_service.get_all()

        for row in data:
            self.tree.insert("", "end", values=(
                row["product_name"],
                row["imei"],
                row["colour"],
                row["customer_name"],
                row["quantity"],
                row["reason"]
            ))

    # ==============================
    # 📤 EXPORT TO EXCEL
    # ==============================
    def export_to_excel(self):
        try:
            data = self.returns_service.get_all()

            if not data:
                messagebox.showwarning("No Data", "No return data to export")
                return

            df = pd.DataFrame(data)

            # Clean column names
            df = df.rename(columns={
                "product_name": "Product",
                "imei": "IMEI",
                "colour": "Colour",
                "customer_name": "Customer",
                "quantity": "Returned Qty",
                "reason": "Reason"
            })

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Excel File"
            )

            if not file_path:
                return

            df.to_excel(file_path, index=False)

            messagebox.showinfo("Success", "Returns exported successfully")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))