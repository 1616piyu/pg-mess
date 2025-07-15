# create_db.py

import sqlite3

con = sqlite3.connect("data.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS menu_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT,
    meal_type TEXT,
    food_items TEXT
)
""")

# Sample menu for 2 days (extend later)
weekly_data = [
    ('Monday', 'Breakfast', 'Poha, Tea'),
    ('Monday', 'Lunch', 'Dal, Rice, Bhindi'),
    ('Monday', 'Dinner', 'Roti, Paneer, Curd'),
    ('Tuesday', 'Breakfast', 'Idli, Sambar'),
    ('Tuesday', 'Lunch', 'Chole, Rice, Salad'),
    ('Tuesday', 'Dinner', 'Roti, Aloo, Buttermilk'),
]

# Insert only if table is empty
cur.execute("SELECT COUNT(*) FROM menu_schedule")
if cur.fetchone()[0] == 0:
    cur.executemany("INSERT INTO menu_schedule (day, meal_type, food_items) VALUES (?, ?, ?)", weekly_data)

con.commit()
con.close()
print("Database created and sample menu added.")
