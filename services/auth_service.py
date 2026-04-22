#auth_service.py
import bcrypt


class AuthService:
    def __init__(self, db):
        self.db = db

    # =========================
    # 🔐 HASH PASSWORD
    # =========================
    def hash_password(self, password: str) -> str:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    # =========================
    # 👤 GET USER (LOGIN STEP 1)
    # =========================
    def get_user(self, name: str, phone: str):
        query = """
            SELECT * FROM users 
            WHERE name=%s AND phone=%s
        """
        return self.db.fetch_one(query, (name, phone))

    # =========================
    # 🆕 FIRST-TIME PASSWORD SET
    # =========================
    def set_password(self, user_id: int, password: str):
        hashed = self.hash_password(password)

        query = """
            UPDATE users 
            SET password=%s 
            WHERE id=%s
        """
        self.db.execute(query, (hashed, user_id))

    # =========================
    # 🔑 VERIFY PASSWORD
    # =========================
    def verify_password(self, user, password: str) -> bool:
        if not user["password"]:
            return False

        return bcrypt.checkpw(
            password.encode(),
            user["password"].encode()
        )

    # =========================
    # 🚀 FULL LOGIN FLOW
    # =========================
    def login(self, name: str, phone: str, password: str = None):
        user = self.get_user(name, phone)

        if not user:
            raise Exception("User not found")

        # First-time login (no password yet)
        if not user["password"]:
            return {
                "status": "SET_PASSWORD",
                "user": user
            }

        # Verify password
        if not self.verify_password(user, password):
            raise Exception("Invalid credentials")

        return {
            "status": "SUCCESS",
            "user": user
        }