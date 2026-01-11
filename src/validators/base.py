"""Base validation framework for CourseScoutAgent."""

import html.parser
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

import requests


class ValidationStatus(Enum):
    """Validation status enum."""
    VALID = "VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


@dataclass
class ValidationResult:
    """Result of URL validation."""
    url: str
    status: ValidationStatus
    reason: str
    final_url: Optional[str] = None
    http_status: Optional[int] = None


class HTMLTextExtractor(html.parser.HTMLParser):
    """Simple HTML parser to extract plain text."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
    
    def handle_data(self, data):
        """Collect text data."""
        self.text_parts.append(data)
    
    def get_text(self) -> str:
        """Get extracted text."""
        return ' '.join(self.text_parts)


def extract_plain_text(html_content: str, max_length: int = 2000) -> str:
    """Extract plain text from HTML content.
    
    Args:
        html_content: HTML content as string.
        max_length: Maximum length of extracted text snippet.
        
    Returns:
        Plain text extracted from HTML, truncated to max_length.
    """
    try:
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        text = parser.get_text()
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    except Exception:
        # If parsing fails, return empty string
        return ""


def fetch_url(
    url: str,
    user_agent: str,
    timeout_sec: int = 10
) -> Tuple[Optional[int], Optional[str], str]:
    """Fetch a URL and return status, final URL, and text snippet.
    
    Args:
        url: The URL to fetch.
        user_agent: User-Agent header value.
        timeout_sec: Request timeout in seconds.
        
    Returns:
        Tuple of (http_status, final_url, body_text_snippet).
        Returns (None, None, "") on network errors.
    """
    headers = {'User-Agent': user_agent}
    max_retries = 2
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=timeout_sec,
                allow_redirects=True
            )
            
            # Get final URL after redirects
            final_url = response.url
            
            # Extract plain text from HTML
            body_text_snippet = extract_plain_text(response.text)
            
            return (response.status_code, final_url, body_text_snippet)
            
        except requests.exceptions.RequestException:
            if attempt < max_retries:
                # Small backoff: wait 0.5s, 1s
                time.sleep(0.5 * (attempt + 1))
            else:
                # All retries failed
                return (None, None, "")
    
    return (None, None, "")

