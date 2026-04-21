import random
import string
from datetime import datetime
from app.config import InventoryConfig


def generate_batch_number() -> str:
    """Generate inventory batch number"""
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"{InventoryConfig.BATCH_PREFIX}-{random_part}"


def current_timestamp():
    """Return current timestamp"""
    return datetime.now()


def format_currency(amount: float) -> str:
    """Optional helper for UI display"""
    return f"₦{amount:,.2f}"


def safe_int(value, default=0):
    """Safely cast to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default