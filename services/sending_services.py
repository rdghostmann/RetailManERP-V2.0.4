#services/sending_services.py
from services.log_service import LogService
from services.batch_service import BatchService
from utils.validators import Validators


class SendingService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)
        self.batch = BatchService(db)

    # =====================================================
    # 🚚 CREATE DISPATCH
    # =====================================================
    def create_dispatch(
        self,
        user_id: int,
        product_id: int,
        customer_name: str,
        customer_contact: str,
        description: str = ""
    ):
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_required(customer_name, "Customer name is required")
        Validators.validate_phone(customer_contact)

        try:
            self.db.execute("START TRANSACTION")

            batch_no = self.batch.generate("sending", "SEND")

            # 🔥 SAFE INSERT (handles DB without description column)
            self.db.execute(
                """
                INSERT INTO sending (
                    batch_no,
                    product_id,
                    customer_name,
                    customer_contact,
                    sent_by
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (
                    batch_no,
                    product_id,
                    customer_name,
                    customer_contact,
                    user_id
                )
            )

            record = self.db.fetch_one(
                "SELECT id FROM sending ORDER BY id DESC LIMIT 1"
            )

            self.db.execute("COMMIT")

            self.logger.log(user_id, "CREATE", "sending", record["id"])
            return record

        except Exception:
            self.db.execute("ROLLBACK")
            raise

    # =====================================================
    # 📊 GET ALL DISPATCH
    # =====================================================
    def get_all(self):
        return self.db.fetch_all(
            """
            SELECT
                s.id,
                s.batch_no,
                s.product_id,
                p.name AS product_name,
                s.customer_name,
                s.customer_contact,
                s.created_at
            FROM sending s
            JOIN products p ON p.id = s.product_id
            ORDER BY s.created_at DESC
            """
        )

    # =====================================================
    # 📦 MARK AS COLLECTED
    # =====================================================
    def mark_as_collected(
        self,
        user_id: int,
        sending_id: int,
        collected_name: str,
        collected_phone: str
    ):
        Validators.validate_required(collected_name, "Collector name required")
        Validators.validate_phone(collected_phone)

        try:
            self.db.execute("START TRANSACTION")

            record = self.db.fetch_one(
                "SELECT * FROM sending WHERE id=%s FOR UPDATE",
                (sending_id,)
            )

            if not record:
                raise ValueError("Record not found")

            batch_no = record.get("batch_no")

            # 🔥 SAFE MOVE TO COLLECTED (NO description dependency)
            self.db.execute(
                """
                INSERT INTO collected (
                    batch_no,
                    sending_id,
                    product_id,
                    customer_name,
                    customer_contact,
                    collected_by_name,
                    collected_by_phone
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    batch_no,
                    sending_id,
                    record["product_id"],
                    record["customer_name"],
                    record["customer_contact"],
                    collected_name,
                    collected_phone
                )
            )

            self.db.execute(
                "DELETE FROM sending WHERE id=%s",
                (sending_id,)
            )

            self.db.execute("COMMIT")

            self.logger.log(user_id, "MOVE", "sending→collected", sending_id)

        except Exception:
            self.db.execute("ROLLBACK")
            raise