import sqlite3
import time
from datetime import datetime, timezone
import feedparser

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

init_db()  # run immediately so table exists

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
        pass  # Skip duplicates
    conn.commit()
    conn.close()

# --- Parse dates ---
def parse_date(entry):
    if entry.get("published_parsed"):
        return time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
    return entry.get("published", "") or entry.get("updated", "")

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
        author = (entry.get("author") or
                  (entry.get("dc_creator") 
                   if "dc_creator" 
                   in entry else None) or "Unknown")

        published = parse_date(entry)
        summary = entry.get("summary", "").strip()

        tags_list = [tag['term'] for tag in entry.get('tags', [])]
        tags = ", ".join(tags_list)

        word_count = len(summary.split())
        image_url = entry.get("media_content", [{}])[0].get("url", "")

        if title and link:
            add_post(newsletter, title, link, author, published, summary, tags, word_count, image_url)

    print(f"Stored {len(entries)} posts from {newsletter}")

def fetch_all():
    with open(FEED_LIST, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        fetch_feed(url)

if __name__ == "__main__":
    fetch_all()
