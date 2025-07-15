import sqlite3

conn = sqlite3.connect('data.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    meal_type TEXT,
    rating INTEGER,
    comment TEXT
)
''')

conn.commit()
conn.close()

print("✅ feedback table created.")
