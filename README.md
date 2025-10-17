# Substack Tracker

This is a simple Streamlit app I built to track and organize Substack newsletters (and other RSS feeds) without digging through endless tabs or emails.

It fetches posts automatically, stores them in a small database, and gives you a clean dashboard to search, filter, and export resultsm, all directly in your browser.

---

## 🚀 How to Use (No Local Setup Needed)

You can run the app directly online here:  
👉 **[Streamlit App Link] [(https://your-streamlit-url-here.streamlit.app](https://substack-tracker-s8apev8vkp8usqxnof6hmm.streamlit.app/))**

Once it loads, it will automatically:
- Fetch and store posts from the feeds listed in `data/newsletters.txt`
- Display them in a searchable, filterable Streamlit dashboard
- Let you export results as a CSV

If you ever want to **update which newsletters it tracks**, just:

1. Open the file:  
   `data/newsletters.txt`
2. Add or remove any feed URLs (one per line)
3. Refresh the app — it’ll automatically reload with the new data

Example entries in `data/newsletters.txt`:

---

## 🧩 What It Does
- Pulls posts from Substack + RSS feeds
- Stores them in an internal SQLite database
- Lets you search,and filter content
- Runs fully in the browser — no installs or scripts needed

---

## 📂 Repo Layout

---

## 🛠️ Developer Notes (Optional)
If you want to run it locally:
```bash
git clone https://github.com/antevan235/substack-tracker.git
cd substack-tracker
pip install -r requirements.txt
streamlit run src/dashboard.py

```
---
## ✅ What’s Improved
- Focused entirely on the *Streamlit Cloud workflow*
- Highlighted `data/newsletters.txt` as the **main interaction point**
- Simplified steps for non-technical users.
- Still includes optional developer setup for future contributors
