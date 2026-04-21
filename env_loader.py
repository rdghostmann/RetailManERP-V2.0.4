"""
Environment loader for RetailMan

Ensures .env variables are loaded before app startup.
"""

from dotenv import load_dotenv
import os

# Load .env at startup
load_dotenv()


class Env:
    """Central access point for environment variables"""

    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    @staticmethod
    def require(key: str):
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Missing required env variable: {key}")
        return value