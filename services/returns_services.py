# services/returns_services.py
from services.log_service import LogService
from services.batch_service import BatchService
from utils.validators import Validators


class ReturnsService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)
        self.batch = BatchService(db)

    # =========================
    # GET SALE BY IMEI
    # =========================
    def get_plaza_sale_by_imei(self, imei: str):
        query = """
        SELECT p.*, pr.name as product_name, pr.brand
        FROM plaza p
        JOIN products pr ON p.product_id = pr.id
        WHERE p.imei = %s
        ORDER BY p.created_at DESC
        LIMIT 1
        """
        return self.db.fetch_one(query, (imei,))

    # =========================
    # CREATE RETURN (WITH BATCH NO)
    # =========================
    def create_return(
        self,
        user_id: int,
        plaza_id: int,
        quantity: int,
        reason: str = ""
    ):
        sale = self.db.fetch_one(
            "SELECT * FROM plaza WHERE id = %s",
            (plaza_id,)
        )

        if not sale:
            raise ValueError("Sale not found")

        if quantity > sale["quantity"]:
            raise ValueError("Cannot return more than sold quantity")

        Validators.validate_quantity(quantity)

        try:
            self.db.execute("START TRANSACTION")

            # 🔥 Generate batch number
            batch_no = self.batch.generate("returns", "RETURN")

            # =========================
            # INSERT RETURN
            # =========================
            self.db.execute(
                """
                INSERT INTO returns (
                    batch_no, plaza_id, imei, product_id, colour,
                    quantity, reason, recorded_by
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    batch_no,
                    plaza_id,
                    sale["imei"],
                    sale["product_id"],
                    sale["colour"],
                    quantity,
                    reason,
                    user_id
                )
            )

            record = self.db.fetch_one(
                "SELECT id FROM returns ORDER BY id DESC LIMIT 1"
            )

            # =========================
            # RESTORE STOCK
            # =========================
            self.db.execute(
                "UPDATE stock SET quantity = quantity + %s WHERE imei=%s",
                (quantity, sale["imei"])
            )

            self.db.execute("COMMIT")

            self.logger.log(user_id, "CREATE", "returns", record["id"])

            return record

        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e

    # =========================
    # GET ALL RETURNS
    # =========================
    def get_all(self):
        query = """
        SELECT 
            r.id,
            r.batch_no,
            r.created_at,
            p.customer_name,
            p.customer_phone,
            p.imei,
            p.colour,
            pr.name as product_name,
            r.quantity,
            r.reason
        FROM returns r
        JOIN plaza p ON r.plaza_id = p.id
        JOIN products pr ON p.product_id = pr.id
        ORDER BY r.created_at DESC
        """
        return self.db.fetch_all(query)