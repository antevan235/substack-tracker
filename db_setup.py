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
            fetched_at TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_FILE}")
