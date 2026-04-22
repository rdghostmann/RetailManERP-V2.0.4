from services.log_service import LogService
from utils.validators import Validators


class ReturnsService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def get_plaza_sale_by_imei(self, imei: str):
        """Get the most recent plaza sale by IMEI"""
        query = """
        SELECT p.*, pr.name as product_name, pr.brand
        FROM plaza p
        JOIN products pr ON p.product_id = pr.id
        WHERE p.imei = %s
        ORDER BY p.created_at DESC
        LIMIT 1
        """
        return self.db.fetch_one(query, (imei,))

    def create_return(
        self,
        user_id: int,
        plaza_id: int,
        quantity: int,
        reason: str = ""
    ):
        """Create a return for a plaza sale"""
        # Get the original sale
        sale = self.db.fetch_one(
            """
            SELECT * FROM plaza WHERE id = %s
            """,
            (plaza_id,)
        )
        
        if not sale:
            raise ValueError("Sale not found")
        
        if quantity > sale["quantity"]:
            raise ValueError(f"Cannot return more than {sale['quantity']} items sold")
        
        Validators.validate_quantity(quantity)

        query = """
        INSERT INTO returns (plaza_id, imei, product_id, colour, quantity, reason, recorded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        try:
            self.db.execute(query, (
                plaza_id,
                sale["imei"],
                sale["product_id"],
                sale["colour"],
                quantity,
                reason,
                user_id
            ))

            record = self.db.fetch_one(
                "SELECT id FROM returns ORDER BY id DESC LIMIT 1"
            )

            # Restore stock
            self.db.execute(
                "UPDATE stock SET quantity = quantity + %s WHERE imei=%s",
                (quantity, sale["imei"])
            )

            # 🔐 Log action
            self.logger.log(user_id, "CREATE", "returns", record["id"])

            return record

        except Exception as e:
            raise e

            return record

        except Exception as e:
            raise e

    def get_all(self):
        query = """
        SELECT r.*, p.customer_name, p.customer_phone, p.imei, p.colour, pr.name as product_name
        FROM returns r
        JOIN plaza p ON r.plaza_id = p.id
        JOIN products pr ON p.product_id = pr.id
        """
        return self.db.fetch_all(query)