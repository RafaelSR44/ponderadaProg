"""
seed.py – Popula o banco com 35 leituras de exemplo distribuídas no tempo.
Execute uma única vez: python seed.py
"""

import random
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "estacao.db")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("""
    CREATE TABLE IF NOT EXISTS leituras (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        temperatura REAL    NOT NULL,
        umidade     REAL    NOT NULL,
        pressao     REAL,
        localizacao TEXT    DEFAULT 'Inteli - São Paulo',
        timestamp   DATETIME DEFAULT (datetime('now','localtime'))
    )
""")

base_time = datetime.now() - timedelta(hours=35)
rows = []
for i in range(35):
    ts   = base_time + timedelta(hours=i)
    temp = round(random.uniform(18.0, 35.0), 1)
    umid = round(random.uniform(40.0, 90.0), 1)
    pres = round(random.uniform(1000.0, 1025.0), 1)
    rows.append((temp, umid, pres, "Inteli - São Paulo", ts.strftime("%Y-%m-%d %H:%M:%S")))

conn.executemany(
    "INSERT INTO leituras (temperatura, umidade, pressao, localizacao, timestamp) VALUES (?,?,?,?,?)",
    rows,
)
conn.commit()
conn.close()
print(f"35 leituras inseridas em {DB_PATH}")
