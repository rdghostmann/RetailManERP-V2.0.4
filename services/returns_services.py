from datetime import datetime
from services.log_service import LogService
from utils.validators import Validators


class ReturnsService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def create_return(
        self,
        user_id: int,
        product_id: int,
        imei: str,
        colour: str,
        quantity: int,
        reason: str = ""
    ):
        # ✅ Validation
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_imei(imei)
        Validators.validate_quantity(quantity)

        query = """
        INSERT INTO returns (product_id, imei, colour, quantity, reason, recorded_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            self.db.execute(query, (
                product_id,
                imei,
                colour,
                quantity,
                reason,
                user_id,
                datetime.now()
            ))

            record = self.db.fetch_one(
                "SELECT id FROM returns ORDER BY id DESC LIMIT 1"
            )

            # 🔐 Log action
            self.logger.log(user_id, "CREATE", "returns", record["id"])

            return record

        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM returns")