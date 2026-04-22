
# db.py
import pymysql
from pymysql.connections import Connection
from typing import Any, Dict, List, Optional
from env_loader import Env
from app.config import DB_CONFIG


class Database:
    """
    Core DB handler (lightweight connection manager)
    """

    def __init__(self):
        self.config = DB_CONFIG.get_connection_dict()
        self.connection: Optional[Connection] = None

    # ==============================
    # 🔌 CONNECTION HANDLING
    # ==============================

    def connect(self) -> Connection:
        if self.connection and self.connection.open:
            return self.connection

        try:
            self.connection = pymysql.connect(**self.config)
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
        """
        Insert/Update/Delete operations
        Returns affected rows
        """
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


# Singleton instance for app-wide reuse
db = Database()