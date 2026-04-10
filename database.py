import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'pantry.db')


def get_db():
    """Open a database connection and return it with Row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables and load seed data if the DB does not exist yet."""
    conn = get_db()
    base = os.path.dirname(__file__)

    with open(os.path.join(base, 'schema.sql'), 'r') as f:

        conn.executescript(f.read())

    with open(os.path.join(base, 'seed.sql'), 'r') as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()
