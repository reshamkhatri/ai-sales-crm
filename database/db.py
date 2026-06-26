import sqlite3
import os
from config import DATABASE_PATH

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCHEMA_PATH = os.path.join(_HERE, "schema.sql")

# Ensure the DB directory exists (works regardless of working directory)
_db_dir = os.path.dirname(DATABASE_PATH)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with open(_SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    
    # Migration: Add tags column if it doesn't exist yet
    try:
        conn.execute("SELECT tags FROM leads LIMIT 1")
    except sqlite3.OperationalError:
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN tags TEXT")
            conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")

    # Migration: Add place_id column (Google Maps dedup) if it doesn't exist yet
    try:
        conn.execute("SELECT place_id FROM leads LIMIT 1")
    except sqlite3.OperationalError:
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN place_id TEXT")
            conn.commit()
        except Exception as e:
            print(f"Migration error (place_id): {e}")

    conn.close()

def execute(query, params=()):
    conn = get_connection()
    cursor = conn.execute(query, params)
    conn.commit()
    lastrowid = cursor.lastrowid
    conn.close()
    return lastrowid

def fetchone(query, params=()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None

def fetchall(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]
