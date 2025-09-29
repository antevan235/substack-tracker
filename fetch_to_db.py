import sqlite3
from datetime import datetime, timezone
import feedparser
from dateutil import parser as date_parser
import time
import difflib

DB_FILE = "substack.db"
FEED_LIST = "newsletters.txt"

# --- Initialize database ---
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

# --- Add post to DB ---
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
        pass  # Skip duplicates by URL
    conn.commit()
    conn.close()

# --- Check for near-duplicate titles ---
def is_similar_title(title, newsletter):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT title FROM posts WHERE newsletter = ?", (newsletter,))
    existing_titles = [row[0] for row in c.fetchall()]
    conn.close()

    for existing in existing_titles:
        similarity = difflib.SequenceMatcher(None, title, existing).ratio()
        if similarity > 0.9:  # >90% similar
            return True
    return False

# --- Parse date robustly ---
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
            dt = date_parser.parse(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return date_str  # fallback if parsing fails
    return ""

# --- Fetch a single RSS feed ---
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

        # Only add if not duplicate by URL or near-duplicate by title
        if title and link and not is_similar_title(title, newsletter):
            add_post(newsletter, title, link, author, published, summary, tags, word_count, image_url)

    print(f"Stored {len(entries)} posts from {newsletter}")

# --- Fetch all feeds from the list ---
def fetch_all():
    with open(FEED_LIST, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        fetch_feed(url)

# --- Main execution ---
if __name__ == "__main__":
    init_db()   # ensure table exists
    fetch_all()
