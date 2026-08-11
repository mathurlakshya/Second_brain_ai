import sqlite3

conn = sqlite3.connect("second_brain.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE memories ADD COLUMN embedding TEXT")

conn.commit()
conn.close()

print("Done")