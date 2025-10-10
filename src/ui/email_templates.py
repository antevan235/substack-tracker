"""Email template generation for author outreach.

This module provides context-aware email templates for different
author categories (hot authors, rising stars, new voices, going cold).
"""

from typing import Dict, Optional


def generate_email_template(
    author_name: str,
    newsletter: str,
    category: str,
    posts: int = 0,
    last_post: str = ""
) -> Dict[str, str]:
    """Generate context-aware email template.
    
    Args:
        author_name: Name of the author
        newsletter: Newsletter name
        category: Author category (Hot Author, Rising Star, New Voice, Going Cold)
        posts: Number of posts
        last_post: Date of last post
        
    Returns:
        Dictionary with 'subject' and 'body' keys
        
    Example:
        >>> template = generate_email_template(
        ...     "John Doe", "Tech Newsletter", "Hot Author", 5
        ... )
        >>> print(template['subject'])
        'Love your recent work on Tech Newsletter'
    """
    # Clean author name (remove email if present)
    clean_name = author_name.split('<')[0].strip()
    
    templates = {
        'Hot Author': _hot_author_template,
        'Rising Star': _rising_star_template,
        'New Voice': _new_voice_template,
        'Going Cold': _going_cold_template
    }
    
    template_func = templates.get(category, _default_template)
    return template_func(clean_name, newsletter, posts, last_post)


def _hot_author_template(
    name: str,
    newsletter: str,
    posts: int,
    last_post: str
) -> Dict[str, str]:
    """Template for hot authors (actively publishing).
    
    Args:
        name: Author name
        newsletter: Newsletter name
        posts: Number of recent posts
        last_post: Date of last post
        
    Returns:
        Dict with subject and body
    """
    subject = f"Love your recent work on {newsletter}"
    
    body = f"""Hi {name},

I've been following your work on {newsletter} and wanted to reach out. I noticed you've published {posts} posts recently, and your insights on [TOPIC] really resonated with me.

I'm particularly interested in [SPECIFIC ASPECT] and would love to explore potential collaboration opportunities.

Would you be open to a quick conversation?

Best regards,
[YOUR NAME]"""
    
    return {'subject': subject, 'body': body}


def _rising_star_template(
    name: str,
    newsletter: str,
    posts: int,
    last_post: str
) -> Dict[str, str]:
    """Template for rising stars (increasing momentum).
    
    Args:
        name: Author name
        newsletter: Newsletter name
        posts: Number of recent posts
        last_post: Date of last post
        
    Returns:
        Dict with subject and body
    """
    subject = f"Impressed by your growing presence in {newsletter}"
    
    body = f"""Hi {name},

I've been tracking your increasing activity on {newsletter} and I'm impressed by your growing momentum. Your recent pieces show real depth and insight.

I think there could be some interesting synergies between what you're building and what we're working on.

Would you be interested in exploring collaboration opportunities?

Best,
[YOUR NAME]"""
    
    return {'subject': subject, 'body': body}


def _new_voice_template(
    name: str,
    newsletter: str,
    posts: int,
    last_post: str
) -> Dict[str, str]:
    """Template for new voices (recently started).
    
    Args:
        name: Author name
        newsletter: Newsletter name
        posts: Number of posts
        last_post: Date of last post
        
    Returns:
        Dict with subject and body
    """
    subject = f"Welcome to the community - {newsletter}"
    
    body = f"""Hi {name},

I noticed you recently started contributing to {newsletter} - welcome to the community!

Your fresh perspective on [TOPIC] caught my attention. As someone who's been in this space for a while, I'd love to connect and share insights.

Building relationships early is so valuable. Would you be open to a brief intro call?

Looking forward to connecting,
[YOUR NAME]"""
    
    return {'subject': subject, 'body': body}


def _going_cold_template(
    name: str,
    newsletter: str,
    posts: int,
    last_post: str
) -> Dict[str, str]:
    """Template for going cold authors (haven't posted recently).
    
    Args:
        name: Author name
        newsletter: Newsletter name
        posts: Number of posts
        last_post: Date of last post
        
    Returns:
        Dict with subject and body
    """
    subject = f"Would love to contribute to {newsletter}"
    
    body = f"""Hi {name},

I've been following {newsletter} and really appreciate the quality of content you've published. I noticed it's been a while since the last post (around {last_post}), and I wanted to reach out.

I have some ideas that might align well with your newsletter's focus, and I'd love to discuss potential contributions or collaborations.

Would you be interested in exploring this?

Best regards,
[YOUR NAME]"""
    
    return {'subject': subject, 'body': body}


def _default_template(
    name: str,
    newsletter: str,
    posts: int,
    last_post: str
) -> Dict[str, str]:
    """Default template for unknown categories.
    
    Args:
        name: Author name
        newsletter: Newsletter name
        posts: Number of posts
        last_post: Date of last post
        
    Returns:
        Dict with subject and body
    """
    subject = f"Interested in connecting - {newsletter}"
    
    body = f"""Hi {name},

I came across your work on {newsletter} and wanted to reach out. Your content has been really valuable.

I'd love to explore potential collaboration opportunities.

Best,
[YOUR NAME]"""
    
    return {'subject': subject, 'body': body}
