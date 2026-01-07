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

