# ui/premises.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.premises_service import PremisesService
from services.product_service import ProductService


class PremisesPage:
    def __init__(self, root, db, user):
        self.root = root
        self.db = db
        self.user = user

        self.service = PremisesService(db)
        self.product_service = ProductService(db)

        # 🔎 STATE
        self.fetched_product = None
        self.selected_colour = None

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(fill="both", expand=True)

        self.build_ui()
        self.load_table()

    # =========================
    # UI
    # =========================
    def build_ui(self):
        ctk.CTkLabel(
            self.frame,
            text="Premises Sales",
            font=("Arial", 18)
        ).pack(pady=10)

        form = ctk.CTkFrame(self.frame)
        form.pack(fill="x", padx=10, pady=10)

        # IMEI INPUT
        self.imei = ctk.CTkEntry(form, placeholder_text="Enter IMEI")
        self.imei.pack(side="left", padx=5)
        self.imei.bind("<KeyRelease>", lambda e: self.lookup_product())

        # PRODUCT INFO
        self.product_label = ctk.CTkLabel(
            form,
            text="No product selected",
            text_color="gray"
        )
        self.product_label.pack(side="left", padx=5)

        # COLOUR DROPDOWN
        self.colour_var = ctk.StringVar()
        self.colour_dropdown = ctk.CTkComboBox(
            form,
            variable=self.colour_var,
            values=[]
        )
        self.colour_dropdown.pack(side="left", padx=5)

        # CUSTOMER INPUTS
        self.customer = ctk.CTkEntry(form, placeholder_text="Customer")
        self.customer.pack(side="left", padx=5)

        self.phone = ctk.CTkEntry(form, placeholder_text="Phone")
        self.phone.pack(side="left", padx=5)

        # ACTION BUTTON
        ctk.CTkButton(
            form,
            text="Sell",
            command=self.sell
        ).pack(side="left", padx=5)

        # ======================
        # TABLE
        # ======================
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Product", "IMEI", "Colour", "Customer", "Phone"),
            show="headings"
        )

        for col in ("Product", "IMEI", "Colour", "Customer", "Phone"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================
    # IMEI LOOKUP
    # =========================
    def lookup_product(self):
        imei = self.imei.get().strip()

        if not imei:
            self.reset_lookup()
            return

        try:
            product = self.product_service.get_by_imei(imei)

            if not product:
                self.product_label.configure(
                    text="IMEI not found",
                    text_color="red"
                )
                return

            # 🔎 FETCH AVAILABLE COLOURS FROM STOCK
            stock = self.db.fetch_all(
                "SELECT colour FROM stock WHERE product_id=%s AND quantity > 0",
                (product["id"],)
            )

            colours = list({s["colour"] for s in stock})

            if not colours:
                self.product_label.configure(
                    text="Out of stock",
                    text_color="red"
                )
                return

            self.fetched_product = product

            self.colour_dropdown.configure(values=colours)
            self.colour_var.set(colours[0])

            self.product_label.configure(
                text=f"{product['name']} ({product['brand']})",
                text_color="green"
            )

        except Exception as e:
            self.product_label.configure(text=str(e), text_color="red")

    def reset_lookup(self):
        self.fetched_product = None
        self.colour_dropdown.configure(values=[])
        self.colour_var.set("")
        self.product_label.configure(
            text="No product selected",
            text_color="gray"
        )

    # =========================
    # SELL
    # =========================
    def sell(self):
        try:
            if not self.fetched_product:
                raise ValueError("Invalid IMEI")

            customer = self.customer.get().strip()
            phone = self.phone.get().strip()
            colour = self.colour_var.get()

            if not customer:
                raise ValueError("Customer name required")

            self.service.record_sale(
                self.user["id"],
                self.fetched_product["id"],
                self.imei.get().strip(),
                colour,
                1,
                customer,
                phone
            )

            messagebox.showinfo("Success", "Sale recorded")

            # RESET
            self.imei.delete(0, "end")
            self.customer.delete(0, "end")
            self.phone.delete(0, "end")

            self.reset_lookup()
            self.load_table()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================
    # TABLE
    # =========================
    def load_table(self):
        self.tree.delete(*self.tree.get_children())

        for row in self.service.get_all():
            product = self.db.fetch_one(
                "SELECT name FROM products WHERE id=%s",
                (row["product_id"],)
            )

            self.tree.insert("", "end", values=(
                product["name"] if product else "Unknown",
                row["imei"],
                row["colour"],
                row["customer_name"],
                row["customer_phone"]
            ))