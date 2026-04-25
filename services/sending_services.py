#services/sending_services.py
from services.log_service import LogService
from utils.validators import Validators


class SendingService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def create_dispatch(
        self,
        user_id: int,
        product_id: int,
        customer_name: str,
        customer_contact: str,
        description: str = ""
    ):
        # ✅ Validation
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_required(customer_name, "Customer name is required")
        Validators.validate_phone(customer_contact)

        query = """
        INSERT INTO sending (product_id, customer_name, customer_contact, description, sent_by)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            self.db.execute(query, (
                product_id,
                customer_name,
                customer_contact,
                description,
                user_id
            ))

            record = self.db.fetch_one(
                "SELECT id FROM sending ORDER BY id DESC LIMIT 1"
            )

            # 🔐 Log action
            self.logger.log(user_id, "CREATE", "sending", record["id"])

            return record

        except Exception as e:
            raise e

    def get_all(self):
        return self.db.fetch_all("""
            SELECT *
            FROM sending
            ORDER BY created_at DESC
        """)
    
    def mark_as_collected(self,
        user_id: int,
        sending_id: int,
        collected_name: str,
        collected_phone: str
    ):
        # 🔎 Get original record
        record = self.db.fetch_one(
            "SELECT * FROM sending WHERE id=%s",
            (sending_id,)
        )

        if not record:
            raise ValueError("Record not found")

        Validators.validate_required(collected_name, "Collector name required")
        Validators.validate_phone(collected_phone)

        try:
            # ✅ Insert into collected
            self.db.execute(
                """
                INSERT INTO collected (
                    sending_id, product_id,
                    customer_name, customer_contact,
                    description,
                    collected_by_name, collected_by_phone
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    sending_id,
                    record["product_id"],
                    record["customer_name"],
                    record["customer_contact"],
                    record["description"],
                    collected_name,
                    collected_phone
                )
            )

            # ❌ Remove from sending
            self.db.execute(
                "DELETE FROM sending WHERE id=%s",
                (sending_id,)
            )

            self.logger.log(user_id, "MOVE", "sending→collected", sending_id)

        except Exception as e:
            raise e