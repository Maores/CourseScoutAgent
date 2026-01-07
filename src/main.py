"""Main entry point for CourseScoutAgent."""

from collectors.reddit_public import collect_reddit_posts
from storage.db import init_db, insert_post_if_new


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
    
    # Print statistics
    print(f"Total fetched: {total_fetched}")
    print(f"Inserted: {inserted_count}")
    print(f"Duplicates: {duplicate_count}")


if __name__ == '__main__':
    main()

