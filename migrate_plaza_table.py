from models.db import Database

db = Database()
db.connect()

try:
    db.execute("""
        ALTER TABLE plaza 
        ADD COLUMN colour VARCHAR(50) AFTER imei
    """)
    print("✓ Added colour column to plaza table")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✓ colour column already exists")
    else:
        print(f"Error: {e}")

# Verify
cols = db.fetch_all('DESCRIBE plaza')
print('\nUpdated plaza table schema:')
for col in cols:
    print(f"  - {col['Field']}: {col['Type']}")
