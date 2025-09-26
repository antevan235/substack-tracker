# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

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
            # adjust columns to match your DB schema
            query = """
                SELECT newsletter, title, url, author, published, summary, image, fetched_at
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
        # empty placeholder
        df = pd.DataFrame(columns=["newsletter","title","url","author","published","summary","image","fetched_at"])

    # normalize columns
    for col in ["newsletter","title","url","author","summary","image","fetched_at"]:
        if col not in df.columns:
            df[col] = ""

    # parse published to datetime where possible
    if "published" in df.columns:
        df["published_dt"] = pd.to_datetime(df["published"], errors="coerce")
    else:
        df["published_dt"] = pd.NaT

    # ensure order newest first
    df = df.sort_values("published_dt", ascending=False).reset_index(drop=True)
    return df

df = load_data()

# ---------- SIDEBAR (filters & controls) ----------
st.sidebar.header("Filters & Controls")

# quick refresh (invalidates cache)
if st.sidebar.button("🔁 Reload data"):
    load_data.clear()
    df = load_data()
    st.experimental_rerun()

# date range default: last 90 days
max_date = df["published_dt"].max()
if pd.isna(max_date):
    max_date = datetime.utcnow()
default_start = (max_date - timedelta(days=90)).date() if max_date else (datetime.utcnow() - timedelta(days=90)).date()
start_date = st.sidebar.date_input("Start date", value=default_start)
end_date = st.sidebar.date_input("End date", value=max_date.date() if max_date else datetime.utcnow().date())

# newsletter filter
newsletter_list = sorted(df["newsletter"].dropna().unique().tolist())
selected_newsletters = st.sidebar.multiselect("Newsletters", options=newsletter_list, default=newsletter_list[:6] or newsletter_list)

# author filter
author_list = sorted(df["author"].dropna().unique().tolist())
selected_authors = st.sidebar.multiselect("Authors", options=author_list, default=[])

# keyword search
search = st.sidebar.text_input("Search (title / summary)", placeholder="type keywords to search")

# limit results
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

# date filter
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
filtered = filtered[(filtered["published_dt"] >= start_dt) & (filtered["published_dt"] <= end_dt)]

# newsletter filter
if selected_newsletters:
    filtered = filtered[filtered["newsletter"].isin(selected_newsletters)]

# author filter
if selected_authors:
    filtered = filtered[filtered["author"].isin(selected_authors)]

# search filter
if search:
    mask = (
        filtered["title"].fillna("").str.contains(search, case=False, na=False) |
        filtered["summary"].fillna("").str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]

# limit
filtered = filtered.head(max_rows)

# ---------- CHART & STATS ----------
st.subheader("Activity overview")
c1, c2 = st.columns([2,1])
with c1:
    # posts per newsletter bar chart
    posts_per = filtered.groupby("newsletter").size().sort_values(ascending=False)
    if not posts_per.empty:
        st.bar_chart(posts_per)
    else:
        st.info("No posts to chart for the current filters.")
with c2:
    st.write("### Top newsletters")
    st.write(posts_per.head(10).to_frame("posts") if not posts_per.empty else "—")

st.markdown("---")

# ---------- RESULTS TABLE ----------
st.subheader(f"Showing {len(filtered)} posts")
# columns to show in table
table_cols = ["newsletter", "title", "author", "published_dt", "url"]
if "summary" in filtered.columns:
    table_cols.insert(3, "summary")
display_table = filtered[table_cols].copy()
display_table = display_table.rename(columns={"published_dt":"published"})
# make URLs clickable in streamlit table by showing as link column later

st.dataframe(display_table.reset_index(drop=True), use_container_width=True)

# ---------- PER-POST PREVIEW (first N results) ----------
st.markdown("---")
st.subheader("Preview (first posts)")

preview_count = st.number_input("Number of post previews to show", min_value=1, max_value=20, value=5, step=1)
preview_df = filtered.head(preview_count).reset_index(drop=True)

for i, row in preview_df.iterrows():
    with st.expander(f"{i+1}. {row['title']} — {row['newsletter']} ({row['published_dt'].date() if pd.notna(row['published_dt']) else 'N/A'})", expanded=(i==0)):
        left, right = st.columns([3,1])
        with left:
            st.markdown(f"**{row['title']}**  \n")
            if row.get("author"):
                st.markdown(f"*By {row['author']}*")
            if row.get("published_dt") and pd.notna(row['published_dt']):
                st.markdown(f"**Published:** {row['published_dt'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if row.get("summary"):
                st.markdown(row["summary"], unsafe_allow_html=True)
            st.markdown(f"[Open original post]({row['url']})")
        with right:
            if row.get("image"):
                try:
                    st.image(row["image"], use_column_width=True)
                except Exception:
                    st.write("Image not available")
            else:
                st.write("No image")

# ---------- DOWNLOAD BUTTON ----------
st.markdown("---")
st.subheader("Export / Share")
export_df = filtered.copy()
if not export_df.empty:
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered CSV", data=csv_bytes, file_name="substack_filtered.csv", mime="text/csv")
else:
    st.write("No rows to export for the current filters.")

st.write("")
st.caption("Tip: To add or remove newsletters, edit newsletters.txt in the project folder (one base URL per line). Then run the fetch script to update the DB/CSV.")
