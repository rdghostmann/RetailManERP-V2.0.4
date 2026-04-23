# utils/session_manager.py
class SessionManager:
    current_user = None

    @classmethod
    def login(cls, user):
        cls.current_user = user

    @classmethod
    def logout(cls):
        cls.current_user = None

    @classmethod
    def get_user(cls):
        return cls.current_user

    @classmethod
    def is_authenticated(cls):
        return cls.current_user is not None