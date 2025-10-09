from pathlib import Path
import sqlite3
from contextlib import contextmanager
from typing import Optional
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations and schema setup"""
    
    def __init__(self, db_path: str = "output/substack.db"):
        self.db_path = Path(db_path)
        self.schema = """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            newsletter TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            author TEXT,
            published TEXT NOT NULL,
            summary TEXT,
            tags TEXT,
            word_count INTEGER,
            image_url TEXT,
            fetched_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(url);
        CREATE INDEX IF NOT EXISTS idx_posts_newsletter ON posts(newsletter);
        CREATE INDEX IF NOT EXISTS idx_posts_published ON posts(published);
        CREATE INDEX IF NOT EXISTS idx_posts_author ON posts(author);
        """

    @contextmanager
    def connect(self) -> sqlite3.Connection:
        """Create database connection with context management"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def init_database(self) -> bool:
        """Initialize database schema with error handling"""
        try:
            with self.connect() as conn:
                conn.executescript(self.schema)
                logger.info(f"Database initialized successfully at {self.db_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False

    def verify_database(self) -> bool:
        """Verify database structure and accessibility"""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                # Check if posts table exists and has correct structure
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
                if not cursor.fetchone():
                    logger.error("Posts table not found")
                    return False
                
                # Verify table structure
                cursor.execute("PRAGMA table_info(posts)")
                columns = {row['name'] for row in cursor.fetchall()}
                required_columns = {
                    'id', 'newsletter', 'title', 'url', 'author',
                    'published', 'summary', 'tags', 'word_count',
                    'image_url', 'fetched_at', 'created_at'
                }
                
                if not required_columns.issubset(columns):
                    logger.error(f"Missing columns: {required_columns - columns}")
                    return False
                
                logger.info("Database verification successful")
                return True
                
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False

def main():
    """Main execution function"""
    try:
        db = DatabaseManager()
        
        if not db.init_database():
            logger.error("Failed to initialize database")
            sys.exit(1)
            
        if not db.verify_database():
            logger.error("Database verification failed")
            sys.exit(1)
            
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Unexpected error during database setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()