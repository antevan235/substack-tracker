from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class Config:
    """Application configuration"""
    # Database
    DB_FILE: str = "substack.db"
    DB_URL: str = f"sqlite:///{DB_FILE}"
    
    # Files
    FEED_LIST: str = "newsletters.txt"
    DATA_DIR: Path = Path("data")
    
    # Fetch settings
    MAX_WORKERS: int = 4
    FEED_LIMIT: int = 50
    BATCH_SIZE: int = 100
    
    # Dashboard settings
    PAGE_TITLE: str = "Substack Tracker"
    CACHE_TTL: int = 60
    
    @staticmethod
    def get_utc_now() -> str:
        """Get current UTC timestamp"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

config = Config()