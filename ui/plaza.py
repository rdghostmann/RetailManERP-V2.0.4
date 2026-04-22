import customtkinter as ctk
from tkinter import ttk, messagebox

from services.plaza_services import PlazaService
from services.product_service import ProductService
from utils.validators import Validators


class PlazaPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.plaza_service = PlazaService(db)
        self.product_service = ProductService(db)

        self.fetched_product = None
        self.available_colours = []
        self.quantity = 1  # Default quantity

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    def build_ui(self):
        # Form for sale entry
        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        # IMEI input
        self.imei_entry = ctk.CTkEntry(form, placeholder_text="Enter Product IMEI")
        self.imei_entry.pack(side="left", padx=5)
        self.imei_entry.bind("<KeyRelease>", lambda e: self.lookup_product())

        # Product info display
        self.product_info_label = ctk.CTkLabel(form, text="No product selected", text_color="gray")
        self.product_info_label.pack(side="left", padx=5)

        # Colour dropdown (from available colours in stock)
        self.colour_var = ctk.StringVar()
        self.colour_dropdown = ctk.CTkComboBox(
            form,
            variable=self.colour_var,
            values=[]
        )
        self.colour_dropdown.pack(side="left", padx=5)

        # Customer details
        self.customer_name = ctk.CTkEntry(form, placeholder_text="Customer Name")
        self.customer_name.pack(side="left", padx=5)
        
        self.customer_phone = ctk.CTkEntry(form, placeholder_text="Phone")
        self.customer_phone.pack(side="left", padx=5)

        # Record Sale button
        ctk.CTkButton(form, text="Record Sale", command=self.record_sale).pack(side="left", padx=5)

        # Table to display sales
        self.tree = ttk.Treeview(self.frame, columns=("Product", "IMEI", "Colour", "Qty", "Customer", "Phone"), show="headings")
        for col in ("Product", "IMEI", "Colour", "Qty", "Customer", "Phone"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def lookup_product(self):
        """Fetch product details by IMEI and available colours"""
        imei = self.imei_entry.get().strip()
        
        if not imei:
            self.fetched_product = None
            self.available_colours = []
            self.colour_dropdown.configure(values=[])
            self.colour_var.set("")
            self.product_info_label.configure(text="No product selected", text_color="gray")
            return

        try:
            product = self.product_service.get_by_imei(imei)
            
            if not product:
                self.fetched_product = None
                self.available_colours = []
                self.colour_dropdown.configure(values=[])
                self.colour_var.set("")
                self.product_info_label.configure(text="IMEI not found", text_color="red")
                return

            # Fetch all available colours for this IMEI from stock
            stock_records = self.db.fetch_all(
                "SELECT DISTINCT colour FROM stock WHERE imei=%s AND quantity > 0",
                (imei,)
            )
            
            self.available_colours = [s["colour"] for s in stock_records]
            
            if not self.available_colours:
                self.fetched_product = None
                self.colour_dropdown.configure(values=[])
                self.colour_var.set("")
                self.product_info_label.configure(text="No stock available", text_color="red")
                return

            self.fetched_product = product
            self.colour_dropdown.configure(values=self.available_colours)
            self.colour_var.set(self.available_colours[0])  # Set first colour as default
            
            product_text = f"{product['name']} ({product['brand']}) - Available Colours: {', '.join(self.available_colours)}"
            self.product_info_label.configure(text=product_text, text_color="green")

        except Exception as e:
            self.fetched_product = None
            self.available_colours = []
            self.colour_dropdown.configure(values=[])
            self.colour_var.set("")
            self.product_info_label.configure(text=f"Error: {str(e)}", text_color="red")

    def record_sale(self):
        try:
            if not self.fetched_product:
                raise ValueError("Please enter a valid product IMEI")

            colour = self.colour_var.get().strip()
            if not colour:
                raise ValueError("Please select a colour")

            # Verify colour is in available colours
            if colour not in self.available_colours:
                raise ValueError(f"Colour '{colour}' is not available for this IMEI")

            if not self.customer_name.get().strip():
                raise ValueError("Customer name is required")

            if not self.customer_phone.get().strip():
                raise ValueError("Customer phone is required")

            imei = self.imei_entry.get().strip()
            qty = self.quantity

            Validators.validate_phone(self.customer_phone.get())

            # Check stock for this specific IMEI and COLOUR
            stock = self.db.fetch_one(
                "SELECT quantity FROM stock WHERE imei=%s AND colour=%s",
                (imei, colour)
            )

            if not stock or stock["quantity"] < qty:
                raise ValueError(f"Insufficient stock for {colour}")

            # Deduct stock
            self.db.execute(
                "UPDATE stock SET quantity = quantity - %s WHERE imei=%s AND colour=%s",
                (qty, imei, colour)
            )

            self.plaza_service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                imei,
                colour,
                qty,
                self.customer_name.get().strip(),
                self.customer_phone.get().strip()
            )

            messagebox.showinfo("Success", "Sale recorded successfully")
            
            # Clear form
            self.imei_entry.delete(0, "end")
            self.colour_var.set("")
            self.customer_name.delete(0, "end")
            self.customer_phone.delete(0, "end")
            self.colour_dropdown.configure(values=[])
            self.fetched_product = None
            self.available_colours = []
            self.product_info_label.configure(text="No product selected", text_color="gray")
            
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = self.plaza_service.get_all()

        for row in data:
            # Fetch product name for display
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )
            product_name = product["name"] if product else "Unknown"
            
            self.tree.insert("", "end", values=(
                product_name,
                row["imei"],
                row["colour"],
                row["quantity"],
                row["customer_name"],
                row["customer_phone"]
            ))