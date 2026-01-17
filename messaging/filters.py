"""Content filtering for messages to protect young users."""
import re
from django.core.cache import cache
from .models import BlockedWord

FILTER_CACHE_KEY = 'blocked_words_pattern'
CACHE_TIMEOUT = 3600  # 1 hour


def get_blocked_pattern():
    """Get compiled regex pattern for blocked words (cached)."""
    pattern = cache.get(FILTER_CACHE_KEY)
    if pattern is None:
        words = BlockedWord.objects.filter(is_active=True).values_list('word', flat=True)
        if words:
            # Build case-insensitive pattern with word boundaries
            escaped = [re.escape(w) for w in words]
            pattern = re.compile(r'\b(' + '|'.join(escaped) + r')\b', re.IGNORECASE)
        else:
            pattern = None
        cache.set(FILTER_CACHE_KEY, pattern, CACHE_TIMEOUT)
    return pattern


def filter_content(text):
    """
    Filter blocked words from text.
    Returns tuple: (filtered_text, was_filtered)
    """
    if not text:
        return text, False

    pattern = get_blocked_pattern()
    if pattern is None:
        return text, False

    # Replace matches with asterisks
    filtered = pattern.sub(lambda m: '*' * len(m.group()), text)
    was_filtered = filtered != text
    return filtered, was_filtered


def invalidate_filter_cache():
    """Call this when BlockedWord model changes."""
    cache.delete(FILTER_CACHE_KEY)


def check_username_allowed(username):
    """
    Check if a username contains blocked words.
    Returns tuple: (is_allowed, reason)
    """
    if not username:
        return False, "Username is required"

    username_lower = username.lower()

    # Check against blocked words
    blocked_words = BlockedWord.objects.filter(is_active=True).values_list('word', flat=True)
    for word in blocked_words:
        if word.lower() in username_lower:
            return False, "This username contains inappropriate content"

    return True, None
