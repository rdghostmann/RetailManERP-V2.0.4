import pymysql
from pymysql.connections import Connection
from typing import Any, Dict, List, Optional
from env_loader import Env


class Database:
    """
    Core DB handler (lightweight connection manager)
    """

    def __init__(self):
        self.connection: Optional[Connection] = None

    # ==============================
    # 🔌 CONNECTION HANDLING
    # ==============================

    def connect(self) -> Connection:
        if self.connection and self.connection.open:
            return self.connection

        try:
            # ✅ Load config directly from .env
            self.connection = pymysql.connect(
                host=Env.require("DB_HOST"),
                user=Env.require("DB_USER"),
                password=Env.require("DB_PASSWORD"),
                database=Env.require("DB_NAME"),
                port=int(Env.get("DB_PORT", 3306)),
                cursorclass=pymysql.cursors.DictCursor
            )
            return self.connection

        except Exception as e:
            raise ConnectionError(f"Database connection failed: {str(e)}")

    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()

    # ==============================
    # ⚙️ CORE QUERY METHODS
    # ==============================

    def execute(self, query: str, params: tuple = None) -> int:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                result = cursor.execute(query, params)
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Query execution failed: {str(e)}")

    def fetch_one(self, query: str, params: tuple = None) -> Dict:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            raise RuntimeError(f"Fetch one failed: {str(e)}")

    def fetch_all(self, query: str, params: tuple = None) -> List[Dict]:
        conn = self.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"Fetch all failed: {str(e)}")

    # ==============================
    # 🧪 HEALTH CHECK
    # ==============================

    def ping(self) -> bool:
        try:
            conn = self.connect()
            conn.ping(reconnect=True)
            return True
        except Exception:
            return False


# Singleton instance
db = Database()