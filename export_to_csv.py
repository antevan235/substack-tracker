import sqlite3
import pandas as pd

# Connect to your database
conn = sqlite3.connect("substack.db")

# Read all posts ordered by newest first
df = pd.read_sql_query("SELECT * FROM posts ORDER BY published DESC", conn)

# Save to CSV
df.to_csv("latest_posts.csv", index=False)

conn.close()

print("Exported latest_posts.csv")
# Count posts per newsletter
summary = df.groupby("newsletter").size().reset_index(name="num_posts")
summary = summary.sort_values("num_posts", ascending=False)
print(summary)
