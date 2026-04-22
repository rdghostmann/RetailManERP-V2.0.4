import customtkinter as ctk
from tkinter import ttk, messagebox

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

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        # Form for return entry
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        # IMEI input
        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_sale())

        # Sale info display
        self.sale_info_label = ctk.CTkLabel(form, text="No sale found", text_color="gray")
        self.sale_info_label.pack(side="left", padx=5)

        # Return quantity
        self.return_qty_entry = ctk.CTkEntry(form, placeholder_text="Return Qty")
        self.return_qty_entry.pack(side="left", padx=5)

        # Reason
        self.reason_entry = ctk.CTkEntry(form, placeholder_text="Reason for return")
        self.reason_entry.pack(side="left", padx=5)

        # Record Return button
        ctk.CTkButton(form, text="Record Return", command=self.record_return).pack(side="left", padx=5)

        # Table to display returns
        self.tree = ttk.Treeview(self.frame, columns=("Product", "IMEI", "Colour", "Customer", "Returned Qty", "Reason"), show="headings")
        for col in ("Product", "IMEI", "Colour", "Customer", "Returned Qty", "Reason"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def lookup_sale(self):
        """Fetch plaza sale details by IMEI"""
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

            return_qty_str = self.return_qty_entry.get().strip()
            if not return_qty_str:
                raise ValueError("Return quantity is required")

            return_qty = int(return_qty_str)
            Validators.validate_quantity(return_qty)

            self.returns_service.create_return(
                self.user["id"],
                self.fetched_sale["id"],
                return_qty,
                self.reason_entry.get().strip()
            )

            messagebox.showinfo("Success", "Return recorded successfully")
            
            # Clear form
            self.imei_entry.delete(0, "end")
            self.return_qty_entry.delete(0, "end")
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