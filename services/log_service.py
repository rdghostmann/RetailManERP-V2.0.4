class LogService:
    def __init__(self, db):
        self.db = db

    def log(self, user_id, action, table_name, record_id):
        query = """
        INSERT INTO logs (user_id, action, table_name, record_id)
        VALUES (%s, %s, %s, %s)
        """

        self.db.execute(query, (
            user_id,
            action,
            table_name,
            record_id
        ))