from dotenv import load_dotenv
import os
import sys

def get_env_path():
    # ✅ Check multiple locations for .env file
    
    # 1. Check AppData (for installed apps)
    base_path = os.getenv("LOCALAPPDATA")
    if base_path:
        app_dir = os.path.join(base_path, "RetailMan")
        appdata_env_path = os.path.join(app_dir, ".env")
        if os.path.exists(appdata_env_path):
            return appdata_env_path
    
    # 2. Check project root (for development)
    project_env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(project_env_path):
        return project_env_path
    
    # 3. If neither exists, return AppData path (will create it later if needed)
    if base_path:
        app_dir = os.path.join(base_path, "RetailMan")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, ".env")
    
    raise EnvironmentError("Cannot determine .env file path")

env_path = get_env_path()

if not os.path.exists(env_path):
    raise EnvironmentError(f".env not found at {env_path}. Please ensure .env is in either the project root or AppData\\RetailMan\\ directory.")

load_dotenv(env_path)


class Env:
    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    @staticmethod
    def require(key: str):
        value = os.getenv(key)
        if value is None:
            raise EnvironmentError(f"Missing required env variable: {key}")
        return value