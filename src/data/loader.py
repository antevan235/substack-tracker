"""Data loading and preparation functionality."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from config import Config

config = Config()


class DataManager:
    """Handles all data loading and preparation operations.
    
    This class manages data loading from SQLite database or CSV files,
    with caching support for improved performance and automatic initialization.
    """
    
    @contextmanager
    def _db_connection(self):
        """Database connection context manager.
        
        Yields:
            sqlite3.Connection: Database connection object
        """
        conn = sqlite3.connect(config.DB_FILE)
        try:
            yield conn
        finally:
            conn.close()

    def _check_database_has_data(self) -> bool:
        """Check if database exists and has posts.
        
        Returns:
            bool: True if database exists and has data
        """
        if not Path(config.DB_FILE).exists():
            return False
        
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM posts")
                count = cursor.fetchone()[0]
                return count > 0
        except Exception:
            return False

    def _auto_initialize_if_needed(self) -> bool:
        """Automatically initialize database and fetch data if needed.
        
        Returns:
            bool: True if initialization successful or not needed
        """
        # Check if we already have data
        if self._check_database_has_data():
            return True
        
        st.info("🔧 Initializing database for first use...")
        
        try:
            # Create output directory if needed
            output_dir = Path(config.DB_FILE).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize database schema
            from db_setup import DatabaseManager
            db_manager = DatabaseManager(config.DB_FILE)
            if not db_manager.init_database():
                st.error("Failed to initialize database schema")
                return False
            
            # Fetch newsletter data
            st.info("📥 Fetching newsletter data (this may take a minute)...")
            
            from fetch_to_db import Database, FeedProcessor
            
            # Check if newsletters.txt exists
            feed_list = Path("data/newsletters.txt")
            if not feed_list.exists():
                st.warning("No newsletters configured in data/newsletters.txt")
                return True  # Database is initialized, just no feeds to fetch
            
            # Read newsletter URLs
            with open(feed_list, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                st.warning("No newsletter URLs found in data/newsletters.txt")
                return True
            
            # Fetch data from newsletters
            db = Database(config.DB_FILE)
            processor = FeedProcessor(db)
            
            total_inserted = 0
            for url in urls:
                inserted = processor.process_feed(url)
                if inserted:
                    total_inserted += inserted
            
            st.success(f"✅ Database initialized! Fetched {total_inserted} posts from {len(urls)} newsletters.")
            return True
            
        except Exception as e:
            st.error(f"Error during initialization: {e}")
            return False

    @st.cache_data(ttl=config.CACHE_TTL)
    def load_data(_self) -> pd.DataFrame:
        """Load and prepare data from database or CSV.
        
        Automatically initializes database and fetches data if needed.
        
        Returns:
            pd.DataFrame: Prepared dataframe with cleaned and sorted data
        """
        # Auto-initialize if needed (first time or empty database)
        _self._auto_initialize_if_needed()
        
        df = _self._load_from_source()
        return _self._prepare_dataframe(df)

    def _load_from_source(self) -> pd.DataFrame:
        """Load data from database or CSV file.
        
        Attempts to load from database first, falls back to CSV,
        and returns empty dataframe if neither source is available.
        
        Returns:
            pd.DataFrame: Raw data from source
        """
        try:
            if Path(config.DB_FILE).exists():
                with self._db_connection() as conn:
                    return pd.read_sql_query("""
                        SELECT 
                            newsletter, title, url, author, 
                            published, summary, image_url as image, 
                            fetched_at
                        FROM posts
                    """, conn)
        except Exception as e:
            st.warning(f"Database error: {e}")

        try:
            if Path(config.CSV_FILE).exists():
                return pd.read_csv(config.CSV_FILE)
        except Exception as e:
            st.warning(f"CSV error: {e}")

        return pd.DataFrame(columns=[
            "newsletter", "title", "url", "author",
            "published", "summary", "image", "fetched_at"
        ])

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean dataframe.
        
        Args:
            df: Raw dataframe from source
            
        Returns:
            pd.DataFrame: Cleaned and prepared dataframe
        """
        # Ensure required columns exist
        for col in ["newsletter", "title", "url", "author", 
                   "summary", "image", "fetched_at"]:
            df[col] = df.get(col, "")

        # Convert published dates to UTC
        df["published_dt"] = pd.to_datetime(
            df.get("published"), 
            errors="coerce"
        ).dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')

        return df.sort_values("published_dt", ascending=False).reset_index(
            drop=True
        )

    def load_uploaded_csv(self, file: Any) -> pd.DataFrame:
        """Process uploaded CSV file.
        
        Args:
            file: Uploaded file object from Streamlit file_uploader
            
        Returns:
            pd.DataFrame: Processed dataframe with UTC timestamps
        """
        df = pd.read_csv(file)
        df["published_dt"] = pd.to_datetime(
            df.get("published"), 
            errors="coerce"
        ).dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
        return df
