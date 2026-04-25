# services/product_service.py
from services.log_service import LogService

class ProductService:
    def __init__(self, db):
        self.db = db
        self.logger = LogService(db)

    # =========================
    # ➕ CREATE PRODUCT
    # =========================
    def create_product(self, user_id, name, brand, description):
        name = name.strip()

        if not name:
            raise ValueError("Product name is required")

        # ✅ Case-insensitive duplicate check
        exists = self.db.fetch_one(
            "SELECT id FROM products WHERE LOWER(name)=LOWER(%s)",
            (name,)
        )

        if exists:
            raise ValueError("Product already exists")

        query = """
        INSERT INTO products (name, brand, description)
        VALUES (%s, %s, %s)
        """

        self.db.execute(query, (name, brand.strip(), description.strip()))

        # ✅ Reliable fetch (LAST_INSERT_ID safer if supported)
        product = self.db.fetch_one(
            "SELECT id, name FROM products WHERE name=%s ORDER BY id DESC LIMIT 1",
            (name,)
        )

        if not product:
            raise ValueError("Failed to create product")

        # 🔐 Log
        self.logger.log(user_id, "CREATE", "products", product["id"])

        return product

    # =========================
    # 📦 GET ALL PRODUCTS
    # =========================
    def get_all(self):
        return self.db.fetch_all("SELECT * FROM products ORDER BY name ASC")

    # =========================
    # 🔍 GET PRODUCT BY IMEI
    # =========================
    def get_by_imei(self, imei: str):
        if not imei:
            return None

        query = """
        SELECT 
            p.id,
            p.name,
            p.brand,
            p.description,
            s.imei,
            s.quantity,
            s.colour,
            s.created_at
        FROM stock s
        JOIN products p ON s.product_id = p.id
        WHERE s.imei = %s
        LIMIT 1
        """

        return self.db.fetch_one(query, (imei,))

    # =========================
    # 🔍 GET PRODUCT BY ID (NEW)
    # =========================
    def get_by_id(self, product_id: int):
        return self.db.fetch_one(
            "SELECT * FROM products WHERE id=%s",
            (product_id,)
        )