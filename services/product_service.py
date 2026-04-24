# services/product_service.py
from services.log_service import LogService


class ProductService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    def create_product(self, user_id, name, brand, description):
        # Check duplicate
        exists = self.db.fetch_one(
            "SELECT id FROM products WHERE name=%s",
            (name,)
        )

        if exists:
            raise ValueError("Product already exists")

        query = """
        INSERT INTO products (name, brand, description)
        VALUES (%s, %s, %s)
        """

        self.db.execute(query, (name, brand, description))

        product = self.db.fetch_one(
            "SELECT id FROM products WHERE name=%s",
            (name,)
        )

        self.logger.log(user_id, "CREATE", "products", product["id"])

        return product

    def get_all(self):
        return self.db.fetch_all("SELECT * FROM products")

    def get_by_imei(self, imei: str):
        """Get product details by IMEI from stock"""
        query = """
        SELECT p.*, s.imei, s.quantity as stock_quantity, s.colour
        FROM stock s
        JOIN products p ON s.product_id = p.id
        WHERE s.imei = %s
        """
        return self.db.fetch_one(query, (imei,))