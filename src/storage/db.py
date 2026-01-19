"""SQLite storage module for CourseScoutAgent."""

import json
import os
import sqlite3
import time
from typing import Dict, Any


def init_db(db_path: str = "coursescout.db") -> None:
    """Create the database and posts table if they don't exist.
    
    Args:
        db_path: Path to the SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                subreddit TEXT,
                title TEXT,
                content TEXT,
                url_list TEXT,
                author TEXT,
                created_utc INTEGER,
                permalink TEXT,
                inserted_at INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS url_checks (
                url TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                reason TEXT,
                http_status INTEGER,
                final_url TEXT,
                checked_at INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise


def insert_post_if_new(post: Dict[str, Any], db_path: str = "coursescout.db") -> bool:
    """Insert a post if it doesn't already exist.
    
    Args:
        post: Dictionary containing post data.
        db_path: Path to the SQLite database file.
        
    Returns:
        True if the post was inserted, False if it already exists.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extract fields safely with defaults
        post_id = post.get('post_id', '')
        source = post.get('source', '')
        subreddit = post.get('subreddit')
        title = post.get('title')
        content = post.get('content')
        # Map outbound_urls to url_list (handle both field names)
        outbound_urls = post.get('outbound_urls', post.get('url_list', []))
        author = post.get('author')
        created_utc = post.get('created_utc')
        permalink = post.get('permalink')
        
        # JSON-encode url_list (always as a list)
        if not isinstance(outbound_urls, list):
            outbound_urls = []
        url_list_json = json.dumps(outbound_urls)
        
        # Get current timestamp for inserted_at
        inserted_at = int(time.time())
        
        # Check if post_id already exists
        cursor.execute("SELECT 1 FROM posts WHERE post_id = ?", (post_id,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Insert the post
        cursor.execute("""
            INSERT INTO posts (
                post_id, source, subreddit, title, content,
                url_list, author, created_utc, permalink, inserted_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_id, source, subreddit, title, content,
            url_list_json, author, created_utc, permalink, inserted_at
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Error inserting post: {e}")
        raise
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error processing post data: {e}")
        raise


def upsert_url_check(result, db_path: str = "coursescout.db") -> None:
    """Insert or update a URL check result.
    
    Args:
        result: Object or dict with url, status, reason, http_status, final_url, checked_at.
        db_path: Path to the SQLite database file.
    """
    # Handle both dict and object with attributes
    if isinstance(result, dict):
        url = result.get('url')
        status = result.get('status')
        reason = result.get('reason')
        http_status = result.get('http_status')
        final_url = result.get('final_url')
        checked_at = result.get('checked_at')
    else:
        url = getattr(result, 'url', None)
        status = getattr(result, 'status', None)
        reason = getattr(result, 'reason', None)
        http_status = getattr(result, 'http_status', None)
        final_url = getattr(result, 'final_url', None)
        checked_at = getattr(result, 'checked_at', None)
    
    # Convert status to string if it's an enum
    if hasattr(status, 'value'):
        status = status.value
    elif status is not None:
        status = str(status)
    
    # Use current time if checked_at not provided
    if checked_at is None:
        checked_at = int(time.time())
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO url_checks (url, status, reason, http_status, final_url, checked_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                status = excluded.status,
                reason = excluded.reason,
                http_status = excluded.http_status,
                final_url = excluded.final_url,
                checked_at = excluded.checked_at
        """, (url, status, reason, http_status, final_url, checked_at))
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error upserting URL check: {e}")
        raise


def get_url_check(url: str, db_path: str = "coursescout.db") -> dict | None:
    """Retrieve a URL check result.
    
    Args:
        url: The URL to look up.
        db_path: Path to the SQLite database file.
        
    Returns:
        Dict with url, status, reason, http_status, final_url, checked_at or None.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT url, status, reason, http_status, final_url, checked_at
            FROM url_checks WHERE url = ?
        """, (url,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'url': row[0],
                'status': row[1],
                'reason': row[2],
                'http_status': row[3],
                'final_url': row[4],
                'checked_at': row[5]
            }
        return None
    except sqlite3.Error as e:
        print(f"Error getting URL check: {e}")
        raise
