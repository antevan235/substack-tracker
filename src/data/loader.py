"""Data loading and preparation functionality."""

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
    with caching support for improved performance.
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

    @st.cache_data(ttl=config.CACHE_TTL)
    def load_data(_self) -> pd.DataFrame:
        """Load and prepare data from database or CSV.
        
        Returns:
            pd.DataFrame: Prepared dataframe with cleaned and sorted data
        """
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
