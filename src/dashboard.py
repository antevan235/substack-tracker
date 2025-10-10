"""Substack Tracker Dashboard - Main application entry point.

This module orchestrates the Streamlit dashboard, coordinating between
data loading, analytics calculations, and UI rendering.
"""

import streamlit as st

from config import Config
from data.loader import DataManager
from ui.components import render_sidebar, render_metrics
from ui.tabs import render_newsletter_directory
from ui.actions import render_contact_export_tab

# Initialize config and page
config = Config()
st.set_page_config(
    page_title=config.PAGE_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

def main() -> None:
    """Main application entry point.
    
    Orchestrates the dashboard by:
    1. Loading data via DataManager
    2. Rendering sidebar with filters
    3. Displaying top-level metrics
    4. Creating tabbed interface with various views
    """
    # Initialize data manager and load data
    data_manager = DataManager()
    df = data_manager.load_data()
    
    # Render sidebar and get filter values
    dates, filters = render_sidebar(df, data_manager)
    
    # Render top-level metrics
    render_metrics(df)
    
    # Create tabbed interface
    tab1, tab2, tab3, tab4 = st.tabs([
        "📬 Newsletter Directory",
        "👤 Author Profiles (Coming Soon)",
        "📊 Content Analysis (Coming Soon)",
        "📤 Contact Export (Coming Soon)"
    ])
    
    with tab1:
        render_newsletter_directory(df)
    
    with tab2:
        st.info("Author Profiles feature coming soon!")
    
    with tab3:
        st.info("Content Analysis feature coming soon!")
    
    with tab4:
        render_contact_export_tab(df)


if __name__ == "__main__":
    main()