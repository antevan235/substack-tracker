import sqlite3
from datetime import datetime, timezone
import feedparser
from dateutil import parser as date_parser  # <- new import
import time

DB_FILE = "substack.db"
FEED_LIST = "newsletters.txt"

# --- Make sure table exists first ---
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

# --- Add posts ---
def add_post(newsletter, title, url, author, published, summary="", tags="", word_count=0, image_url=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO posts (newsletter, title, url, author, published, summary, tags, word_count, image_url, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            newsletter, title, url, author, published, summary, tags, word_count, image_url,
            datetime.now(timezone.utc).isoformat()
        ))
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()

# --- Parse dates more robustly ---
def parse_date(entry):
    date_str = ""
    if entry.get("published"):
        date_str = entry["published"]
    elif entry.get("updated"):
        date_str = entry["updated"]
    elif entry.get("published_parsed"):
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
    
    if date_str:
        try:
            # Use dateutil to parse and convert to ISO
            dt = date_parser.parse(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return date_str  # fallback to original if parsing fails
    return ""

# --- Fetch RSS feeds ---
def fetch_feed(url):
    rss_url = url.rstrip("/") + "/feed"
    print(f"Fetching: {rss_url}")
    feed = feedparser.parse(rss_url)

    newsletter = feed.feed.get("title", url)
    entries = feed.entries or []

    for entry in entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        # --- Author detection ---
        author = entry.get("author") or feed.feed.get("author") or newsletter

        published = parse_date(entry)
        summary = entry.get("summary", "").strip()

        tags_list = [tag['term'] for tag in entry.get('tags', [])]
        tags = ", ".join(tags_list)

        word_count = len(summary.split())
        image_url = entry.get("media_content", [{}])[0].get("url", "")

        if title and link:
            add_post(newsletter, title, link, author, published, summary, tags, word_count, image_url)

    print(f"Stored {len(entries)} posts from {newsletter}")

# --- Fetch all feeds from list ---
def fetch_all():
    with open(FEED_LIST, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        fetch_feed(url)

if __name__ == "__main__":
    fetch_all()
