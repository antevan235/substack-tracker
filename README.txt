# Substack Tracker Dashboard

A Streamlit dashboard for tracking and analyzing Substack newsletters.

## Features

- Real-time data loading from SQLite database or CSV
- Interactive filters for newsletters and authors
- Date range selection
- Full-text search
- CSV upload functionality
- Responsive metrics display

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run dashboard.py
```

## Configuration

The dashboard looks for:
- `substack.db`: SQLite database with posts
- `substack_posts.csv`: Fallback CSV file (optional)

## Deployment

### Local Development
```bash
streamlit run dashboard.py
```

### Docker Deployment
```bash
docker build -t substack-dashboard .
docker run -p 8501:8501 substack-dashboard
```
