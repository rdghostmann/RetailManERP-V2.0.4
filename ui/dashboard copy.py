# ui/dashboard.py
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

from ui.logs import LogsPage
from ui.prduct_catalogue import ProductCataloguePage
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.stock_service import StockService
from services.plaza_services import PlazaService
from services.sending_services import SendingService
from services.returns_services import ReturnsService
from app.config import InventoryConfig, UIConfig
from utils.theme_manager import theme_manager

from ui.stock import StockPage
from ui.plaza import PlazaPage
from ui.returns import ReturnsPage
from ui.sending import SendingPage
from ui.user import UserPage

from PIL import Image


class Dashboard:
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.active_tab = "dashboard"

        self.stock_service = StockService(db)
        self.plaza_service = PlazaService(db)
        self.sending_service = SendingService(db)
        self.returns_service = ReturnsService(db)

        ctk.set_appearance_mode("dark" if theme_manager.is_dark() else "light")

        self.root = ctk.CTk()
        self.root.title("RetailMan ERP V.2.0.1")
        self.root.geometry(f"{UIConfig.WINDOW_WIDTH}x{UIConfig.WINDOW_HEIGHT}")

        # ICONS
        self.icons = {
            "dashboard": ctk.CTkImage(Image.open("public/dashboard.png"), size=(20, 20)),
            "stock": ctk.CTkImage(Image.open("public/in-stock.png"), size=(20, 20)),
            "sending": ctk.CTkImage(Image.open("public/sending.png"), size=(20, 20)),
            "plaza": ctk.CTkImage(Image.open("public/plaza.png"), size=(20, 20)),
            "returns": ctk.CTkImage(Image.open("public/return-box.png"), size=(20, 20)),
            "logs": ctk.CTkImage(Image.open("public/log-format.png"), size=(20, 20)),
            "users": ctk.CTkImage(Image.open("public/users.png"), size=(20, 20)),
            "products": ctk.CTkImage(Image.open("public/product-catalog.png"), size=(20, 20)),
            "logout": ctk.CTkImage(Image.open("public/check-out.png"), size=(20, 20)),

            # KPI ICONS
            "total-stock": ctk.CTkImage(Image.open("public/total-stock.png"), size=(28, 28)),
            "sales": ctk.CTkImage(Image.open("public/sales.png"), size=(28, 28)),
            "dispatch": ctk.CTkImage(Image.open("public/dispatch.png"), size=(28, 28)),
            "returns_kpi": ctk.CTkImage(Image.open("public/returns.png"), size=(28, 28)),
        }

        self.build_layout()
        self.load_dashboard_data()

    # ==============================
    # 🧱 LAYOUT
    # ==============================

    def build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = ctk.CTkFrame(self.root)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.build_sidebar()
        self.build_dashboard_home()

    # ==============================
    # 📚 SIDEBAR
    # ==============================

    def create_sidebar_button(self, text, icon, command, tab_name):
        is_active = self.active_tab == tab_name

        return ctk.CTkButton(
            self.sidebar,
            text=f"  {text}",
            image=icon,
            compound="left",
            command=lambda: self.set_active_tab(tab_name, command),
            fg_color="#1E293B" if is_active else "transparent",
            text_color="white" if is_active else "#A0AEC0",
            hover_color="#334155",
            anchor="w",
            corner_radius=8,
            height=40
        )

    def set_active_tab(self, tab_name, callback):
        self.active_tab = tab_name
        self.refresh_sidebar()
        callback()

    def refresh_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self.build_sidebar()

    def build_sidebar(self):
        header = ctk.CTkFrame(self.sidebar)
        header.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(header, text="RetailMan", font=("Arial", 18)).pack()
        ctk.CTkLabel(header, text=f"Role: {self.user['role'].title()}",
                     font=("Arial", 10), text_color="gray").pack()

        self.create_sidebar_button("Dashboard", self.icons["dashboard"], self.show_dashboard, "dashboard").pack(fill="x", padx=10, pady=5)
        self.create_sidebar_button("Stock", self.icons["stock"], self.open_stock, "stock").pack(fill="x", padx=10, pady=5)
        self.create_sidebar_button("Sending", self.icons["sending"], self.open_sending, "sending").pack(fill="x", padx=10, pady=5)
        self.create_sidebar_button("Plaza", self.icons["plaza"], self.open_plaza, "plaza").pack(fill="x", padx=10, pady=5)
        self.create_sidebar_button("Returns", self.icons["returns"], self.open_returns, "returns").pack(fill="x", padx=10, pady=5)

        if self.user["role"] == "admin":
            self.create_sidebar_button("Logs", self.icons["logs"], self.open_logs, "logs").pack(fill="x", padx=10, pady=5)
            self.create_sidebar_button("Users", self.icons["users"], self.open_users, "users").pack(fill="x", padx=10, pady=5)
            self.create_sidebar_button("Products", self.icons["products"], self.product_catalogue, "products").pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="🌙 / ☀ Theme",
                      fg_color="transparent", text_color="gray",
                      hover_color="#003F7D",
                      command=self.toggle_theme).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="🔓 Logout",
                      fg_color="red", command=self.logout).pack(fill="x", padx=10, pady=20)

    # ==============================
    # 🏠 DASHBOARD VIEW
    # ==============================

    def build_dashboard_home(self):
        self.clear_content()

        ctk.CTkLabel(self.content,
                     text=f"Welcome, {self.user['name']} ({self.user['role'].title()})",
                     font=("Arial", 20)).pack(pady=10)

        # KPI
        self.kpi_frame = ctk.CTkFrame(self.content)
        self.kpi_frame.pack(fill="x", padx=10, pady=10)

        self.stock_card = self.create_card(self.kpi_frame, "Total Stock", "0", self.icons["total-stock"])
        self.sales_card = self.create_card(self.kpi_frame, "Sales", "0", self.icons["sales"])
        self.sending_card = self.create_card(self.kpi_frame, "Dispatch", "0", self.icons["dispatch"])
        self.returns_card = self.create_card(self.kpi_frame, "Returns", "0", self.icons["returns_kpi"])

        # Alerts
        self.alert_frame = ctk.CTkFrame(self.content)
        self.alert_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.alert_frame, text="⚠️ Alerts", font=("Arial", 16)).pack(anchor="w", padx=10)

        self.alert_list = ctk.CTkTextbox(self.alert_frame, height=120)
        self.alert_list.pack(fill="x", padx=10, pady=5)

        # Table
        self.inventory_frame = ctk.CTkFrame(self.content)
        self.inventory_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.inventory_frame, text="📦 Inventory Overview",
                     font=("Arial", 16)).pack(anchor="w", padx=10)

        self.inventory_table = ttk.Treeview(
            self.inventory_frame,
            columns=("Name", "Brand", "Description", "Colour", "Qty", "Created"),
            show="headings"
        )

        for col in ("Name", "Brand", "Description", "Colour", "Qty", "Created"):
            self.inventory_table.heading(col, text=col)

        self.inventory_table.pack(fill="both", expand=True, padx=10, pady=10)

    # ==============================
    # 🧮 KPI CARD (UPDATED)
    # ==============================

    def create_card(self, parent, title, value, icon):
        card = ctk.CTkFrame(parent, width=180, height=90, corner_radius=12)
        card.pack(side="left", padx=10, pady=10)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(top, image=icon, text="").pack(side="left")

        ctk.CTkLabel(top, text=title, text_color="#94A3B8").pack(side="left", padx=8)

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 22, "bold")
        )
        value_label.pack(anchor="w", padx=15, pady=(5, 10))

        return value_label

    # ==============================
    # 📊 DATA
    # ==============================

    def load_dashboard_data(self):
        try:
            stock_data = self.stock_service.get_all_stock()
            aggregated_stock = self.stock_service.get_aggregated_stock()

            total_stock = sum(row["quantity"] for row in stock_data)

            sales_data = self.plaza_service.get_all()
            sending_data = self.sending_service.get_all()
            returns_data = self.returns_service.get_all()

            self.stock_card.configure(text=str(total_stock))
            self.sales_card.configure(text=str(len(sales_data)))
            self.sending_card.configure(text=str(len(sending_data)))
            self.returns_card.configure(text=str(len(returns_data)))

            self.alert_list.delete("0.0", "end")

            for row in aggregated_stock:
                if row["total_quantity"] < InventoryConfig.LOW_STOCK_THRESHOLD:
                    self.alert_list.insert(
                        "end",
                        f"{row['name']} ({row['colour']}) LOW: {row['total_quantity']}\n"
                    )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # NAVIGATION
    # ==============================

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.set_active_tab("dashboard", lambda: None)
        self.build_dashboard_home()
        self.load_dashboard_data()

    def open_stock(self):
        self.set_active_tab("stock", lambda: None)
        self.clear_content()
        StockPage(self.content, self.db, self.user)

    def open_plaza(self):
        self.set_active_tab("plaza", lambda: None)
        self.clear_content()
        PlazaPage(self.content, self.db, self.user)

    def open_sending(self):
        self.set_active_tab("sending", lambda: None)
        self.clear_content()
        SendingPage(self.content, self.db, self.user)

    def open_returns(self):
        self.set_active_tab("returns", lambda: None)
        self.clear_content()
        ReturnsPage(self.content, self.db, self.user)

    def open_logs(self):
        self.set_active_tab("logs", lambda: None)
        self.clear_content()
        LogsPage(self.content, self.db, self.user)

    def open_users(self):
        self.set_active_tab("users", lambda: None)
        self.clear_content()
        UserPage(self.content, self.db, self.user)

    def product_catalogue(self):
        self.set_active_tab("products", lambda: None)
        self.clear_content()
        ProductCataloguePage(self.content, self.db, self.user)

    def toggle_theme(self):
        theme_manager.toggle_theme()
        ctk.set_appearance_mode("dark" if theme_manager.is_dark() else "light")
        self.refresh_sidebar()

    def logout(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()