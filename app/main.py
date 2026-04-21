import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))



from ui.login import LoginWindow
from models.db import Database

from app.config import DB_CONFIG

def bootstrap():
    """Initialize application"""
    db = Database()
    db.connect()

    app = LoginWindow(db)
    app.run()

if __name__ == "__main__":
    bootstrap()