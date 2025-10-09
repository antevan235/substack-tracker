import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import pytz
from dataclasses import dataclass
from contextlib import contextmanager

# Configuration
@dataclass
class Config:
    """Application configuration"""
    DB_FILE: str = "output/substack.db"
    CSV_FILE: str = "output/substack_posts.csv"
    DEFAULT_DAYS: int = 90
    MIN_ROWS: int = 10
    MAX_ROWS: int = 2000
    DEFAULT_ROWS: int = 200
    PAGE_TITLE: str = "Substack Tracker"
    CACHE_TTL: int = 60  # seconds

# Initialize config and page
config = Config()
st.set_page_config(
    page_title=config.PAGE_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

class DataManager:
    """Handles all data operations"""
    
    @contextmanager
    def _db_connection(self):
        """Database connection context manager"""
        conn = sqlite3.connect(config.DB_FILE)
        try:
            yield conn
        finally:
            conn.close()

    @st.cache_data(ttl=config.CACHE_TTL)
    def load_data(_self) -> pd.DataFrame:
        """Load and prepare data from database or CSV"""
        df = _self._load_from_source()
        return _self._prepare_dataframe(df)

    def _load_from_source(self) -> pd.DataFrame:
        """Load data from DB or CSV"""
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
        """Prepare and clean dataframe"""
        # Ensure required columns exist
        for col in ["newsletter", "title", "url", "author", 
                   "summary", "image", "fetched_at"]:
            df[col] = df.get(col, "")

        # Convert published dates to UTC
        df["published_dt"] = pd.to_datetime(
            df.get("published"), 
            errors="coerce"
        ).dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')

        return df.sort_values("published_dt", ascending=False).reset_index(drop=True)

    def load_uploaded_csv(self, file) -> pd.DataFrame:
        """Process uploaded CSV file"""
        df = pd.read_csv(file)
        df["published_dt"] = pd.to_datetime(
            df.get("published"), 
            errors="coerce"
        ).dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
        return df

class Dashboard:
    """Main dashboard interface"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.df = self.data_manager.load_data()

    def render_sidebar(self) -> tuple:
        """Render sidebar filters"""
        st.sidebar.header("Filters & Controls")

        if st.sidebar.button("🔁 Reload data"):
            self.data_manager.load_data.clear()
            self.df = self.data_manager.load_data()
            st.experimental_rerun()

        # Date filters
        max_date = self.df["published_dt"].max() or datetime.now(pytz.UTC)
        default_start = (max_date - timedelta(days=config.DEFAULT_DAYS)).date()
        dates = (
            st.sidebar.date_input("Start date", value=default_start),
            st.sidebar.date_input("End date", value=max_date.date())
        )

        # Newsletter and author filters
        newsletters = sorted(self.df["newsletter"].dropna().unique())
        authors = sorted(self.df["author"].dropna().unique())
        
        filters = {
            'newsletters': st.sidebar.multiselect(
                "Newsletters", 
                options=newsletters, 
                default=newsletters[:6] or newsletters
            ),
            'authors': st.sidebar.multiselect(
                "Authors", 
                options=authors
            ),
            'search': st.sidebar.text_input(
                "Search (title / summary)", 
                placeholder="type keywords to search"
            ),
            'max_rows': st.sidebar.number_input(
                "Max rows to show",
                min_value=config.MIN_ROWS,
                max_value=config.MAX_ROWS,
                value=config.DEFAULT_ROWS,
                step=10
            )
        }

        return dates, filters

    def render_metrics(self):
        """Render dashboard metrics"""
        st.title("📬 Substack Tracker")
        st.markdown("Live view of fetched Substack posts. Use the filters on the left to narrow results.")

        cols = st.columns([1.4, 1.0, 1.0, 1.0])
        
        metrics = [
            ("Newsletters tracked", self.df["newsletter"].nunique()),
            ("Total posts", len(self.df)),
            ("Most recent post", self.df["published_dt"].max().strftime("%Y-%m-%d") 
             if pd.notna(self.df["published_dt"].max()) else "N/A"),
            ("Last fetch (UTC)", self.df["fetched_at"].max() 
             if "fetched_at" in self.df.columns else "N/A")
        ]

        for col, (label, value) in zip(cols, metrics):
            with col:
                st.metric(label, value)

    def render_upload_section(self):
        """Render CSV upload section"""
        st.markdown("---")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        
        if not uploaded_file:
            st.info("Upload a CSV file to get started.")
            return

        df_uploaded = self.data_manager.load_uploaded_csv(uploaded_file)
        
        if "newsletter" not in df_uploaded.columns:
            st.error("CSV must have a column named 'newsletter'")
            return

        newsletter_list = sorted(df_uploaded["newsletter"].dropna().unique())
        selected_newsletter = st.selectbox("Select a newsletter", newsletter_list)
        
        filtered_df = df_uploaded[df_uploaded['newsletter'] == selected_newsletter]
        st.dataframe(filtered_df)

def main():
    """Main application entry point"""
    dashboard = Dashboard()
    dates, filters = dashboard.render_sidebar()
    dashboard.render_metrics()
    dashboard.render_upload_section()

if __name__ == "__main__":
    main()