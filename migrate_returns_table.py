from models.db import Database

db = Database()
db.connect()

# Check if plaza_id column exists
try:
    # Try to add the plaza_id column if it doesn't exist
    db.execute("""
        ALTER TABLE returns 
        ADD COLUMN plaza_id INT AFTER id,
        ADD CONSTRAINT fk_returns_plaza FOREIGN KEY (plaza_id) REFERENCES plaza(id)
    """)
    print("✓ Added plaza_id column to returns table")
except Exception as e:
    if "Duplicate column name" in str(e):
        print("✓ plaza_id column already exists")
    else:
        print(f"Error: {e}")

# Verify the schema
cols = db.fetch_all('DESCRIBE returns')
print('\nUpdated returns table schema:')
for col in cols:
    print(f"  - {col['Field']}: {col['Type']}")
