# services/premises_service.py
from services.log_service import LogService
from utils.validators import Validators


class PremisesService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def record_sale(
        self,
        user_id,
        product_id,
        imei,
        colour,
        quantity,
        customer_name,
        customer_phone
    ):
        Validators.validate_phone(customer_phone)

        stock = self.db.fetch_one(
            "SELECT id, quantity FROM stock WHERE imei=%s AND colour=%s",
            (imei, colour)
        )

        if not stock or stock["quantity"] < quantity:
            raise ValueError("Insufficient stock")

        try:
            # INSERT SALE
            self.db.execute(
                """
                INSERT INTO premises_sales (
                    product_id, imei, colour, quantity,
                    customer_name, customer_phone, sold_by
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    product_id, imei, colour,
                    quantity, customer_name,
                    customer_phone, user_id
                )
            )

            # UPDATE STOCK
            new_qty = stock["quantity"] - quantity

            if new_qty > 0:
                self.db.execute(
                    "UPDATE stock SET quantity=%s WHERE id=%s",
                    (new_qty, stock["id"])
                )
            else:
                self.db.execute(
                    "DELETE FROM stock WHERE id=%s",
                    (stock["id"],)
                )

            self.logger.log(user_id, "CREATE", "premises_sales", product_id)

        except Exception as e:
            raise e

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM premises_sales")