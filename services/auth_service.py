import hashlib


class AuthService:
    def __init__(self, db):
        self.db = db

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, name: str, phone: str):
        query = "SELECT * FROM users WHERE name=%s AND phone=%s"
        return self.db.fetch_one(query, (name, phone))

    def set_password(self, user_id: int, password: str):
        hashed = self.hash_password(password)

        query = "UPDATE users SET password=%s WHERE id=%s"
        self.db.execute(query, (hashed, user_id))

    def verify_password(self, user, password: str):
        return user["password"] == self.hash_password(password)