# init_db.py
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    fruit_type TEXT NOT NULL,
    weight REAL NOT NULL,
    price_per_kg REAL NOT NULL,
    total_price REAL NOT NULL,
    cold_storage_name TEXT NOT NULL,
    scale_cost REAL NOT NULL,
    net_price REAL NOT NULL,
    car_plate TEXT NOT NULL,
    driver_name TEXT NOT NULL,
    box_count INTEGER NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ جدول sales ساخته شد.")
