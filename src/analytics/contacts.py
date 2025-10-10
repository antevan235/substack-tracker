"""Contact extraction and validation functions.

This module provides utilities for extracting and validating email addresses
and Twitter handles from author strings and other contact information.
"""

import re
from typing import Dict, List, Optional, Set

import pandas as pd


def validate_email(email: str) -> bool:
    """Validate email address format (RFC 5322 simplified).
    
    Args:
        email: Email address string to validate
        
    Returns:
        True if email is valid format, False otherwise
        
    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    
    # Simplified RFC 5322 pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_twitter_handle(handle: str) -> Optional[str]:
    """Validate and normalize Twitter handle.
    
    Extracts Twitter handle from various formats:
    - Plain username: "username" -> "username"
    - With @: "@username" -> "username"
    - Twitter URL: "twitter.com/username" -> "username"
    - X.com URL: "x.com/username" -> "username"
    
    Args:
        handle: Twitter handle or URL string
        
    Returns:
        Normalized username (without @) if valid, None otherwise
        
    Example:
        >>> validate_twitter_handle("@johndoe")
        'johndoe'
        >>> validate_twitter_handle("twitter.com/johndoe")
        'johndoe'
    """
    if not handle or not isinstance(handle, str):
        return None
    
    handle = handle.strip()
    
    # Extract from Twitter/X URL
    url_match = re.search(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', handle)
    if url_match:
        return url_match.group(1)
    
    # Extract from @username format
    at_match = re.match(r'^@?([a-zA-Z0-9_]+)$', handle)
    if at_match:
        username = at_match.group(1)
        # Twitter usernames are 1-15 characters
        if 1 <= len(username) <= 15:
            return username
    
    return None


def extract_contacts(
    df: pd.DataFrame,
    category: Optional[str] = None
) -> List[Dict[str, any]]:
    """Extract and validate contact information from dataframe.
    
    Args:
        df: DataFrame with author and newsletter columns
        category: Optional filter for contact type 
                  ('hot', 'rising', 'new', 'cold', or None for all)
        
    Returns:
        List of dicts with contact info including:
        - name: Author name
        - email: Email address (validated)
        - twitter: Twitter handle (normalized)
        - newsletter: Newsletter name
        - posts: Post count
        - last_post: Most recent post date
        - category: Contact category
        
    Example:
        >>> extract_contacts(df, category='hot')
        [{'name': 'John Doe', 'email': 'john@example.com', ...}]
    """
    from analytics.insights import (
        get_hot_authors,
        get_rising_stars,
        get_new_voices,
        get_going_cold,
        extract_email
    )
    
    contacts = []
    seen_emails: Set[str] = set()
    
    # Get categorized authors
    categories_to_fetch = [category] if category else ['hot', 'rising', 'new', 'cold']
    
    for cat in categories_to_fetch:
        if cat == 'hot':
            authors = get_hot_authors(df)
            for author in authors:
                email = author.get('email')
                if email and validate_email(email) and email not in seen_emails:
                    seen_emails.add(email)
                    
                    author_df = df[df['author'] == author['author']]
                    last_post = author_df['published_dt'].max()
                    
                    # Extract Twitter
                    twitter = None
                    if isinstance(author['author'], str):
                        twitter = validate_twitter_handle(author['author'])
                    
                    contacts.append({
                        'name': author['author'],
                        'email': email,
                        'twitter': twitter or '',
                        'newsletter': (
                            author_df['newsletter'].iloc[0] 
                            if len(author_df) > 0 else 'N/A'
                        ),
                        'posts': author['count'],
                        'last_post': (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else 'N/A'
                        ),
                        'category': 'Hot Author'
                    })
        
        elif cat == 'rising':
            stars = get_rising_stars(df)
            for star in stars:
                author_df = df[df['author'] == star['author']]
                email = extract_email(star['author'])
                
                if email and validate_email(email) and email not in seen_emails:
                    seen_emails.add(email)
                    
                    last_post = author_df['published_dt'].max()
                    
                    # Extract Twitter
                    twitter = None
                    if isinstance(star['author'], str):
                        twitter = validate_twitter_handle(star['author'])
                    
                    contacts.append({
                        'name': star['author'],
                        'email': email,
                        'twitter': twitter or '',
                        'newsletter': (
                            author_df['newsletter'].iloc[0] 
                            if len(author_df) > 0 else 'N/A'
                        ),
                        'posts': star['recent_count'],
                        'last_post': (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else 'N/A'
                        ),
                        'category': 'Rising Star'
                    })
        
        elif cat == 'new':
            voices = get_new_voices(df)
            for voice in voices:
                author_df = df[df['author'] == voice['author']]
                email = extract_email(voice['author'])
                
                if email and validate_email(email) and email not in seen_emails:
                    seen_emails.add(email)
                    
                    last_post = author_df['published_dt'].max()
                    
                    # Extract Twitter
                    twitter = None
                    if isinstance(voice['author'], str):
                        twitter = validate_twitter_handle(voice['author'])
                    
                    contacts.append({
                        'name': voice['author'],
                        'email': email,
                        'twitter': twitter or '',
                        'newsletter': voice['newsletter'],
                        'posts': len(author_df),
                        'last_post': (
                            last_post.strftime('%Y-%m-%d') 
                            if pd.notna(last_post) else 'N/A'
                        ),
                        'category': 'New Voice'
                    })
        
        elif cat == 'cold':
            # For going cold, we need newsletter-level contacts
            cold = get_going_cold(df)
            for newsletter_data in cold:
                newsletter_df = df[df['newsletter'] == newsletter_data['newsletter']]
                # Get unique authors from this newsletter
                for author in newsletter_df['author'].dropna().unique():
                    email = extract_email(author)
                    
                    if email and validate_email(email) and email not in seen_emails:
                        seen_emails.add(email)
                        
                        author_df = newsletter_df[newsletter_df['author'] == author]
                        last_post = author_df['published_dt'].max()
                        
                        # Extract Twitter
                        twitter = None
                        if isinstance(author, str):
                            twitter = validate_twitter_handle(author)
                        
                        contacts.append({
                            'name': author,
                            'email': email,
                            'twitter': twitter or '',
                            'newsletter': newsletter_data['newsletter'],
                            'posts': len(author_df),
                            'last_post': (
                                last_post.strftime('%Y-%m-%d') 
                                if pd.notna(last_post) else 'N/A'
                            ),
                            'category': 'Going Cold'
                        })
    
    return contacts


def deduplicate_contacts(contacts: List[Dict[str, any]]) -> List[Dict[str, any]]:
    """Remove duplicate contacts based on email address.
    
    If multiple entries exist for same email, keeps the one with
    the most posts.
    
    Args:
        contacts: List of contact dictionaries
        
    Returns:
        Deduplicated list of contacts
        
    Example:
        >>> deduplicate_contacts([
        ...     {'email': 'john@ex.com', 'posts': 5},
        ...     {'email': 'john@ex.com', 'posts': 3}
        ... ])
        [{'email': 'john@ex.com', 'posts': 5}]
    """
    seen: Dict[str, Dict[str, any]] = {}
    
    for contact in contacts:
        email = contact.get('email')
        if not email:
            continue
            
        if email not in seen or contact['posts'] > seen[email]['posts']:
            seen[email] = contact
    
    return list(seen.values())
