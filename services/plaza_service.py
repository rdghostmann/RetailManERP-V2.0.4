# services/plaza_services.py
from services.log_service import LogService
from utils.validators import Validators
from services.batch_service import BatchService


class PlazaService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)
        self.batch = BatchService(db)

    # =====================================================
    # 📝 RECORD ENTRY (PLAZA - STAGING)
    # =====================================================
    def record_sale(
        self,
        user_id: int,
        product_id: int,
        imei: str,
        colour: str,
        quantity: int,
        customer_name: str,
        customer_phone: str
    ):
        # ---------- VALIDATION ----------
        Validators.validate_required(product_id, "Product required")
        Validators.validate_imei(imei)
        Validators.validate_quantity(quantity)
        Validators.validate_required(customer_name, "Customer name required")
        Validators.validate_phone(customer_phone)

        try:
            self.db.execute("START TRANSACTION")

            # ---------- LOCK STOCK ----------
            stock = self.db.fetch_one(
                "SELECT id FROM stock WHERE imei=%s FOR UPDATE",
                (imei,)
            )

            if not stock:
                raise ValueError("IMEI not found in stock")

            # ---------- GENERATE BATCH NO ----------
            batch_no = self.batch.generate("plaza", "PLAZA")

            # ---------- INSERT PLAZA ----------
            self.db.execute(
                """
                INSERT INTO plaza (
                    batch_no,
                    product_id,
                    imei,
                    colour,
                    quantity,
                    customer_name,
                    customer_phone,
                    recorded_by
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

            record = self.db.fetch_one(
                "SELECT id FROM plaza ORDER BY id DESC LIMIT 1"
            )

            self.db.execute("COMMIT")

            self.logger.log(user_id, "CREATE", "plaza", record["id"])

            return record

        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e

    # =====================================================
    # 💰 FINALIZE SALE (PLAZA → PLAZA SALES)
    # =====================================================
    def mark_as_sale(self, user_id: int, plaza_id: int):

        try:
            self.db.execute("START TRANSACTION")

            # ---------- LOCK PLAZA ----------
            record = self.db.fetch_one(
                """
                SELECT * FROM plaza
                WHERE id=%s
                FOR UPDATE
                """,
                (plaza_id,)
            )

            if not record:
                raise ValueError("Plaza record not found")

            # ---------- PREVENT DUPLICATE ----------
            exists = self.db.fetch_one(
                "SELECT id FROM plaza_sales WHERE plaza_id=%s",
                (plaza_id,)
            )

            if exists:
                raise ValueError("Already marked as sale")

            # ---------- LOCK STOCK ----------
            stock = self.db.fetch_one(
                """
                SELECT id, quantity
                FROM stock
                WHERE imei=%s AND colour=%s
                FOR UPDATE
                """,
                (record["imei"], record["colour"])
            )

            if not stock:
                raise ValueError("Stock not found")

            if stock["quantity"] < record["quantity"]:
                raise ValueError("Insufficient stock")

            # ---------- GENERATE SALE BATCH ----------
            batch_no = self.batch.generate("plaza_sales", "PLAZA_SALE")

            # ---------- INSERT INTO SALES ----------
            self.db.execute(
                """
                INSERT INTO plaza_sales (
                    batch_no,
                    plaza_id,
                    product_id,
                    imei,
                    colour,
                    quantity,
                    sold_by
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    batch_no,
                    plaza_id,
                    record["product_id"],
                    record["imei"],
                    record["colour"],
                    record["quantity"],
                    user_id
                )
            )

            # ---------- UPDATE STOCK ----------
            new_qty = stock["quantity"] - record["quantity"]

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

            self.logger.log(user_id, "SALE", "plaza_sales", plaza_id)

        except Exception as e:
            self.db.execute("ROLLBACK")
            raise e

    # =====================================================
    # 📊 PLAZA ENTRIES (UI FEED)
    # =====================================================
    def get_all(self):
        return self.db.fetch_all(
            """
            SELECT
                pl.id,
                pl.batch_no,
                pl.product_id,
                p.name AS product_name,
                pl.imei,
                pl.colour,
                pl.quantity,
                pl.customer_name,
                pl.customer_phone,
                pl.created_at
            FROM plaza pl
            JOIN products p ON pl.product_id = p.id
            ORDER BY pl.id DESC
            """
        )

    # =====================================================
    # 📊 FINAL SALES (UI FEED)
    # =====================================================
    def get_all_sales(self):
        return self.db.fetch_all(
            """
            SELECT
                ps.id,
                ps.batch_no,
                ps.plaza_id,
                ps.product_id,
                p.name AS product_name,
                ps.imei,
                ps.colour,
                ps.quantity,
                ps.sold_by,
                ps.created_at
            FROM plaza_sales ps
            JOIN products p ON ps.product_id = p.id
            ORDER BY ps.id DESC
            """
        )