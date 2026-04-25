# services/plaza_services.py
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
        colour: str,
        quantity: int,
        customer_name: str,
        customer_phone: str
    ):
        # =========================
        # ✅ VALIDATION
        # =========================
        Validators.validate_required(product_id, "Product is required")
        Validators.validate_imei(imei)
        Validators.validate_quantity(quantity)
        Validators.validate_required(customer_name, "Customer name required")
        Validators.validate_phone(customer_phone)

        # =========================
        # 🔎 CHECK STOCK EXISTS
        # =========================
        stock = self.db.fetch_one(
            "SELECT id FROM stock WHERE imei=%s",
            (imei,)
        )

        if not stock:
            raise ValueError("IMEI not found in stock")

        # =========================
        # 🔎 GET SPECIFIC COLOUR STOCK
        # =========================
        colour_stock = self.db.fetch_one(
            "SELECT id, quantity FROM stock WHERE imei=%s AND colour=%s",
            (imei, colour)
        )

        if not colour_stock:
            raise ValueError(f"Colour '{colour}' not found in stock")

        if colour_stock["quantity"] < quantity:
            raise ValueError(f"Insufficient stock for colour '{colour}'")

        try:
            # =========================
            # 🔥 1. INSERT SALE RECORD
            # =========================
            self.db.execute(
                """
                INSERT INTO plaza (customer_name, customer_phone, product_id, imei, colour, quantity, recorded_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    customer_name,
                    customer_phone,
                    product_id,
                    imei,
                    colour,
                    quantity,
                    user_id
                )
            )

    
            # =========================
            # 🔥 3. FETCH LAST RECORD
            # =========================
            record = self.db.fetch_one(
                "SELECT id FROM plaza ORDER BY id DESC LIMIT 1"
            )

            # =========================
            # 🔐 LOG ACTION
            # =========================
            self.logger.log(user_id, "CREATE", "plaza", record["id"])

            return record

        except Exception as e:
            raise e

    def mark_as_sale(self, user_id: int, plaza_id: int):
        record = self.db.fetch_one(
            "SELECT * FROM plaza WHERE id=%s",
            (plaza_id,)
        )

        if not record:
            raise ValueError("Sale record not found")

        # get stock
        stock = self.db.fetch_one(
            "SELECT id, quantity FROM stock WHERE imei=%s AND colour=%s",
            (record["imei"], record["colour"])
        )

        if not stock:
            raise ValueError("Stock not found")

        if stock["quantity"] < record["quantity"]:
            raise ValueError("Insufficient stock")

        try:
            # ✅ INSERT INTO plaza_sales (NEW TABLE)
            self.db.execute(
                """
                INSERT INTO plaza_sales (
                    plaza_id, product_id, imei, colour, quantity, sold_by
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                """,
                (
                    plaza_id,
                    record["product_id"],
                    record["imei"],
                    record["colour"],
                    record["quantity"],
                    user_id
                )
            )

            # ✅ UPDATE STOCK
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

            self.logger.log(user_id, "SALE", "plaza_sales", plaza_id)

        except Exception as e:
            raise e


    # =========================
    # 📊 FETCH ALL SALES
    # =========================
    def get_all(self):
        return self.db.fetch_all("SELECT * FROM plaza")

    # =========================
    # 📊 SALES BY STAFF
    # =========================
    def get_sales_by_staff(self):
        query = """
        SELECT recorded_by, COUNT(*) as total_sales
        FROM plaza
        GROUP BY recorded_by
        """
        return self.db.fetch_all(query)