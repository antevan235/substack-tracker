import sqlite3
import os

print(f"DB exists: {os.path.exists('output/substack.db')}")

if os.path.exists('output/substack.db'):
    conn = sqlite3.connect('output/substack.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM posts')
    count = cursor.fetchone()[0]
    print(f"Posts in database: {count}")
    
    if count > 0:
        cursor.execute('SELECT newsletter, COUNT(*) FROM posts GROUP BY newsletter')
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} posts")
    
    conn.close()
else:
    print("Database file doesn't exist!")