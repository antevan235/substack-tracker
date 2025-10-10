"""Configuration settings for Substack Tracker application."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration settings.
    
    Attributes:
        DB_FILE: Path to SQLite database file
        CSV_FILE: Path to CSV export file
        DEFAULT_DAYS: Default number of days for date range filter
        MIN_ROWS: Minimum number of rows to display
        MAX_ROWS: Maximum number of rows to display
        DEFAULT_ROWS: Default number of rows to display
        PAGE_TITLE: Application page title
        CACHE_TTL: Cache time-to-live in seconds
    """
    DB_FILE: str = "output/substack.db"
    CSV_FILE: str = "output/substack_posts.csv"
    DEFAULT_DAYS: int = 90
    MIN_ROWS: int = 10
    MAX_ROWS: int = 2000
    DEFAULT_ROWS: int = 200
    PAGE_TITLE: str = "Substack Tracker"
    CACHE_TTL: int = 60  # seconds
