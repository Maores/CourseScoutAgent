"""Main entry point for CourseScoutAgent."""

import os
import time

from .collectors.reddit_public import collect_reddit_posts
from .storage.db import init_db, insert_post_if_new, get_url_check, upsert_url_check
from .validators.udemy import validate_udemy_url
from .validators.base import ValidationStatus

# Cache validity period: 24 hours
CACHE_TTL_SECONDS = 86400


def validate_udemy_urls(posts, user_agent):
    """Validate Udemy URLs from posts with caching.
    
    Args:
        posts: List of post dictionaries with outbound_urls field.
        user_agent: User-Agent string for validation requests.
        
    Returns:
        Tuple of (total, fresh, cached, valid, invalid, unknown).
    """
    # Collect all unique Udemy URLs from all posts
    udemy_urls = set()
    for post in posts:
        for url in post.get('outbound_urls', []):
            if 'udemy.com' in url.lower():
                udemy_urls.add(url)
    
    # Check for fallback URLs if no Udemy links found
    if not udemy_urls:
        fallback_urls = os.getenv('UDEMY_TEST_URLS', '').strip()
        if fallback_urls:
            print("No Udemy links found in collected posts. Validating fallback URLs...")
            udemy_urls = set(url.strip() for url in fallback_urls.split(','))
    
    # Counters
    fresh_count = 0
    cached_count = 0
    valid_count = 0
    invalid_count = 0
    unknown_count = 0
    
    current_time = time.time()
    
    # Validate each unique URL (with caching)
    for url in udemy_urls:
        cached = get_url_check(url)
        
        # Check if cache is valid (exists and not expired)
        if cached and (current_time - cached['checked_at']) < CACHE_TTL_SECONDS:
            # Reuse from cache
            status_str = cached['status']
            cached_count += 1
        else:
            # Validate fresh
            result = validate_udemy_url(url, user_agent)
            status_str = result.status.value if hasattr(result.status, 'value') else str(result.status)
            # Persist result
            upsert_url_check(result)
            fresh_count += 1
        
        # Count by status
        if status_str == 'VALID':
            valid_count += 1
        elif status_str == 'INVALID':
            invalid_count += 1
        else:
            unknown_count += 1
    
    total_count = len(udemy_urls)
    return (total_count, fresh_count, cached_count, valid_count, invalid_count, unknown_count)


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
    
    # Validate Udemy URLs (with caching)
    user_agent = os.getenv('REDDIT_USER_AGENT', 'CourseScoutAgent/0.1')
    total, fresh, cached, valid, invalid, unknown = validate_udemy_urls(posts, user_agent)
    
    # Print statistics
    print(f"Total fetched: {total_fetched}")
    print(f"Inserted: {inserted_count}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Udemy URLs total: {total}")
    print(f"Checked fresh: {fresh}")
    print(f"Reused from cache: {cached}")
    print(f"VALID: {valid}")
    print(f"INVALID: {invalid}")
    print(f"UNKNOWN: {unknown}")


if __name__ == '__main__':
    main()

