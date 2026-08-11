import sqlite3

conn = sqlite3.connect("second_brain.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(memories)")

for row in cursor.fetchall():
    print(row)

conn.close()