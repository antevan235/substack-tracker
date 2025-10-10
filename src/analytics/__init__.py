"""Analytics and insights calculation module."""

from .insights import (
    extract_email,
    get_hot_authors,
    get_going_cold,
    get_new_voices,
    get_rising_stars,
    calculate_posting_patterns
)

__all__ = [
    'extract_email',
    'get_hot_authors',
    'get_going_cold',
    'get_new_voices',
    'get_rising_stars',
    'calculate_posting_patterns'
]
