import random
from services.log_service import LogService
from app.config import InventoryConfig


class StockService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    # =========================
    # 📦 Batch Generator
    # =========================
    def generate_batch(self):
        return f"{InventoryConfig.BATCH_PREFIX}-{random.randint(10000, 99999)}"

    # =========================
    # 🔐 IMEI Validation
    # =========================
    def validate_imei(self, imei: str):
        if not imei or not imei.isdigit() or len(imei) != 15:
            raise ValueError("Invalid IMEI format (must be 15 digits)")

        exists = self.db.fetch_one(
            "SELECT id FROM stock WHERE imei=%s",
            (imei,)
        )

        if exists:
            raise ValueError("IMEI already exists in stock")

    # =========================
    # 📥 ADD STOCK
    # =========================
    def add_stock(self, user_id, product_id, imei, colour, quantity=1):
        try:
            # Validate IMEI
            self.validate_imei(imei)

            # Enforce quantity rule (business constraint)
            if quantity != 1:
                raise ValueError("Quantity must be 1 per IMEI")

            query = """
                INSERT INTO stock 
                (product_id, imei, colour, quantity, added_by)
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db.execute(query, (
                product_id,
                imei,
                colour,
                quantity,
                user_id
            ))

            # Get inserted ID (preferred)
            record_id = self.db.last_insert_id()

            if not record_id:
                # fallback (safe guard)
                record = self.db.fetch_one(
                    "SELECT id FROM stock WHERE imei=%s",
                    (imei,)
                )
                if not record:
                    raise ValueError("Failed to retrieve inserted stock record")
                record_id = record["id"]

            # Compliance log
            self.logger.log(user_id, "CREATE", "stock", record_id)

            return {
                "id": record_id,
                "imei": imei
            }

        except Exception as e:
            raise e

    # =========================
    # 📊 RAW STOCK (IMEI VIEW)
    # =========================
    def get_all_stock(self):
        query = """
            SELECT 
                s.id,
                p.name AS product_name,
                s.imei,
                s.colour,
                s.quantity,
                s.created_at
            FROM stock s
            JOIN products p ON s.product_id = p.id
            ORDER BY s.created_at DESC
        """
        return self.db.fetch_all(query)

    # =========================
    # 📈 AGGREGATED STOCK
    # =========================
    def get_aggregated_stock(self):
        query = """
        SELECT 
            p.name,
            p.brand,
            p.description,
            s.colour,
            SUM(s.quantity) AS total_quantity,
            MIN(s.created_at) AS created_at
        FROM stock s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name, p.brand, p.description, s.colour
        ORDER BY p.name
    """
        return self.db.fetch_all(query)

    # =========================
    # 🔍 GET STOCK BY IMEI
    # =========================
    def get_by_imei(self, imei: str):
        query = """
            SELECT 
                s.id,
                p.id AS product_id,
                p.name AS product_name,
                s.imei,
                s.colour,
                s.quantity
            FROM stock s
            JOIN products p ON s.product_id = p.id
            WHERE s.imei=%s
        """
        return self.db.fetch_one(query, (imei,))

    # =========================
    # ❌ DELETE STOCK (Admin Only)
    # =========================
    def delete_stock(self, user, stock_id):
        if user["role"] != "admin":
            raise PermissionError("Only admin can delete stock")

        record = self.db.fetch_one(
            "SELECT id FROM stock WHERE id=%s",
            (stock_id,)
        )

        if not record:
            raise ValueError("Stock record not found")

        self.db.execute(
            "DELETE FROM stock WHERE id=%s",
            (stock_id,)
        )

        self.logger.log(user["id"], "DELETE", "stock", stock_id)

        return True