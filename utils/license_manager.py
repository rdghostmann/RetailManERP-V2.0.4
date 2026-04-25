#utils/license_manager.py
import os
from datetime import datetime, timedelta
import hashlib

# =========================
# 🔐 HASH FUNCTION
# =========================
def hash_key(value: str):
    return hashlib.sha256(value.encode()).hexdigest()


# =========================
# 📁 HIDDEN STORAGE LOCATION
# =========================
BASE_DIR = os.path.join(os.path.expanduser("~"), ".retailman")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

LICENSE_FILE = os.path.join(BASE_DIR, "sys_cache.dat")
INSTALL_FILE = os.path.join(BASE_DIR, "sys_config.dat")


# =========================
# 🔑 LICENSE CONFIG
# =========================
VALID_LICENSE_HASH = hash_key("Randal Chukwuweike Wilson")
TRIAL_DAYS = 365


class LicenseManager:

    # =========================
    # FILE HELPERS
    # =========================
    @staticmethod
    def _write_file(path, value):
        try:
            with open(path, "w") as f:
                f.write(value)
        except Exception:
            pass

    @staticmethod
    def _read_file(path):
        try:
            if not os.path.exists(path):
                return None
            with open(path, "r") as f:
                return f.read().strip()
        except Exception:
            return None

    # =========================
    # INSTALL DATE
    # =========================
    @staticmethod
    def initialize():
        """Create install date if not exists and prevent rollback"""
        today = datetime.now()

        if not os.path.exists(INSTALL_FILE):
            LicenseManager._write_file(
                INSTALL_FILE,
                today.strftime("%Y-%m-%d")
            )
        else:
            saved = LicenseManager.get_install_date()

            # 🔐 Prevent system date rollback trick
            if saved and saved > today:
                LicenseManager._write_file(
                    INSTALL_FILE,
                    today.strftime("%Y-%m-%d")
                )

    @staticmethod
    def get_install_date():
        value = LicenseManager._read_file(INSTALL_FILE)
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except Exception:
            return None

    # =========================
    # LICENSE
    # =========================
    @staticmethod
    def is_licensed():
        key = LicenseManager._read_file(LICENSE_FILE)
        return key == VALID_LICENSE_HASH

    @staticmethod
    def activate(key):
        """Activate license using plain text input"""
        if hash_key(key.strip()) == VALID_LICENSE_HASH:
            LicenseManager._write_file(LICENSE_FILE, VALID_LICENSE_HASH)
            return True
        return False

    # =========================
    # EXPIRY
    # =========================
    @staticmethod
    def is_expired():
        install_date = LicenseManager.get_install_date()

        if not install_date:
            return False

        expiry_date = install_date + timedelta(days=TRIAL_DAYS)
        return datetime.now() > expiry_date

    # =========================
    # DAYS REMAINING (UX BOOST)
    # =========================
    @staticmethod
    def days_remaining():
        install_date = LicenseManager.get_install_date()

        if not install_date:
            return TRIAL_DAYS

        expiry_date = install_date + timedelta(days=TRIAL_DAYS)
        remaining = (expiry_date - datetime.now()).days

        return max(0, remaining)