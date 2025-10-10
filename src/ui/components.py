"""Reusable UI components for the dashboard."""

from datetime import datetime, timedelta
from typing import Dict, Tuple

import pandas as pd
import pytz
import streamlit as st

from config import Config
from data.loader import DataManager

config = Config()


def render_sidebar(
    df: pd.DataFrame, 
    data_manager: DataManager
) -> Tuple[Tuple, Dict]:
    """Render sidebar with filters and controls.
    
    Args:
        df: Main dataframe containing all posts
        data_manager: DataManager instance for reload functionality
        
    Returns:
        Tuple containing:
        - dates: Tuple of (start_date, end_date)
        - filters: Dict with newsletter, author, search, and max_rows filters
    """
    st.sidebar.header("Filters & Controls")

    if st.sidebar.button("🔁 Reload data"):
        data_manager.load_data.clear()
        st.rerun()

    # Date filters - handle NaT values with fallback
    try:
        max_date_raw = df["published_dt"].max()
        if pd.isna(max_date_raw):
            max_date = datetime.now(pytz.UTC)
            default_start = (
                max_date - timedelta(days=config.DEFAULT_DAYS)
            ).date()
        else:
            max_date = max_date_raw
            default_start = (
                max_date - timedelta(days=config.DEFAULT_DAYS)
            ).date()
    except Exception as e:
        st.sidebar.warning(f"Date filter error: {e}")
        max_date = datetime.now(pytz.UTC)
        default_start = (max_date - timedelta(days=config.DEFAULT_DAYS)).date()

    dates = (
        st.sidebar.date_input("Start date", value=default_start),
        st.sidebar.date_input("End date", value=max_date.date())
    )

    # Newsletter and author filters
    newsletters = sorted(df["newsletter"].dropna().unique())
    authors = sorted(df["author"].dropna().unique())
    
    filters = {
        'newsletters': st.sidebar.multiselect(
            "Newsletters", 
            options=newsletters, 
            default=(
                newsletters[:6] if len(newsletters) > 6 else newsletters
            )
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


def render_metrics(df: pd.DataFrame) -> None:
    """Render top-level dashboard metrics.
    
    Args:
        df: Main dataframe containing all posts
    """
    st.title("📬 Substack Tracker")
    st.markdown(
        "Live view of fetched Substack posts. "
        "Use the filters on the left to narrow results."
    )

    cols = st.columns([1.4, 1.0, 1.0, 1.0])
    
    metrics = [
        ("Newsletters tracked", df["newsletter"].nunique()),
        ("Total posts", len(df)),
        (
            "Most recent post", 
            (
                df["published_dt"].max().strftime("%Y-%m-%d") 
                if pd.notna(df["published_dt"].max()) else "N/A"
            )
        ),
        (
            "Last fetch (UTC)", 
            (
                df["fetched_at"].max() 
                if "fetched_at" in df.columns else "N/A"
            )
        )
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label, value)
