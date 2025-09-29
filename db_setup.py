import sqlite3

DB_FILE = "substack.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter TEXT,
            title TEXT,
            url TEXT UNIQUE,
            author TEXT,
            published TEXT,
            summary TEXT,
            tags TEXT,
            word_count INTEGER,
            image_url TEXT,
            fetched_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()
