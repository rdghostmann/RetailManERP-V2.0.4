from datetime import datetime
from services.log_service import LogService
from utils.validators import Validators


class PlazaService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def record_sale(
        self,
        user_id: int,
        product_id: int,
        imei: str,
        quantity: int,
        customer_name: str,
        customer_phone: str
    ):
        # ✅ Validation
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_imei(imei)
        Validators.validate_quantity(quantity)
        Validators.validate_required(customer_name, "Customer name required")
        Validators.validate_phone(customer_phone)

        # 🔎 Ensure IMEI exists in stock
        stock = self.db.fetch_one(
            "SELECT id FROM stock WHERE imei=%s",
            (imei,)
        )

        if not stock:
            raise ValueError("IMEI not found in stock")

        query = """
        INSERT INTO plaza (customer_name, customer_phone, product_id, imei, quantity, recorded_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            self.db.execute(query, (
                customer_name,
                customer_phone,
                product_id,
                imei,
                quantity,
                user_id,
                datetime.now()
            ))

            record = self.db.fetch_one(
                "SELECT id FROM plaza ORDER BY id DESC LIMIT 1"
            )

            # 🔐 Log action
            self.logger.log(user_id, "CREATE", "plaza", record["id"])

            return record

        except Exception as e:
            self.db.rollback()
            raise e

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM plaza")

    def get_sales_by_staff(self):
        query = """
        SELECT recorded_by, COUNT(*) as total_sales
        FROM plaza
        GROUP BY recorded_by
        """
        return self.db.fetch_all(query)