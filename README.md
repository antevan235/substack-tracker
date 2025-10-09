# Substack Tracker

A Python application for tracking and analyzing Substack newsletters with an interactive Streamlit dashboard.

## Features

- 📊 Interactive Streamlit dashboard
- 🔄 Automated RSS feed fetching
- 💾 SQLite database storage
- 📈 Analytics and metrics
- 🔍 Full-text search
- 📅 Date range filtering
- 📤 CSV export functionality

## Project Structure

```
substack-tracker/
├── src/              # Source code
├── data/             # Input data (newsletters list)
└── output/           # Generated files (database, exports)
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Newsletters
Add newsletter URLs to `data/newsletters.txt` (one per line):
```
https://example.substack.com
https://another.substack.com
```

### 3. Initialize Database
```bash
python src/db_setup.py
```

### 4. Fetch Newsletter Data
```bash
python src/fetch_to_db.py
```

### 5. Launch Dashboard
```bash
streamlit run src/dashboard.py
```

The dashboard will open at `http://localhost:8501`

## Scripts

- **`src/db_setup.py`** - Initialize the database schema
- **`src/fetch_to_db.py`** - Fetch posts from RSS feeds to database
- **`src/fetch_with_content.py`** - Fetch posts with full content
- **`src/export_to_csv.py`** - Export database to CSV
- **`src/dashboard.py`** - Launch the Streamlit dashboard

## Data Storage

- **Input**: `data/newsletters.txt` - List of newsletter URLs
- **Output**: `output/substack.db` - SQLite database
- **Output**: `output/substack_posts.csv` - CSV exports

## Development

This project follows Python best practices with organized directory structure:
- All source code in `src/`
- Configuration data in `data/`
- Generated files in `output/` (gitignored)
