# services/premises_service.py
from services.log_service import LogService
from services.batch_service import BatchService
from utils.validators import Validators


class PremisesService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)
        self.batch = BatchService(db)

    # =====================================================
    # 🧾 RECORD SALE (WITH BATCH NO)
    # =====================================================
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

        try:
            self.db.execute("START TRANSACTION")

            stock = self.db.fetch_one(
                "SELECT id, quantity FROM stock WHERE imei=%s AND colour=%s FOR UPDATE",
                (imei, colour)
            )

            if not stock:
                raise ValueError("Stock not found")

            if stock["quantity"] < quantity:
                raise ValueError("Insufficient stock")

            # 🔥 BatchNo (Premises level)
            batch_no = self.batch.generate("premises_sales", "PREMISES")

            self.db.execute(
                """
                INSERT INTO premises_sales (
                    batch_no,
                    product_id,
                    imei,
                    colour,
                    quantity,
                    customer_name,
                    customer_phone,
                    sold_by
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    batch_no,
                    product_id,
                    imei,
                    colour,
                    quantity,
                    customer_name,
                    customer_phone,
                    user_id
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

            self.db.execute("COMMIT")

            self.logger.log(user_id, "CREATE", "premises_sales", product_id)

        except Exception:
            self.db.execute("ROLLBACK")
            raise

    # =====================================================
    # 📊 GET ALL SALES (WITH PRODUCT JOIN)
    # =====================================================
    def get_all(self):
        return self.db.fetch_all(
            """
            SELECT 
                ps.id,
                ps.batch_no,
                ps.product_id,
                p.name AS product_name,
                ps.imei,
                ps.colour,
                ps.quantity,
                ps.customer_name,
                ps.customer_phone,
                ps.created_at
            FROM premises_sales ps
            JOIN products p ON p.id = ps.product_id
            ORDER BY ps.id DESC
            """
        )