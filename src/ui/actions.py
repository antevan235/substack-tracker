"""Action buttons and contact export UI components.

This module provides UI components for author outreach actions including
email drafting, clipboard copy, Twitter links, and CSV export.
"""

import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st

from analytics.contacts import extract_contacts, deduplicate_contacts
from ui.email_templates import generate_email_template


def render_action_buttons(
    author_name: str,
    email: Optional[str],
    newsletter: str,
    category: str,
    posts: int = 0,
    last_post: str = "",
    twitter: Optional[str] = None
) -> None:
    """Render action buttons for an author.
    
    Args:
        author_name: Name of the author
        email: Email address (if available)
        newsletter: Newsletter name
        category: Author category (Hot Author, Rising Star, etc.)
        posts: Number of posts
        last_post: Date of last post
        twitter: Twitter handle (if available)
    """
    if not email:
        return
    
    # Create columns for buttons
    cols = st.columns([1, 1, 1] if twitter else [1, 1])
    
    # Generate email template
    template = generate_email_template(
        author_name, newsletter, category, posts, last_post
    )
    
    with cols[0]:
        # Draft Email button
        mailto_link = create_mailto_link(
            email,
            template['subject'],
            template['body']
        )
        st.markdown(
            f'<a href="{mailto_link}" target="_blank" '
            f'style="text-decoration: none;">'
            f'<button style="width: 100%; padding: 0.25rem 0.75rem; '
            f'background-color: #0066cc; color: white; border: none; '
            f'border-radius: 0.25rem; cursor: pointer; font-size: 0.875rem;">'
            f'📧 Draft Email</button></a>',
            unsafe_allow_html=True
        )
    
    with cols[1]:
        # Copy Email button
        button_key = f"copy_{email}_{author_name}_{category}"
        if st.button("📋 Copy Email", key=button_key, use_container_width=True):
            copy_to_clipboard(email)
            st.toast("✅ Email copied to clipboard!")
    
    if twitter and len(cols) > 2:
        with cols[2]:
            # Twitter link button
            twitter_url = f"https://twitter.com/{twitter}"
            st.markdown(
                f'<a href="{twitter_url}" target="_blank" '
                f'style="text-decoration: none;">'
                f'<button style="width: 100%; padding: 0.25rem 0.75rem; '
                f'background-color: #1DA1F2; color: white; border: none; '
                f'border-radius: 0.25rem; cursor: pointer; font-size: 0.875rem;">'
                f'🐦 Twitter</button></a>',
                unsafe_allow_html=True
            )


def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard using JavaScript.
    
    Uses Streamlit's HTML component to execute JavaScript for clipboard access.
    
    Args:
        text: Text to copy to clipboard
    """
    # Escape text for JavaScript
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    st.components.v1.html(
        f"""
        <script>
        navigator.clipboard.writeText("{escaped_text}").then(function() {{
            console.log('Copied to clipboard successfully');
        }}, function(err) {{
            console.error('Failed to copy: ', err);
        }});
        </script>
        """,
        height=0
    )


def create_mailto_link(
    email: str,
    subject: str,
    body: str
) -> str:
    """Create a mailto: link with pre-filled subject and body.
    
    Args:
        email: Recipient email address
        subject: Email subject
        body: Email body content
        
    Returns:
        Complete mailto: URL
        
    Example:
        >>> create_mailto_link("john@ex.com", "Hello", "Hi there")
        'mailto:john@ex.com?subject=Hello&body=Hi%20there'
    """
    params = urllib.parse.urlencode({
        'subject': subject,
        'body': body
    })
    return f"mailto:{email}?{params}"


def export_contacts_csv(contacts: List[Dict[str, any]]) -> bytes:
    """Convert contacts list to CSV bytes for download.
    
    Args:
        contacts: List of contact dictionaries
        
    Returns:
        CSV data as bytes
    """
    if not contacts:
        # Return empty CSV with headers
        df = pd.DataFrame(columns=[
            'Name', 'Email', 'Twitter', 'Newsletter', 
            'Posts', 'Last Post', 'Category'
        ])
    else:
        df = pd.DataFrame(contacts)
        # Rename columns for better CSV headers
        df = df.rename(columns={
            'name': 'Name',
            'email': 'Email',
            'twitter': 'Twitter',
            'newsletter': 'Newsletter',
            'posts': 'Posts',
            'last_post': 'Last Post',
            'category': 'Category'
        })
        # Reorder columns
        df = df[['Name', 'Email', 'Twitter', 'Newsletter', 
                 'Posts', 'Last Post', 'Category']]
    
    return df.to_csv(index=False).encode('utf-8')


def render_contact_export_tab(df: pd.DataFrame) -> None:
    """Render the Contact Export tab.
    
    Args:
        df: Main dataframe containing all posts
    """
    st.header("📤 Contact Export")
    st.markdown(
        "Export author contact information for outreach. "
        "Filter by category to get targeted contact lists."
    )
    
    # Filter controls
    col1, col2 = st.columns([1, 3])
    
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            options=['All', 'Hot Authors', 'Rising Stars', 'New Voices', 'Going Cold'],
            index=0
        )
    
    # Map display names to internal category names
    category_map = {
        'All': None,
        'Hot Authors': 'hot',
        'Rising Stars': 'rising',
        'New Voices': 'new',
        'Going Cold': 'cold'
    }
    
    # Extract contacts
    category_key = category_map[category_filter]
    contacts = extract_contacts(df, category=category_key)
    contacts = deduplicate_contacts(contacts)
    
    # Show counts
    total_contacts = len(contacts)
    missing_info = sum(1 for c in contacts if not c.get('twitter'))
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("📊 Found Contacts", total_contacts)
    with col_b:
        st.metric("⚠️ Missing Twitter", missing_info)
    
    if not contacts:
        st.info(
            f"No contacts with email addresses found for category: {category_filter}. "
            f"Make sure your data includes author email information."
        )
        return
    
    st.markdown("---")
    
    # Action buttons
    col_btn1, col_btn2, col_spacer = st.columns([1, 1, 2])
    
    with col_btn1:
        # Copy All Emails button
        if st.button("📋 Copy All Emails", use_container_width=True):
            email_list = "; ".join([c['email'] for c in contacts if c.get('email')])
            copy_to_clipboard(email_list)
            st.toast(f"✅ Copied {len(contacts)} email addresses!")
    
    with col_btn2:
        # Export CSV button
        csv_data = export_contacts_csv(contacts)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"contacts_export_{timestamp}.csv"
        
        st.download_button(
            label="📧 Export CSV",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Contact table preview
    st.subheader("📋 Contact Preview")
    
    # Convert to DataFrame for display
    df_contacts = pd.DataFrame(contacts)
    df_contacts = df_contacts.rename(columns={
        'name': 'Name',
        'email': 'Email',
        'twitter': 'Twitter',
        'newsletter': 'Newsletter',
        'posts': 'Posts',
        'last_post': 'Last Post',
        'category': 'Category'
    })
    
    # Reorder and select columns
    display_cols = ['Name', 'Email', 'Twitter', 'Newsletter', 
                    'Posts', 'Last Post', 'Category']
    df_contacts = df_contacts[display_cols]
    
    # Display with formatting
    st.dataframe(
        df_contacts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
            "Twitter": st.column_config.TextColumn("Twitter", width="small"),
            "Newsletter": st.column_config.TextColumn("Newsletter", width="medium"),
            "Posts": st.column_config.NumberColumn("Posts", width="small"),
            "Last Post": st.column_config.TextColumn("Last Post", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small")
        }
    )
