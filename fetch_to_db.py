from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import sqlite3
from datetime import datetime, timezone
import feedparser
from dateutil import parser as date_parser
import time
import difflib
import os
import logging
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
CONFIG = {
    'DB_FILE': "substack.db",
    'FEED_LIST': "newsletters.txt",
    'SIMILARITY_THRESHOLD': 0.9,
    'MAX_POSTS_PER_FEED': 60,
    'BATCH_SIZE': 50,
    'MAX_WORKERS': 4
}

@dataclass
class Post:
    """Data class for blog posts"""
    newsletter: str
    title: str
    url: str
    author: str
    published: str
    summary: str
    tags: str
    word_count: int
    image_url: str
    fetched_at: str = ''

class DatabaseManager:
    """Handles all database operations"""
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema"""
        with self.get_connection() as conn:
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
            # Add indexes for better query performance
            c.execute("CREATE INDEX IF NOT EXISTS idx_url ON posts(url)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_newsletter ON posts(newsletter)")
            conn.commit()

    def add_posts_batch(self, posts: List[Post]) -> int:
        """Add multiple posts to database in a single transaction"""
        if not posts:
            return 0

        with self.get_connection() as conn:
            c = conn.cursor()
            inserted = 0
            
            # Use executemany for better performance
            values = [(
                post.newsletter, post.title, post.url, post.author,
                post.published, post.summary, post.tags,
                post.word_count, post.image_url,
                datetime.now(timezone.utc).isoformat()
            ) for post in posts]
            
            c.executemany("""
                INSERT OR IGNORE INTO posts (
                    newsletter, title, url, author, published,
                    summary, tags, word_count, image_url, fetched_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, values)
            
            inserted = c.rowcount
            conn.commit()
            return inserted

    def get_existing_titles(self, newsletter: str) -> List[str]:
        """Get existing titles for a newsletter"""
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT title FROM posts WHERE newsletter = ?", (newsletter,))
            return [row[0] for row in c.fetchall()]

class FeedProcessor:
    """Handles RSS feed processing"""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    @staticmethod
    def normalize_feed_url(url: str) -> str:
        """Normalize feed URL to ensure proper format"""
        if not url.endswith((".rss", "/feed")):
            return urljoin(url.rstrip("/"), f"/feed?limit={CONFIG['MAX_POSTS_PER_FEED']}")
        return url

    @staticmethod
    def parse_date(entry: Dict[str, Any]) -> str:
        """Parse date from feed entry"""
        date_fields = ['published', 'updated']
        for field in date_fields:
            if entry.get(field):
                try:
                    dt = date_parser.parse(entry[field])
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
        
        if entry.get('published_parsed'):
            return time.strftime("%Y-%m-%d %H:%M:%S", entry.published_parsed)
        
        return ""

    def is_similar_title(self, title: str, existing_titles: List[str]) -> bool:
        """Check if a title is similar to existing ones"""
        return any(
            difflib.SequenceMatcher(None, title, existing).ratio() > 
            CONFIG['SIMILARITY_THRESHOLD']
            for existing in existing_titles
        )

    def process_feed(self, url: str) -> Optional[int]:
        """Process a single feed"""
        try:
            rss_url = self.normalize_feed_url(url)
            logger.info(f"Fetching: {rss_url}")
            
            feed = feedparser.parse(rss_url)
            if feed.bozo:
                logger.error(f"Error parsing feed {rss_url}: {feed.bozo_exception}")
                return None

            newsletter = feed.feed.get("title", url)
            existing_titles = self.db_manager.get_existing_titles(newsletter)
            posts_to_add = []

            for entry in feed.entries:
                post = self._create_post_from_entry(entry, feed, newsletter)
                if post and not self.is_similar_title(post.title, existing_titles):
                    posts_to_add.append(post)

                if len(posts_to_add) >= CONFIG['BATCH_SIZE']:
                    self.db_manager.add_posts_batch(posts_to_add)
                    posts_to_add = []

            # Insert remaining posts
            inserted_count = self.db_manager.add_posts_batch(posts_to_add)
            logger.info(f"Inserted {inserted_count}/{len(feed.entries)} posts from {newsletter}")
            return inserted_count

        except Exception as e:
            logger.error(f"Error processing feed {url}: {e}")
            return None

    def _create_post_from_entry(
        self, entry: Dict[str, Any], feed: Any, newsletter: str
    ) -> Optional[Post]:
        """Create a Post object from feed entry"""
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        if not (title and link):
            return None

        return Post(
            newsletter=newsletter,
            title=title,
            url=link,
            author=entry.get("author") or feed.feed.get("author") or newsletter,
            published=self.parse_date(entry),
            summary=entry.get("summary", "").strip(),
            tags=", ".join(tag['term'] for tag in entry.get('tags', [])),
            word_count=len(entry.get("summary", "").split()),
            image_url=entry.get("media_content", [{}])[0].get("url", "")
        )

def main():
    """Main execution function"""
    if not os.path.exists(CONFIG['FEED_LIST']):
        logger.error(f"{CONFIG['FEED_LIST']} not found. Please create it with one feed URL per line.")
        return

    db_manager = DatabaseManager(CONFIG['DB_FILE'])
    processor = FeedProcessor(db_manager)

    with open(CONFIG['FEED_LIST'], "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Process feeds in parallel
    with ThreadPoolExecutor(max_workers=CONFIG['MAX_WORKERS']) as executor:
        executor.map(processor.process_feed, urls)

if __name__ == "__main__":
    main()