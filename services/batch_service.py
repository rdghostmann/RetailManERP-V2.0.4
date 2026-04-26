# services/batch_services.py
class BatchService:
    def __init__(self, db):
        self.db = db

    def generate(self, module: str, prefix: str) -> str:
        """
        Generate a unique batch number like:
        PLAZA_SALE-0001
        RETURN-0001
        """

        try:
            # 🔒 START TRANSACTION (CRITICAL FOR CONCURRENCY)
            self.db.execute("START TRANSACTION")

            # 🔍 LOCK ROW
            row = self.db.fetch_one(
                "SELECT current_value FROM batch_sequences WHERE module=%s FOR UPDATE",
                (module,)
            )

            if not row:
                # create sequence if not exists
                self.db.execute(
                    "INSERT INTO batch_sequences (module, current_value) VALUES (%s, 0)",
                    (module,)
                )
                current = 0
            else:
                current = row["current_value"]

            next_value = current + 1

            # 🔄 UPDATE COUNTER
            self.db.execute(
                "UPDATE batch_sequences SET current_value=%s WHERE module=%s",
                (next_value, module)
            )

            # ✅ COMMIT
            self.db.execute("COMMIT")

            # 🎯 FORMAT: PREFIX-0001
            return f"{prefix}-{str(next_value).zfill(4)}"

        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e