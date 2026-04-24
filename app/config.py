#app/config.py
"""
Global configuration module for RetailMan V1.2 (Improved)

- Secure environment handling
- Database configuration (production-safe)
- System-wide constants
"""

import os
from dataclasses import dataclass
from pymysql.cursors import DictCursor


# ==============================
# 🌍 ENVIRONMENT CONFIG
# ==============================

@dataclass(frozen=True)
class Environment:
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    APP_NAME: str = "RetailMan V2.1"
    VERSION: str = "2.1.2"


ENV = Environment()


# ==============================
# 🗄️ DATABASE CONFIG
# ==============================

@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 3306))
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD")
    database: str = os.getenv("DB_NAME")

    def __post_init__(self):
        if not self.password:
            raise ValueError("❌ DB_PASSWORD is not set in environment variables")

    def get_connection_dict(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.database,
            "cursorclass": DictCursor,
            "autocommit": True
        }


DB_CONFIG = DatabaseConfig()


# ==============================
# 📦 INVENTORY CONFIG
# ==============================

class InventoryConfig:
    IMEI_LENGTH = 15
    LOW_STOCK_THRESHOLD = 5
    BATCH_PREFIX = "RM-INV"
    DEFAULT_PAGE_SIZE = 20


# ==============================
# 🔐 AUTH CONFIG
# ==============================

class AuthConfig:
    SESSION_TIMEOUT_MINUTES = 60

    ROLES = {
        "ADMIN": "admin",
        "STAFF": "staff"
    }


# ==============================
# 📤 EXPORT CONFIG
# ==============================

class ExportConfig:
    EXPORT_DIR = os.path.join(os.getcwd(), "exports")

    @staticmethod
    def ensure_export_dir():
        os.makedirs(ExportConfig.EXPORT_DIR, exist_ok=True)


# Auto-init export directory
ExportConfig.ensure_export_dir()


# ==============================
# 🎨 UI CONFIG
# ==============================

class UIConfig:
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 900

    # 🖥️ Window Behavior
    FULLSCREEN = False          # true fullscreen (no title bar)
    MAXIMIZED = True            # recommended
    RESIZABLE = True           # disable manual resizing

    FONT = {
        "family": "JetBrains Mono",
        "size": 12
    }

    # Dark Theme
    DARK_COLORS = {
        "bg": "#212121",
        "fg": "#FFFFFF",
        "primary": "#9D007E",
        "secondary": "#1E1E1E",
        "accent": "#00509D",
        "text": "#FFFFFF",
        "text_secondary": "#B0B0B0",
        "border": "#404040",
        "success": "#28A745",
        "danger": "#FF6B6B",
        "warning": "#FFC107"
    }

    # Light Theme
    LIGHT_COLORS = {
        "bg": "#F5F5F5",
        "fg": "#000000",
        "primary": "#9D007E",
        "secondary": "#FFFFFF",
        "accent": "#00509D",
        "text": "#1A1A1A",
        "text_secondary": "#666666",
        "border": "#CCCCCC",
        "success": "#28A745",
        "danger": "#FF6B6B",
        "warning": "#FFC107"
    }


# ==============================
# ⚠️ SYSTEM MESSAGES
# ==============================

class Messages:
    IMEI_REQUIRED = "IMEI is required."
    IMEI_INVALID = "IMEI must be 15 digits."
    IMEI_DUPLICATE = "IMEI already exists."

    PRODUCT_REQUIRED = "Product selection is required."
    PRODUCT_DUPLICATE = "Product already exists."

    UNAUTHORIZED = "Unauthorized action."
    SUCCESS = "Operation completed successfully."
    FAILED = "Operation failed."