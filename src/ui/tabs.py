"""Tab-specific rendering functions."""

import re
from typing import Dict

import pandas as pd
import streamlit as st

from analytics.insights import (
    get_hot_authors,
    get_going_cold,
    get_new_voices,
    get_rising_stars,
    calculate_posting_patterns,
    extract_email
)
from analytics.contacts import validate_twitter_handle
from data.loader import DataManager
from ui.actions import render_action_buttons


def render_newsletter_directory(df: pd.DataFrame) -> None:
    """Render Newsletter Directory tab with insights and details.
    
    Args:
        df: Main dataframe containing all posts
    """
    st.header("📬 Newsletter Directory")
    st.markdown(
        "Browse newsletters organized by publication → authors → contact info"
    )
    
    # Top-level stats
    cols = st.columns(4)
    
    # Total newsletters
    with cols[0]:
        st.metric("Total Newsletters", df["newsletter"].nunique())
    
    # Total unique authors
    with cols[1]:
        st.metric("Unique Authors", df["author"].dropna().nunique())
    
    # Most active newsletter (by post count)
    with cols[2]:
        if len(df) > 0:
            most_active = df["newsletter"].value_counts().iloc[0]
            most_active_name = df["newsletter"].value_counts().index[0]
            st.metric(
                "Most Active Newsletter", 
                f"{most_active_name[:20]}...", 
                delta=f"{most_active} posts"
            )
        else:
            st.metric("Most Active Newsletter", "N/A")
    
    # Most prolific author (by post count)
    with cols[3]:
        if len(df) > 0:
            author_counts = df[df["author"].notna()]["author"].value_counts()
            if len(author_counts) > 0:
                most_prolific = author_counts.iloc[0]
                most_prolific_name = author_counts.index[0]
                st.metric(
                    "Most Prolific Author", 
                    f"{most_prolific_name[:20]}...", 
                    delta=f"{most_prolific} posts"
                )
            else:
                st.metric("Most Prolific Author", "N/A")
        else:
            st.metric("Most Prolific Author", "N/A")
    
    st.markdown("---")
    
    # Actionable Insight Cards
    _render_insight_cards(df)
    
    st.markdown("---")
    
    # Newsletter cards with posting patterns
    _render_newsletter_details(df)


