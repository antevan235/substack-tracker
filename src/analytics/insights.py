"""Analytics and insights calculation functions.

This module contains pure functions for calculating various analytics
metrics and insights from newsletter data.
"""

import re
from typing import Dict, List, Optional

import pandas as pd


def extract_email(author_string: str) -> Optional[str]:
    """Extract email address from author field.
    
    Args:
        author_string: Author string that may contain email in angle brackets
        
    Returns:
        Email address if found, None otherwise
        
    Example:
        >>> extract_email("John Doe <john@example.com>")
        'john@example.com'
    """
    if not isinstance(author_string, str):
        return None
    match = re.search(r'<([^>]+@[^>]+)>', author_string)
    return match.group(1) if match else None


def get_hot_authors(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Find authors with 3+ posts in last 30 days.
    
    Args:
        df: DataFrame with author and published_dt columns
        
    Returns:
        List of dicts with author info (author, count, email), 
        top 5 sorted by post count
    """
    now = pd.Timestamp.now(tz='UTC')
    df = df.copy()
    df['published_dt'] = pd.to_datetime(df['published_dt'])
    recent = df[df['published_dt'] >= now - pd.Timedelta(days=30)]
    
    author_counts = recent.groupby('author').size().reset_index(
        name='post_count'
    )
    hot = author_counts[author_counts['post_count'] >= 3].sort_values(
        'post_count', ascending=False
    ).head(5)
    
    result = []
    for _, row in hot.iterrows():
        author_df = df[df['author'] == row['author']]
        email = (
            extract_email(author_df['author'].iloc[0]) 
            if len(author_df) > 0 else None
        )
        result.append({
            'author': row['author'],
            'count': row['post_count'],
            'email': email
        })
    return result


def get_going_cold(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Find newsletters that haven't posted in 14+ days.
    
    Args:
        df: DataFrame with newsletter and published_dt columns
        
    Returns:
        List of dicts with newsletter info (newsletter, days_since),
        top 5 sorted by days since last post
    """
    now = pd.Timestamp.now(tz='UTC')
    df = df.copy()
    df['published_dt'] = pd.to_datetime(df['published_dt'])
    
    result = []
    for newsletter in df['newsletter'].unique():
        newsletter_df = df[df['newsletter'] == newsletter]
        last_post = newsletter_df['published_dt'].max()
        days_since = (now - last_post).days
        
        if days_since >= 14:
            result.append({
                'newsletter': newsletter,
                'days_since': days_since
            })
    
    return sorted(result, key=lambda x: x['days_since'], reverse=True)[:5]


def get_new_voices(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Find authors who started posting in last 60 days.
    
    Args:
        df: DataFrame with author, newsletter and published_dt columns
        
    Returns:
        List of dicts with author info (author, days_ago, newsletter),
        top 5 sorted by days since first post
    """
    now = pd.Timestamp.now(tz='UTC')
    df = df.copy()
    df['published_dt'] = pd.to_datetime(df['published_dt'])
    
    result = []
    for author in df['author'].unique():
        author_df = df[df['author'] == author].sort_values('published_dt')
        first_post = author_df['published_dt'].min()
        days_since_first = (now - first_post).days
        
        if days_since_first <= 60:
            result.append({
                'author': author,
                'days_ago': days_since_first,
                'newsletter': (
                    author_df['newsletter'].iloc[0] 
                    if len(author_df) > 0 else 'N/A'
                )
            })
    
    return sorted(result, key=lambda x: x['days_ago'])[:5]


def get_rising_stars(df: pd.DataFrame) -> List[Dict[str, any]]:
    """Find authors increasing posting frequency by 50%+.
    
    Compares posting frequency in last 30 days vs 30-60 days ago.
    
    Args:
        df: DataFrame with author and published_dt columns
        
    Returns:
        List of dicts with author info (author, increase_pct, recent_count),
        top 5 sorted by increase percentage
    """
    now = pd.Timestamp.now(tz='UTC')
    df = df.copy()
    df['published_dt'] = pd.to_datetime(df['published_dt'])
    
    result = []
    for author in df['author'].unique():
        author_df = df[df['author'] == author]
        last_30 = author_df[
            author_df['published_dt'] >= now - pd.Timedelta(days=30)
        ]
        prev_30 = author_df[
            (author_df['published_dt'] >= now - pd.Timedelta(days=60)) & 
            (author_df['published_dt'] < now - pd.Timedelta(days=30))
        ]
        
        if len(prev_30) > 0:
            increase_pct = (
                (len(last_30) - len(prev_30)) / len(prev_30)
            ) * 100
            if increase_pct >= 50:
                result.append({
                    'author': author,
                    'increase_pct': increase_pct,
                    'recent_count': len(last_30)
                })
    
    return sorted(result, key=lambda x: x['increase_pct'], reverse=True)[:5]


def calculate_posting_patterns(df: pd.DataFrame) -> Dict[str, Dict[str, any]]:
    """Calculate posting patterns for each newsletter.
    
    Analyzes day-of-week patterns, posting trends, and consistency.
    
    Args:
        df: DataFrame with newsletter and published_dt columns
        
    Returns:
        Dictionary mapping newsletter names to pattern data containing:
        - top_days: List of most common posting days
        - trend: Difference in post count (last 30 days vs previous 30)
        - trend_pct: Percentage change in posting frequency
        - consistency: Label indicating posting consistency
        - recent_count: Number of posts in last 30 days
    """
    patterns = {}
    for newsletter in df['newsletter'].unique():
        newsletter_df = df[df['newsletter'] == newsletter].copy()
        newsletter_df['published_dt'] = pd.to_datetime(
            newsletter_df['published_dt']
        )
        newsletter_df['day_of_week'] = (
            newsletter_df['published_dt'].dt.day_name()
        )
        
        # Day of week distribution
        day_counts = newsletter_df['day_of_week'].value_counts()
        top_days = (
            day_counts.head(2).index.tolist() if len(day_counts) > 0 else []
        )
        
        # Frequency trend (last 30 days vs 30-60 days ago)
        now = pd.Timestamp.now(tz='UTC')
        last_30 = newsletter_df[
            newsletter_df['published_dt'] >= now - pd.Timedelta(days=30)
        ]
        prev_30 = newsletter_df[
            (newsletter_df['published_dt'] >= now - pd.Timedelta(days=60)) & 
            (newsletter_df['published_dt'] < now - pd.Timedelta(days=30))
        ]
        
        trend = len(last_30) - len(prev_30)
        trend_pct = (
            ((len(last_30) - len(prev_30)) / len(prev_30) * 100) 
            if len(prev_30) > 0 else 0
        )
        
        # Consistency score
        if len(newsletter_df) > 1:
            newsletter_df = newsletter_df.sort_values('published_dt')
            days_between = newsletter_df['published_dt'].diff().dt.days.dropna()
            consistency = days_between.std() if len(days_between) > 0 else 0
            if consistency < 3:
                consistency_label = "🟢 Consistent"
            elif consistency < 7:
                consistency_label = "🟡 Moderate"
            else:
                consistency_label = "🔴 Sporadic"
        else:
            consistency_label = "⚪ Insufficient data"
        
        patterns[newsletter] = {
            'top_days': top_days,
            'trend': trend,
            'trend_pct': trend_pct,
            'consistency': consistency_label,
            'recent_count': len(last_30)
        }
    
    return patterns
