import feedparser
import sqlite3
import os
from datetime import datetime, timezone

NEWS_FILE = "newsletters.txt"
DB_FILE = "substack.db"

# -----------------------------
# 1. Helper functions
# -----------------------------

def parse_date(entry):
    """
    Convert feed entry date to ISO format.
    
    Args:
        entry (dict): A single feed entry.
    
    Returns:
        str: ISO formatted date or empty string.
    """
    try:
        if entry.get("published_parsed"):
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        return entry.get("published", "") or entry.get("updated", "")
    except Exception as e:
        print(f"Error parsing date: {e}")
        return ""

def fetch_rss(newsletter_url):
    """
    Fetch posts from a Substack RSS feed.
    
    Args:
        newsletter_url (str): Base URL of the newsletter.
    
    Returns:
        list of dict: List of posts with keys: newsletter, title, url, author, published, summary.
    """
    rss_url = newsletter_url.rstrip("/") + "/feed"
    print(f"Fetching RSS feed: {rss_url}")
    
    try:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            print(f"No entries found for {newsletter_url}")
            return []

        newsletter_name = feed.feed.get("title", newsletter_url)
        posts = []
        for entry in feed.entries:
            post = {
                "newsletter": newsletter_name,
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", "").strip(),
                "author": entry.get("author", "Unknown"),
                "published": parse_date(entry),
                "summary": entry.get("summary", "").strip()
            }
            if post["title"] and post["url"]:
                posts.append(post)
        return posts
    except Exception as e:
        print(f"Failed to fetch {newsletter_url}: {e}")
        return []

def read_newsletters():
    """
    Read newsletter URLs from newsletters.txt
    
    Returns:
        list of str: URLs
    """
    if not os.path.exists(NEWS_FILE):
        print(f"{NEWS_FILE} not found. Please create it with newsletter URLs.")
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# -----------------------------
# 2. Database functions
# -----------------------------

def init_db():
    """Initialize SQLite database with posts table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        newsletter TEXT,
        title TEXT,
        url TEXT,
        author TEXT,
        published TEXT,
        summary TEXT,
        fetched_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_posts(posts):
    """
    Insert multiple posts into the database.
    
    Args:
        posts (list of dict): Posts to insert
    """
    if not posts:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for post in posts:
        cursor.execute("""
            INSERT INTO posts (newsletter, title, url, author, published, summary, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            post["newsletter"],
            post["title"],
            post["url"],
            post["author"],
            post["published"],
            post["summary"],
            datetime.now(timezone.utc).isoformat()
        ))
    conn.commit()
    conn.close()

# -----------------------------
# 3. Main script
# -----------------------------

def fetch_all_newsletters():
    """Fetch posts from all newsletters in newsletters.txt and insert into DB."""
    urls = read_newsletters()
    if not urls:
        return

    init_db()
    all_posts = []
    for url in urls:
        posts = fetch_rss(url)
        print(f"Fetched {len(posts)} posts from {url}")
        insert_posts(posts)
        all_posts.extend(posts)
    print(f"Total posts fetched: {len(all_posts)}")
    return all_posts

if __name__ == "__main__":
    fetch_all_newsletters()
