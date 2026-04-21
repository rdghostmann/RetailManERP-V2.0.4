import customtkinter as ctk
from tkinter import messagebox
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from services.stock_service import StockService
from services.plaza_services import PlazaService
from services.sending_services import SendingService
from services.returns_services import ReturnsService
from app.config import InventoryConfig, UIConfig

from ui.stock import StockPage
from ui.plaza import PlazaPage
from ui.returns import ReturnsPage
from ui.sending import SendingPage

class Dashboard:
    def __init__(self, db, user):
        self.db = db
        self.user = user

        self.stock_service = StockService(db)
        self.plaza_service = PlazaService(db)
        self.sending_service = SendingService(db)
        self.returns_service = ReturnsService(db)

        self.root = ctk.CTk()
        self.root.title("RetailMan Dashboard")
        self.root.geometry(f"{UIConfig.WINDOW_WIDTH}x{UIConfig.WINDOW_HEIGHT}")

        self.build_layout()
        self.load_dashboard_data()

    # ==============================
    # 🧱 LAYOUT
    # ==============================

    def build_layout(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        # Content
        self.content = ctk.CTkFrame(self.root)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.build_sidebar()
        self.build_dashboard_home()

    # ==============================
    # 📚 SIDEBAR
    # ==============================

    def build_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="RetailMan", font=("Arial", 18)).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="Stock", command=self.open_stock).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="Sending", command=self.open_sending).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="Plaza", command=self.open_plaza).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.sidebar, text="Returns", command=self.open_returns).pack(fill="x", padx=10, pady=5)

        if self.user["role"] == "admin":
            ctk.CTkButton(self.sidebar, text="Logs", command=self.not_implemented).pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="red", command=self.logout).pack(fill="x", padx=10, pady=20)

    # ==============================
    # 🏠 DASHBOARD VIEW
    # ==============================

    def build_dashboard_home(self):
        self.clear_content()

        self.header = ctk.CTkLabel(
            self.content,
            text=f"Welcome, {self.user['name']}",
            font=("Arial", 20)
        )
        self.header.pack(pady=10)

        # KPI Container
        self.kpi_frame = ctk.CTkFrame(self.content)
        self.kpi_frame.pack(fill="x", padx=10, pady=10)

        self.stock_card = self.create_card(self.kpi_frame, "Total Stock", "0")
        self.sales_card = self.create_card(self.kpi_frame, "Total Sales", "0")
        self.sending_card = self.create_card(self.kpi_frame, "Dispatch", "0")
        self.returns_card = self.create_card(self.kpi_frame, "Returns", "0")

        # Alerts Section
        self.alert_frame = ctk.CTkFrame(self.content)
        self.alert_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.alert_frame, text="⚠ Critical Alerts", font=("Arial", 16)).pack(anchor="w", padx=10, pady=10)

        self.alert_list = ctk.CTkTextbox(self.alert_frame, height=200)
        self.alert_list.pack(fill="both", expand=True, padx=10, pady=10)

    # ==============================
    # 🧮 KPI CARD
    # ==============================

    def create_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, width=150, height=80)
        card.pack(side="left", padx=10, pady=10)

        label = ctk.CTkLabel(card, text=title)
        label.pack()

        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 18))
        value_label.pack()

        return value_label

    # ==============================
    # 📊 DATA LOADING
    # ==============================

    def load_dashboard_data(self):
        try:
            stock_data = self.stock_service.get_aggregated_stock()
            total_stock = sum([row["total_quantity"] for row in stock_data])

            sales_data = self.plaza_service.get_all()
            sending_data = []
            try:
                sending_data = self.sending_service.get_all()
            except Exception:
                pass
            
            returns_data = []
            try:
                returns_data = self.returns_service.get_all()
            except Exception:
                pass

            self.stock_card.configure(text=str(total_stock))
            self.sales_card.configure(text=str(len(sales_data)))
            self.sending_card.configure(text=str(len(sending_data)))
            self.returns_card.configure(text=str(len(returns_data)))

            # Alerts
            self.alert_list.delete("0.0", "end")

            for row in stock_data:
                if row["total_quantity"] < InventoryConfig.LOW_STOCK_THRESHOLD:
                    self.alert_list.insert(
                        "end",
                        f"LOW STOCK: Product {row['product_id']} ({row['colour']}) → {row['total_quantity']} units\n"
                    )

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==============================
    # 🔄 NAVIGATION
    # ==============================

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.build_dashboard_home()
        self.load_dashboard_data()

    def open_stock(self):
        self.clear_content()
        StockPage(self.content, self.db, self.user)


    def open_plaza(self):
        self.clear_content()
        PlazaPage(self.content, self.db, self.user)

    def open_sending(self):
        self.clear_content()
        SendingPage(self.content, self.db, self.user)

    def open_returns(self):
        self.clear_content()
        ReturnsPage(self.content, self.db, self.user)

    def not_implemented(self):
        messagebox.showinfo("Info", "Module not implemented yet")

    def logout(self):
        self.root.destroy()

    # ==============================
    # ▶ RUN
    # ==============================

    def run(self):
        self.root.mainloop()