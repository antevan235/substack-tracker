import sqlite3
from datetime import datetime, timezone
import feedparser
from dateutil import parser as date_parser
import time
import difflib
import os

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

# --- Add multiple posts to DB at once ---
def add_posts(posts):
    if not posts:
        return 0
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    inserted = 0
    for post in posts:
        try:
            c.execute("""
                INSERT INTO posts (newsletter, title, url, author, published, summary, tags, word_count, image_url, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post["newsletter"], post["title"], post["url"], post["author"], post["published"],
                post["summary"], post["tags"], post["word_count"], post["image_url"],
                datetime.now(timezone.utc).isoformat()
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # Skip duplicates by URL
    conn.commit()
    conn.close()
    return inserted

# --- Check for near-duplicate titles ---
def is_similar_title(title, newsletter):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT title FROM posts WHERE newsletter = ?", (newsletter,))
    existing_titles = [row[0] for row in c.fetchall()]
    conn.close()

    for existing in existing_titles:
        if difflib.SequenceMatcher(None, title, existing).ratio() > 0.9:
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
            return date_str
    return ""

# --- Fetch a single RSS feed ---
def fetch_feed(url):
    # Handle feed URL correctly
    if not url.endswith((".rss", "/feed")):
        rss_url = url.rstrip("/") + "/feed?limit=60"  # fetch up to 60 posts for Substack
    else:
        rss_url = url

    print(f"\nFetching: {rss_url}")
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        print(f"Error parsing feed {rss_url}: {feed.bozo_exception}")
        return

    newsletter = feed.feed.get("title", url)
    entries = feed.entries or []
    posts_to_add = []

    for entry in entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        author = entry.get("author") or feed.feed.get("author") or newsletter
        published = parse_date(entry)
        summary = entry.get("summary", "").strip()
        tags_list = [tag['term'] for tag in entry.get('tags', [])]
        tags = ", ".join(tags_list)
        word_count = len(summary.split())
        image_url = entry.get("media_content", [{}])[0].get("url", "")

        # Skip if duplicate URL or near-duplicate title
        if title and link and not is_similar_title(title, newsletter):
            posts_to_add.append({
                "newsletter": newsletter,
                "title": title,
                "url": link,
                "author": author,
                "published": published,
                "summary": summary,
                "tags": tags,
                "word_count": word_count,
                "image_url": image_url
            })

    inserted_count = add_posts(posts_to_add)
    print(f"Inserted {inserted_count}/{len(entries)} posts from {newsletter}")

# --- Fetch all feeds from the list ---
def fetch_all():
    if not os.path.exists(FEED_LIST):
        print(f"{FEED_LIST} not found. Please create it with one feed URL per line.")
        return

    with open(FEED_LIST, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            fetch_feed(url)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

# --- Main execution ---
if __name__ == "__main__":
    init_db()
    fetch_all()
