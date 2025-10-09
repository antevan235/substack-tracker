# Substack Tracker - Quick demo

## Run locally
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
python -m streamlit run dashboard.py

## Deploy (streamlit cloud)
1. Push repo to GitHub
2. Create app on Streamlit Community Cloud and select this repo
3. Set secrets in the Cloud UI if needed
