import sqlite3
import time
from datetime import datetime, timezone
import feedparser

DB_FILE = "substack.db"
FEED_LIST = "newsletters.txt"

def add_post(newsletter, title, url, author, published):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO posts (newsletter, title, url, author, published, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (newsletter, title, url, author, published, datetime.now(timezone.utc).isoformat()))
    except sqlite3.IntegrityError:
        pass  # Skip duplicates
    conn.commit()
    conn.close()

def parse_date(entry):
    if entry.get("published_parsed"):
        return time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
    return entry.get("published", "") or entry.get("updated", "")

def fetch_feed(url):
    rss_url = url.rstrip("/") + "/feed"
    print(f"Fetching: {rss_url}")
    feed = feedparser.parse(rss_url)

    newsletter = feed.feed.get("title", url)
    entries = feed.entries or []

    for entry in entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        author = entry.get("author", "Unknown")
        published = parse_date(entry)

        if title and link:
            add_post(newsletter, title, link, author, published)

    print(f"Stored {len(entries)} posts from {newsletter}")

def fetch_all():
    with open(FEED_LIST, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        fetch_feed(url)

if __name__ == "__main__":
    fetch_all()
