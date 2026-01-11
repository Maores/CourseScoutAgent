"""Main entry point for CourseScoutAgent."""

import os

from .collectors.reddit_public import collect_reddit_posts
from .storage.db import init_db, insert_post_if_new
from .validators.udemy import validate_udemy_url
from .validators.base import ValidationStatus


def validate_udemy_urls(posts, user_agent):
    """Validate Udemy URLs from posts.
    
    Args:
        posts: List of post dictionaries with outbound_urls field.
        user_agent: User-Agent string for validation requests.
        
    Returns:
        Tuple of (checked_count, valid_count, invalid_count, unknown_count).
    """
    # Collect all unique Udemy URLs from all posts
    udemy_urls = set()
    for post in posts:
        for url in post.get('outbound_urls', []):
            if 'udemy.com' in url.lower():
                udemy_urls.add(url)
    
    # Count results by status
    valid_count = 0
    invalid_count = 0
    unknown_count = 0
    
    # Validate each unique URL
    for url in udemy_urls:
        result = validate_udemy_url(url, user_agent)
        if result.status == ValidationStatus.VALID:
            valid_count += 1
        elif result.status == ValidationStatus.INVALID:
            invalid_count += 1
        else:
            unknown_count += 1
    
    checked_count = len(udemy_urls)
    return (checked_count, valid_count, invalid_count, unknown_count)


def main():
    """Fetch and store Reddit posts."""
    # Initialize database
    init_db()
    
    # Fetch posts
    posts = collect_reddit_posts()
    total_fetched = len(posts)
    
    # Insert posts and track counts
    inserted_count = 0
    duplicate_count = 0
    
    for post in posts:
        if insert_post_if_new(post):
            inserted_count += 1
        else:
            duplicate_count += 1
    
    # Validate Udemy URLs
    user_agent = os.getenv('REDDIT_USER_AGENT', 'CourseScoutAgent/0.1')
    checked_count, valid_count, invalid_count, unknown_count = validate_udemy_urls(posts, user_agent)
    
    # Print statistics
    print(f"Total fetched: {total_fetched}")
    print(f"Inserted: {inserted_count}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Udemy links checked: {checked_count}")
    print(f"VALID: {valid_count}")
    print(f"INVALID: {invalid_count}")
    print(f"UNKNOWN: {unknown_count}")


if __name__ == '__main__':
    main()

