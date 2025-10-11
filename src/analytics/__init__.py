"""Analytics and insights calculation module."""

from .insights import (
    extract_email,
    get_hot_authors,
    get_going_cold,
    get_new_voices,
    get_rising_stars,
    calculate_posting_patterns
)
from .contacts import (
    validate_email,
    validate_twitter_handle,
    extract_contacts,
    deduplicate_contacts
)
from .clustering import (
    StudentClusteringAnalyzer,
    generate_analysis_report
)

__all__ = [
    'extract_email',
    'get_hot_authors',
    'get_going_cold',
    'get_new_voices',
    'get_rising_stars',
    'calculate_posting_patterns',
    'validate_email',
    'validate_twitter_handle',
    'extract_contacts',
    'deduplicate_contacts',
    'StudentClusteringAnalyzer',
    'generate_analysis_report'
]
