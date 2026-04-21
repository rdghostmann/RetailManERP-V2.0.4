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
        quantity: int,
        customer_contact: str,
        description: str = ""
    ):
        # ✅ Validation
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_quantity(quantity)
        Validators.validate_phone(customer_contact)

        query = """
        INSERT INTO sending (product_id, quantity, customer_contact, description, sent_by)
        VALUES (%s, %s, %s, %s, %s)
        """

        try:
            self.db.execute(query, (
                product_id,
                quantity,
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
        return self.db.fetch_all("SELECT * FROM sending")