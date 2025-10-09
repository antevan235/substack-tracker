import sqlite3
import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser
from typing import List, Dict, Any, Optional
import logging
from contextlib import contextmanager
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from urllib.parse import urljoin

# Configuration
CONFIG = {
    'DB_FILE': 'output/substack.db',
    'FEED_LIST': 'data/newsletters.txt',
    'BATCH_SIZE': 50,
    'MAX_WORKERS': 4,
    'POSTS_LIMIT': 60,
    'TITLE_SIMILARITY': 0.9
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Post:
    """Data structure for blog posts"""
    newsletter: str
    title: str
    url: str
    author: str
    published: str
    summary: str
    tags: str
    word_count: int
    image_url: str

class Database:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._initialize()

    @contextmanager
    def connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_file)
        try:
            yield conn
        finally:
            conn.close()

    def _initialize(self):
        """Initialize database with indexes"""
        with self.connection() as conn:
            conn.executescript('''
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
                );
                CREATE INDEX IF NOT EXISTS idx_url ON posts(url);
                CREATE INDEX IF NOT EXISTS idx_newsletter_title ON posts(newsletter, title);
            ''')

    def insert_posts(self, posts: List[Post]) -> int:
        """Batch insert posts into database"""
        if not posts:
            return 0

        with self.connection() as conn:
            values = [(
                post.newsletter, post.title, post.url, post.author,
                post.published, post.summary, post.tags,
                post.word_count, post.image_url,
                datetime.now(timezone.utc).isoformat()
            ) for post in posts]

            return conn.executemany('''
                INSERT OR IGNORE INTO posts (
                    newsletter, title, url, author, published,
                    summary, tags, word_count, image_url, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', values).rowcount

    def get_titles(self, newsletter: str) -> List[str]:
        """Get existing titles for duplicate checking"""
        with self.connection() as conn:
            return [row[0] for row in conn.execute(
                "SELECT title FROM posts WHERE newsletter = ?", 
                (newsletter,)
            )]

class FeedProcessor:
    def __init__(self, db: Database):
        self.db = db

    def process_feed(self, url: str) -> Optional[int]:
        """Process a single feed URL"""
        try:
            feed_url = self._normalize_url(url)
            logger.info(f"Fetching: {feed_url}")
            
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logger.error(f"Feed parse error {feed_url}: {feed.bozo_exception}")
                return None

            newsletter = feed.feed.get("title", url)
            existing_titles = self.db.get_titles(newsletter)
            posts = self._process_entries(feed.entries, feed, newsletter, existing_titles)
            
            inserted = self.db.insert_posts(posts)
            logger.info(f"Inserted {inserted}/{len(feed.entries)} posts from {newsletter}")
            return inserted

        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Ensure URL is in correct format"""
        if not url.endswith((".rss", "/feed")):
            return urljoin(url.rstrip("/"), f"/feed?limit={CONFIG['POSTS_LIMIT']}")
        return url

    @staticmethod
    def _parse_date(entry: Dict[str, Any]) -> str:
        """Extract and parse date from entry"""
        for field in ['published', 'updated']:
            if date_str := entry.get(field):
                try:
                    return date_parser.parse(date_str).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    continue
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _process_entries(
        self, 
        entries: List[Dict], 
        feed: Any, 
        newsletter: str,
        existing_titles: List[str]
    ) -> List[Post]:
        """Process feed entries into Post objects"""
        from difflib import SequenceMatcher
        posts = []

        for entry in entries:
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()
            
            if not (title and url) or any(
                SequenceMatcher(None, title, existing).ratio() > CONFIG['TITLE_SIMILARITY']
                for existing in existing_titles
            ):
                continue

            posts.append(Post(
                newsletter=newsletter,
                title=title,
                url=url,
                author=entry.get("author") or feed.feed.get("author") or newsletter,
                published=self._parse_date(entry),
                summary=entry.get("summary", "").strip(),
                tags=", ".join(tag['term'] for tag in entry.get('tags', [])),
                word_count=len(entry.get("summary", "").split()),
                image_url=entry.get("media_content", [{}])[0].get("url", "")
            ))

        return posts

def main():
    """Main execution function"""
    if not os.path.exists(CONFIG['FEED_LIST']):
        logger.error(f"Feed list {CONFIG['FEED_LIST']} not found")
        return

    db = Database(CONFIG['DB_FILE'])
    processor = FeedProcessor(db)

    with open(CONFIG['FEED_LIST'], 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    with ThreadPoolExecutor(max_workers=CONFIG['MAX_WORKERS']) as executor:
        list(executor.map(processor.process_feed, urls))

if __name__ == "__main__":
    main()