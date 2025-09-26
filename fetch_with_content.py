import feedparser
import pandas as pd
import os
from datetime import datetime, timezone

CSV_FILE = "substack_posts.csv"
NEWS_FILE = "newsletters.txt"

def parse_date(entry):
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
    return entry.get("published", "") or entry.get("updated", "")

def fetch_rss(newsletter_url):
    rss_url = newsletter_url.rstrip("/") + "/feed"
    print(f"Fetching RSS feed: {rss_url}")  # debug
    feed = feedparser.parse(rss_url)
    print(f"Number of entries found: {len(feed.entries)}")  # debug

    if not feed.entries:
        print(f"No entries found for {newsletter_url}. Skipping.")
        return []

    newsletter_name = feed.feed.get("title", newsletter_url)
    posts = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        author = entry.get("author", "Unknown")
        published = parse_date(entry)
        summary = entry.get("summary", "").strip()

        if title and link:
            post = {
                "newsletter": newsletter_name,
                "title": title,
                "url": link,
                "author": author,
                "published": published,
                "summary": summary,
                
            }
            posts.append(post)

    return posts

def fetch_all_newsletters():
    if not os.path.exists(NEWS_FILE):
        print(f"Create {NEWS_FILE} with newsletter URLs, one per line.")
        return []

    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    all_posts = []
    for url in urls:
        try:
            posts = fetch_rss(url)
            print(f"Fetched {len(posts)} posts from {url}")
            all_posts.extend(posts)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    return all_posts

def save_to_csv(posts):
    df = pd.DataFrame(posts)
    df.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(posts)} posts to {CSV_FILE}")

if __name__ == "__main__":
    posts = fetch_all_newsletters()
    if posts:
        save_to_csv(posts)
    else:
        print("No posts fetched.")
