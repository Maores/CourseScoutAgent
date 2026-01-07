"""Reddit public API collector for CourseScoutAgent.

Fetches posts from public Reddit endpoints without OAuth authentication.
"""

import os
import re
import time
from typing import List, Dict, Any, Optional

import requests


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text using regex.
    
    Args:
        text: The text to extract URLs from.
        
    Returns:
        List of unique URLs found in the text.
    """
    if not text:
        return []
    
    # Pattern to match URLs (http, https, or www)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text, re.IGNORECASE)
    
    # Normalize URLs (add http:// to www. URLs)
    normalized_urls = []
    for url in urls:
        if url.startswith('www.'):
            url = 'http://' + url
        normalized_urls.append(url)
    
    # Return unique URLs
    return list(set(normalized_urls))


def get_user_agent() -> str:
    """Get User-Agent from environment variable or use default.
    
    Returns:
        User-Agent string for requests.
    """
    return os.getenv('REDDIT_USER_AGENT', 'CourseScoutAgent/0.1')


def fetch_reddit_posts(url: str, max_retries: int = 2, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Fetch posts from a Reddit JSON endpoint with retry logic.
    
    Args:
        url: The Reddit JSON endpoint URL.
        max_retries: Maximum number of retry attempts.
        timeout: Request timeout in seconds.
        
    Returns:
        Parsed JSON response as dictionary, or None if all retries fail.
    """
    headers = {'User-Agent': get_user_agent()}
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries:
                # Exponential backoff: wait 1s, 2s, 4s...
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                print(f"Failed to fetch {url} after {max_retries + 1} attempts: {e}")
                return None
    
    return None


def parse_reddit_post(post_data: Dict[str, Any], subreddit: str) -> Dict[str, Any]:
    """Parse a single Reddit post into the required format.
    
    Args:
        post_data: The post data from Reddit API.
        subreddit: The subreddit name.
        
    Returns:
        Dictionary with parsed post information.
    """
    # Extract data safely with defaults
    post_id = post_data.get('id', '')
    title = post_data.get('title', '')
    selftext = post_data.get('selftext', '')
    author = post_data.get('author', '[deleted]')
    created_utc = post_data.get('created_utc', 0)
    permalink = post_data.get('permalink', '')
    url = post_data.get('url', '')
    
    # Convert permalink to full URL if it's relative
    if permalink and not permalink.startswith('http'):
        permalink = f"https://www.reddit.com{permalink}"
    
    # Extract URLs from selftext
    outbound_urls = extract_urls(selftext)
    
    # If the post URL is external (not a Reddit link), add it to outbound_urls
    if url and not url.startswith('https://www.reddit.com') and not url.startswith('/r/'):
        if url not in outbound_urls:
            outbound_urls.append(url)
    
    # Convert created_utc to int if it's a float
    if isinstance(created_utc, float):
        created_utc = int(created_utc)
    
    return {
        'post_id': post_id,
        'source': 'reddit',
        'subreddit': subreddit,
        'title': title,
        'content': selftext,
        'outbound_urls': outbound_urls,
        'author': author if author else '[deleted]',
        'created_utc': created_utc,
        'permalink': permalink
    }


def collect_reddit_posts() -> List[Dict[str, Any]]:
    """Collect posts from Reddit public endpoints.
    
    Fetches posts from:
    - r/udemyfreebies
    - r/FreeUdemyCoupons
    
    Returns:
        List of dictionaries, one per post, with parsed information.
    """
    endpoints = [
        'https://www.reddit.com/r/udemyfreebies/new.json?limit=50',
        'https://www.reddit.com/r/FreeUdemyCoupons/new.json?limit=50'
    ]
    
    all_posts = []
    
    for endpoint in endpoints:
        # Extract subreddit name from URL
        subreddit_match = re.search(r'/r/([^/]+)/', endpoint)
        subreddit = subreddit_match.group(1) if subreddit_match else 'unknown'
        
        # Fetch posts
        data = fetch_reddit_posts(endpoint)
        if not data:
            continue
        
        # Reddit API returns data in a nested structure: data -> children -> data
        posts = data.get('data', {}).get('children', [])
        
        for post_wrapper in posts:
            post_data = post_wrapper.get('data', {})
            if post_data:
                parsed_post = parse_reddit_post(post_data, subreddit)
                all_posts.append(parsed_post)
    
    return all_posts

