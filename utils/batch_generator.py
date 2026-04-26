# utils/batch_generator.py
class BatchGenerator:
    def __init__(self, db):
        self.db = db

    def generate(self, table: str, prefix: str) -> str:
        last = self.db.fetch_one(
            f"""
            SELECT batch_no
            FROM {table}
            WHERE batch_no LIKE %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (f"{prefix}-%",)
        )

        if not last or not last.get("batch_no"):
            return f"{prefix}-0000"

        try:
            last_num = int(last["batch_no"].split("-")[-1])
            return f"{prefix}-{last_num + 1:04d}"
        except:
            return f"{prefix}-0000"