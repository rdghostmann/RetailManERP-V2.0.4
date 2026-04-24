import pymysql


def seed_products():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Password@123",
        database="retail_man_db",
        cursorclass=pymysql.cursors.DictCursor
    )

    products = [
        {"name": "iPhone 13", "brand": "Apple", "description": "128GB Smartphone"},
        {"name": "iPhone 14 Pro", "brand": "Apple", "description": "256GB Pro Model"},
        {"name": "Galaxy S22", "brand": "Samsung", "description": "Flagship Android"},
        {"name": "Galaxy A54", "brand": "Samsung", "description": "Mid-range device"},
        {"name": "Redmi Note 12", "brand": "Xiaomi", "description": "Budget smartphone"},
        {"name": "Pixel 7", "brand": "Google", "description": "Pure Android experience"},
        {"name": "Tecno Camon 20", "brand": "Tecno", "description": "Camera focused"},
        {"name": "Infinix Zero 5G", "brand": "Infinix", "description": "Affordable 5G device"}
    ]

    try:
        with connection.cursor() as cursor:
            for product in products:
                query = """
                    INSERT INTO products (name, brand, description)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        description = VALUES(description)
                """

                cursor.execute(query, (
                    product["name"],
                    product["brand"],
                    product["description"]
                ))

        connection.commit()
        print("✅ Products seeded successfully")

    finally:
        connection.close()


if __name__ == "__main__":
    seed_products()