def _render_insight_cards(df: pd.DataFrame) -> None:
    """Render actionable insight cards.
    
    Args:
        df: Main dataframe containing all posts
    """
    st.markdown("## 🎯 Actionable Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 🔥 Hot Authors")
            st.markdown("_Best time to reach out - they're actively publishing!_")
            hot = get_hot_authors(df)
            if hot:
                for author in hot:
                    st.markdown(
                        f"**{author['author'][:40]}** - {author['count']} posts"
                    )
                    if author['email']:
                        st.markdown(f"📧 {author['email']}")
                        
                        # Get additional info for action buttons
                        author_df = df[df['author'] == author['author']]
                        last_post = author_df['published_dt'].max()
                        last_post_str = (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else ''
                        )
                        newsletter = (
                            author_df['newsletter'].iloc[0] 
                            if len(author_df) > 0 else ''
                        )
                        twitter = validate_twitter_handle(author['author'])
                        
                        # Render action buttons
                        render_action_buttons(
                            author_name=author['author'],
                            email=author['email'],
                            newsletter=newsletter,
                            category='Hot Author',
                            posts=author['count'],
                            last_post=last_post_str,
                            twitter=twitter
                        )
                        st.markdown("")
            else:
                st.info("No highly active authors in last 30 days")
    
    with col2:
        with st.container(border=True):
            st.markdown("### 💤 Going Cold")
            st.markdown(
                "_Potential opportunities - they might need content!_"
            )
            cold = get_going_cold(df)
            if cold:
                for newsletter_data in cold:
                    st.markdown(
                        f"**{newsletter_data['newsletter'][:40]}** - "
                        f"{newsletter_data['days_since']} days ago"
                    )
                    
                    # Get first author with email from this newsletter
                    newsletter_df = df[df['newsletter'] == newsletter_data['newsletter']]
                    for author in newsletter_df['author'].dropna().unique():
                        email = extract_email(author)
                        if email:
                            st.markdown(f"📧 {email}")
                            
                            author_df = newsletter_df[newsletter_df['author'] == author]
                            last_post = author_df['published_dt'].max()
                            last_post_str = (
                                last_post.strftime('%Y-%m-%d') 
                                if pd.notna(last_post) else ''
                            )
                            twitter = validate_twitter_handle(author)
                            
                            # Render action buttons
                            render_action_buttons(
                                author_name=author,
                                email=email,
                                newsletter=newsletter_data['newsletter'],
                                category='Going Cold',
                                posts=len(author_df),
                                last_post=last_post_str,
                                twitter=twitter
                            )
                            st.markdown("")
                            break  # Only show first author with email
            else:
                st.success("All newsletters are active!")
    
    col3, col4 = st.columns(2)
    
    with col3:
        with st.container(border=True):
            st.markdown("### 🆕 New Voices")
            st.markdown(
                "_Fresh perspectives - early relationship building opportunity!_"
            )
            new = get_new_voices(df)
            if new:
                for voice in new:
                    st.markdown(
                        f"**{voice['author'][:40]}** "
                        f"({voice['newsletter'][:30]}) - "
                        f"{voice['days_ago']} days ago"
                    )
                    
                    # Get email and other info for action buttons
                    email = extract_email(voice['author'])
                    if email:
                        st.markdown(f"📧 {email}")
                        
                        author_df = df[df['author'] == voice['author']]
                        last_post = author_df['published_dt'].max()
                        last_post_str = (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else ''
                        )
                        twitter = validate_twitter_handle(voice['author'])
                        
                        # Render action buttons
                        render_action_buttons(
                            author_name=voice['author'],
                            email=email,
                            newsletter=voice['newsletter'],
                            category='New Voice',
                            posts=len(author_df),
                            last_post=last_post_str,
                            twitter=twitter
                        )
                        st.markdown("")
            else:
                st.info("No new authors in last 60 days")
    
    with col4:
        with st.container(border=True):
            st.markdown("### 📈 Rising Stars")
            st.markdown(
                "_Growing momentum - catch them while they're active!_"
            )
            rising = get_rising_stars(df)
            if rising:
                for star in rising:
                    st.markdown(
                        f"**{star['author'][:40]}** - "
                        f"+{star['increase_pct']:.0f}%"
                    )
                    
                    # Get email and other info for action buttons
                    email = extract_email(star['author'])
                    if email:
                        st.markdown(f"📧 {email}")
                        
                        author_df = df[df['author'] == star['author']]
                        last_post = author_df['published_dt'].max()
                        last_post_str = (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else ''
                        )
                        newsletter = (
                            author_df['newsletter'].iloc[0] 
                            if len(author_df) > 0 else ''
                        )
                        twitter = validate_twitter_handle(star['author'])
                        
                        # Render action buttons
                        render_action_buttons(
                            author_name=star['author'],
                            email=email,
                            newsletter=newsletter,
                            category='Rising Star',
                            posts=star['recent_count'],
                            last_post=last_post_str,
                            twitter=twitter
                        )
                        st.markdown("")
            else:
                st.info("No authors with significant growth")


