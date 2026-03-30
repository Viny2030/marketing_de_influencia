"""
db.py — DEPRECADO. Usar database.py para PostgreSQL.

Este módulo con SQLite se conserva temporalmente para no romper
importaciones existentes. Migrar a database.py en el próximo sprint.
"""
import warnings
warnings.warn(
    "db.py (SQLite) está deprecado. Usar database.py (PostgreSQL).",
    DeprecationWarning,
    stacklevel=2,
)

import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    device_id TEXT,
    campaign_id TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversions (
    user_id TEXT,
    value REAL,
    timestamp TEXT
)
""")

conn.commit()


def insert_event(device_id, campaign_id, timestamp):
    cursor.execute("INSERT INTO events VALUES (?, ?, ?)",
                   (device_id, campaign_id, str(timestamp)))
    conn.commit()


def insert_conversion(user_id, value, timestamp):
    cursor.execute("INSERT INTO conversions VALUES (?, ?, ?)",
                   (user_id, value, str(timestamp)))
    conn.commit()


def get_data():
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.execute("SELECT * FROM conversions")
    conversions = cursor.fetchall()
    return {
        "events": [
            {"device_id": e[0], "campaign_id": e[1], "timestamp": _parse_dt(e[2])}
            for e in events
        ],
        "conversions": [
            {"user_id": c[0], "value": c[1], "timestamp": _parse_dt(c[2])}
            for c in conversions
        ],
    }


def _parse_dt(dt):
    from datetime import datetime
    return datetime.fromisoformat(dt)
