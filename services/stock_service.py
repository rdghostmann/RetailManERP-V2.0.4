# stock_service.py 
import random
from services.log_service import LogService
from app.config import InventoryConfig


class StockService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    # =========================
    # Batch Generator
    # =========================
    def generate_batch(self):
        return f"{InventoryConfig.BATCH_PREFIX}-{random.randint(10000,99999)}"

    # =========================
    # IMEI Validation
    # =========================
    def validate_imei(self, imei):
        if not imei or len(imei) != 15:
            raise ValueError("Invalid IMEI")

        exists = self.db.fetch_one(
            "SELECT id FROM stock WHERE imei=%s",
            (imei,)
        )

        if exists:
            raise ValueError("IMEI already exists")

    # =========================
    # ADD STOCK (FIXED)
    # =========================
    def add_stock(self, user_id, product_id, imei, colour, quantity):
        try:
            # Validate IMEI
            self.validate_imei(imei)

            batch_no = self.generate_batch()

            query = """
                INSERT INTO stock 
                (product_id, imei, colour, quantity, batch_no, added_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            self.db.execute(query, (
                product_id,
                imei,
                colour,
                quantity,
                batch_no,
                user_id
            ))

            # Get inserted record safely
            record = self.db.fetch_one(
                "SELECT id FROM stock WHERE imei=%s",
                (imei,)
            )

            if not record:
                raise ValueError("Failed to retrieve inserted stock record")

            # Log action
            self.logger.log(user_id, "CREATE", "stock", record["id"])

            return record

        except Exception as e:
            raise e

    # =========================
    # AGGREGATED STOCK VIEW
    # =========================
    def get_aggregated_stock(self):
        query = """
            SELECT 
                product_id,
                colour,
                SUM(quantity) as total_quantity
            FROM stock
            GROUP BY product_id, colour
        """

        return self.db.fetch_all(query)