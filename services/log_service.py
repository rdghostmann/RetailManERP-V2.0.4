from datetime import datetime


class LogService:
    def __init__(self, db):
        self.db = db

    def log(self, user_id, action, table_name, record_id):
        query = """
        INSERT INTO logs (user_id, action, table_name, record_id, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """

        self.db.execute(query, (
            user_id,
            action,
            table_name,
            record_id,
            datetime.now()
        ))