import sqlite3

conn = sqlite3.connect("second_brain.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE memories
    ADD COLUMN embedding TEXT
    """)
    print("✅ Embedding column added successfully.")
except Exception as e:
    print(e)

conn.commit()
conn.close()