# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import pytz  # for UTC localization

# ---------- CONFIG ----------
DB_FILE = "substack.db"
CSV_FILE = "substack_posts.csv"

st.set_page_config(page_title="Substack Tracker", layout="wide", initial_sidebar_state="expanded")

# ---------- DATA LOADING ----------
@st.cache_data(ttl=60)
def load_data():
    """
    Load posts from SQLite DB if available, otherwise from CSV.
    Returns DataFrame with normalized columns and parsed dates.
    """
    df = None
    if os.path.exists(DB_FILE):
        try:
            conn = sqlite3.connect(DB_FILE)
            query = """
                SELECT newsletter, title, url, author, published, summary, image_url as image, fetched_at
                FROM posts
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
        except Exception as e:
            st.warning(f"Error reading {DB_FILE}: {e}")
            df = None

    if df is None and os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception as e:
            st.warning(f"Error reading {CSV_FILE}: {e}")
            df = None

    if df is None:
        df = pd.DataFrame(columns=["newsletter","title","url","author","published","summary","image","fetched_at"])

    # normalize columns
    for col in ["newsletter","title","url","author","summary","image","fetched_at"]:
        if col not in df.columns:
            df[col] = ""

    # parse published to datetime (UTC-aware)
    if "published" in df.columns:
        df["published_dt"] = pd.to_datetime(df["published"], errors="coerce").dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT')
    else:
        df["published_dt"] = pd.NaT

    # newest first
    df = df.sort_values("published_dt", ascending=False).reset_index(drop=True)
    return df

df = load_data()

# ---------- SIDEBAR (filters & controls) ----------
st.sidebar.header("Filters & Controls")

if st.sidebar.button("🔁 Reload data"):
    load_data.clear()
    df = load_data()
    st.experimental_rerun()

max_date = df["published_dt"].max()
if pd.isna(max_date):
    max_date = datetime.utcnow().replace(tzinfo=pytz.UTC)
default_start = (max_date - timedelta(days=90)).date() if max_date else (datetime.utcnow() - timedelta(days=90)).date()

start_date = st.sidebar.date_input("Start date", value=default_start)
end_date = st.sidebar.date_input("End date", value=max_date.date() if max_date else datetime.utcnow().date())

# --- Newsletters filter
newsletter_list = sorted(df["newsletter"].dropna().unique().tolist())
selected_newsletters = st.sidebar.multiselect(
    "Newsletters", options=newsletter_list, default=newsletter_list[:6] or newsletter_list
)

# --- Authors filter
author_list = sorted(df["author"].dropna().unique().tolist())
selected_authors = st.sidebar.multiselect("Authors", options=author_list, default=[])

# --- Search and max rows
search = st.sidebar.text_input("Search (title / summary)", placeholder="type keywords to search")
max_rows = st.sidebar.number_input("Max rows to show", min_value=10, max_value=2000, value=200, step=10)

# ---------- TOP SUMMARY ----------
st.title("📬 Substack Tracker")
st.markdown("Live view of fetched Substack posts. Use the filters on the left to narrow results.")

col1, col2, col3, col4 = st.columns([1.4,1.0,1.0,1.0])
with col1:
    st.metric("Newsletters tracked", df["newsletter"].nunique())
with col2:
    st.metric("Total posts", len(df))
with col3:
    most_recent = df["published_dt"].max()
    st.metric("Most recent post", most_recent.strftime("%Y-%m-%d") if pd.notna(most_recent) else "N/A")
with col4:
    last_fetch = df["fetched_at"].max() if "fetched_at" in df.columns else None
    st.metric("Last fetch (UTC)", last_fetch if last_fetch else "N/A")

st.markdown("---")

# ---------- FILTERING ----------
filtered = df.copy()

# convert sideb
