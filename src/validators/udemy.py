"""Udemy-specific URL validator for CourseScoutAgent."""

#from validators.base import ValidationResult, ValidationStatus, fetch_url
from .base import ValidationResult, ValidationStatus, fetch_url


def validate_udemy_url(url: str, user_agent: str) -> ValidationResult:
    """Validate a Udemy course URL.
    
    Args:
        url: The Udemy URL to validate.
        user_agent: User-Agent header value for requests.
        
    Returns:
        ValidationResult with status, reason, and metadata.
    """
    # Fetch the URL
    http_status, final_url, text_snippet = fetch_url(url, user_agent)
    
    text_lower = text_snippet.lower()
    
    # Check for INVALID conditions
    if http_status == 404:
        return ValidationResult(
            url=url,
            status=ValidationStatus.INVALID,
            reason="HTTP 404 - Page not found",
            final_url=final_url,
            http_status=http_status
        )
    
    invalid_keywords = [
        "course is no longer available",
        "we couldn't find the page",
        "we could not find the page",
        "not found"
    ]
    
    for keyword in invalid_keywords:
        if keyword in text_lower:
            return ValidationResult(
                url=url,
                status=ValidationStatus.INVALID,
                reason=f"Page indicates unavailability: '{keyword}'",
                final_url=final_url,
                http_status=http_status
            )
    
    # Check for UNKNOWN conditions
    if http_status == 429:
        return ValidationResult(
            url=url,
            status=ValidationStatus.UNKNOWN,
            reason="HTTP 429 - Rate limited",
            final_url=final_url,
            http_status=http_status
        )
    
    if http_status is None:
        return ValidationResult(
            url=url,
            status=ValidationStatus.UNKNOWN,
            reason="Network error - could not fetch URL",
            final_url=final_url,
            http_status=http_status
        )
    
    unknown_keywords = [
        "please log in",
        "access denied"
    ]
    
    for keyword in unknown_keywords:
        if keyword in text_lower:
            return ValidationResult(
                url=url,
                status=ValidationStatus.UNKNOWN,
                reason=f"Requires authentication: '{keyword}'",
                final_url=final_url,
                http_status=http_status
            )
    
    # Otherwise assume VALID
    return ValidationResult(
        url=url,
        status=ValidationStatus.VALID,
        reason="URL accessible and appears valid",
        final_url=final_url,
        http_status=http_status
    )

