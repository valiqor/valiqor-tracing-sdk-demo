"""
Valiqor Trace SDK - Redaction Module

Minimal PII and token redaction for safe local trace storage.
No external dependencies, no network calls.
"""

import re
from typing import Any, Dict, List, Union


# Patterns to detect sensitive data
PATTERNS = {
    "api_key": re.compile(r"(sk-|api[_-]?key|bearer\s+)[\w\-]{20,}", re.IGNORECASE),
    "token": re.compile(r"(token|jwt|auth)[\"\']?\s*[:=]\s*[\"\']?[\w\-\.]{20,}", re.IGNORECASE),
    "password": re.compile(r"(password|passwd|pwd)[\"\']?\s*[:=]\s*[\"\']?[\w\S]{6,}", re.IGNORECASE),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b"),
    "phone": re.compile(r"\b(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}\b"),
}

# Common sensitive keys
SENSITIVE_KEYS = {
    "api_key", "apikey", "api-key",
    "secret", "secret_key", "secretkey",
    "password", "passwd", "pwd",
    "token", "access_token", "refresh_token", "auth_token",
    "private_key", "privatekey",
    "client_secret", "clientsecret",
    "bearer",
}


def redact_string(text: str) -> str:
    """
    Redact sensitive patterns from a string.
    
    Args:
        text: Input string
        
    Returns:
        String with sensitive data replaced with [REDACTED]
    """
    if not isinstance(text, str):
        return text
    
    for pattern in PATTERNS.values():
        text = pattern.sub("[REDACTED]", text)
    
    return text


def safe(obj: Any, depth: int = 0, max_depth: int = 10) -> Any:
    """
    Recursively sanitize objects, redacting sensitive data.
    
    Args:
        obj: Object to sanitize (dict, list, str, or primitive)
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops
        
    Returns:
        Sanitized copy of the object
    """
    # Prevent infinite recursion
    if depth > max_depth:
        return "[MAX_DEPTH_EXCEEDED]"
    
    # Handle None and primitives
    if obj is None or isinstance(obj, (bool, int, float)):
        return obj
    
    # Handle strings - redact patterns
    if isinstance(obj, str):
        return redact_string(obj)
    
    # Handle dictionaries
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Check if key is sensitive
            if isinstance(key, str) and key.lower() in SENSITIVE_KEYS:
                result[key] = "[REDACTED]"
            else:
                result[key] = safe(value, depth + 1, max_depth)
        return result
    
    # Handle lists and tuples
    if isinstance(obj, (list, tuple)):
        sanitized = [safe(item, depth + 1, max_depth) for item in obj]
        return sanitized if isinstance(obj, list) else tuple(sanitized)
    
    # Handle sets
    if isinstance(obj, set):
        return {safe(item, depth + 1, max_depth) for item in obj}
    
    # For other objects, try to convert to string and redact
    try:
        return redact_string(str(obj))
    except Exception:
        return "[UNSERIALIZABLE]"


def redact_dict_keys(data: Dict[str, Any], keys_to_redact: List[str]) -> Dict[str, Any]:
    """
    Redact specific keys from a dictionary.
    
    Args:
        data: Dictionary to redact
        keys_to_redact: List of key names to redact
        
    Returns:
        Dictionary with specified keys redacted
    """
    result = {}
    keys_lower = {k.lower() for k in keys_to_redact}
    
    for key, value in data.items():
        if isinstance(key, str) and key.lower() in keys_lower:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = redact_dict_keys(value, keys_to_redact)
        elif isinstance(value, list):
            result[key] = [
                redact_dict_keys(item, keys_to_redact) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


# Convenience function for quick redaction
def sanitize(obj: Any) -> Any:
    """
    Quick sanitization function - alias for safe().
    
    Args:
        obj: Object to sanitize
        
    Returns:
        Sanitized copy
    """
    return safe(obj)