def _render_newsletter_details(df: pd.DataFrame) -> None:
    """Render detailed newsletter cards with patterns.
    
    Args:
        df: Main dataframe containing all posts
    """
    st.markdown("## 📊 Newsletter Details")
    patterns = calculate_posting_patterns(df)
    newsletters = sorted(df["newsletter"].dropna().unique())
    
    for newsletter in newsletters:
        # Get newsletter data
        newsletter_df = df[df["newsletter"] == newsletter]
        total_posts = len(newsletter_df)
        unique_authors = newsletter_df["author"].dropna().nunique()
        
        # Most recent post date
        recent_date = newsletter_df["published_dt"].max()
        recent_date_str = (
            recent_date.strftime("%Y-%m-%d") 
            if pd.notna(recent_date) else "N/A"
        )
        
        # Posting frequency (posts per month)
        if pd.notna(recent_date):
            min_date = newsletter_df["published_dt"].min()
            if pd.notna(min_date):
                days_diff = (recent_date - min_date).days
                if days_diff > 0:
                    posts_per_month = (total_posts / days_diff) * 30
                else:
                    posts_per_month = 0
            else:
                posts_per_month = 0
        else:
            posts_per_month = 0
        
        # Get posting patterns for this newsletter
        pattern = patterns.get(newsletter, {})
        consistency_label = pattern.get('consistency', '⚪ Unknown')
        
        # Create expander for each newsletter with pattern info
        with st.expander(
            f"📬 **{newsletter}** | {total_posts} posts | "
            f"{consistency_label}"
        ):
            # Newsletter stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Posts", total_posts)
            with col2:
                st.metric("👥 Unique Authors", unique_authors)
            with col3:
                st.metric("📅 Most Recent", recent_date_str)
            with col4:
                st.metric("🔄 Posts/Month", f"{posts_per_month:.1f}")
            
            # Show posting patterns
            if pattern:
                st.markdown("---")
                st.markdown("### 📊 Posting Patterns")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if pattern.get('top_days'):
                        st.markdown(
                            f"**📅 Typically posts on:** "
                            f"{', '.join(pattern.get('top_days', ['Unknown']))}"
                        )
                    else:
                        st.markdown(
                            "**📅 Typically posts on:** Insufficient data"
                        )
                
                with col_b:
                    trend_pct = pattern.get('trend_pct', 0)
                    if trend_pct > 20:
                        st.markdown(
                            f"**📈 Trend:** "
                            f"Posting {trend_pct:.0f}% more than before"
                        )
                    elif trend_pct < -20:
                        st.markdown(
                            f"**📉 Trend:** "
                            f"Posting {abs(trend_pct):.0f}% less than before"
                        )
                    else:
                        st.markdown("**➡️ Trend:** Stable posting frequency")
            
            st.markdown("---")
            st.subheader("Authors")
            
            # Author details
            _render_newsletter_authors(newsletter_df)


def _render_newsletter_authors(newsletter_df: pd.DataFrame) -> None:
    """Render author details within a newsletter card.
    
    Args:
        newsletter_df: DataFrame filtered to specific newsletter
    """
    authors = newsletter_df["author"].dropna().unique()
    
    for author in sorted(authors):
        author_posts = newsletter_df[newsletter_df["author"] == author]
        author_post_count = len(author_posts)
        
        # Most recent post
        most_recent = author_posts.iloc[0]
        recent_title = most_recent["title"]
        recent_url = most_recent["url"]
        
        # Extract contact info from author field
        email = ""
        twitter = ""
        if isinstance(author, str):
            # Try to extract email (pattern: text <email@domain.com>)
            email_match = re.search(r'<([^>]+@[^>]+)>', author)
            if email_match:
                email = email_match.group(1)
            
            # Try to extract Twitter handle
            twitter_match = re.search(r'@(\w+)', author)
            if twitter_match:
                twitter = f"@{twitter_match.group(1)}"
        
        # Display author info
        st.markdown(f"**{author}**")
        st.markdown(f"- 📝 Posts: {author_post_count}")
        st.markdown(f"- 🔗 Latest: [{recent_title}]({recent_url})")
        
        if email:
            st.markdown(f"- 📧 Email: {email}")
        if twitter:
            st.markdown(f"- 🐦 Twitter: {twitter}")
        
        st.markdown("")


def render_upload_section(data_manager: DataManager) -> None:
    """Render CSV upload section.
    
    Args:
        data_manager: DataManager instance for processing uploads
    """
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    if not uploaded_file:
        st.info("Upload a CSV file to get started.")
        return

    df_uploaded = data_manager.load_uploaded_csv(uploaded_file)
    
    if "newsletter" not in df_uploaded.columns:
        st.error("CSV must have a column named 'newsletter'")
        return

    newsletter_list = sorted(df_uploaded["newsletter"].dropna().unique())
    selected_newsletter = st.selectbox("Select a newsletter", newsletter_list)
    
    filtered_df = df_uploaded[df_uploaded['newsletter'] == selected_newsletter]
    st.dataframe(filtered_df)
