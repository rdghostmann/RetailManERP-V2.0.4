import pymysql
import bcrypt

# =========================
# 🔌 DB CONNECTION
# =========================
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Password@123",
    database="retail_man_db",
    cursorclass=pymysql.cursors.DictCursor
)

# =========================
# 🔐 HASH PASSWORD
# =========================
plain_password = "password123"
hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

try:
    with connection.cursor() as cursor:
        # Check if admin already exists
        cursor.execute(
            "SELECT id FROM users WHERE phone=%s",
            ("09032374880",)
        )
        existing = cursor.fetchone()

        if existing:
            print("⚠️ Admin user already exists")
        else:
            # Insert admin user
            sql = """
                INSERT INTO users (name, phone, password, role)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                "admin",
                "09032374880",
                hashed_password,
                "admin"
            ))

            connection.commit()
            print("✅ Admin user created successfully")

finally:
    connection.close()