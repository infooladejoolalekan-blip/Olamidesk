"""
utils.py
Shared helper functions: rate limiting, reference IDs, text truncation.
"""

import asyncio
import secrets
import string
from datetime import datetime, timezone
from typing import Dict

from config import settings

# ─── Rate Limiter ────────────────────────────────────────────────────
# Stores the last message timestamp for each user.
# Prevents spamming the AI and DeepSeek API.
_last_message_time: Dict[int, float] = {}


def check_rate_limit(user_id: int) -> tuple[bool, float]:
    """
    Returns (allowed, seconds_remaining).
    If the user sent a message too recently, they are blocked.
    """
    now = asyncio.get_event_loop().time()
    last = _last_message_time.get(user_id, 0.0)
    elapsed = now - last

    if elapsed < settings.rate_limit_seconds:
        remaining = settings.rate_limit_seconds - elapsed
        return False, remaining

    _last_message_time[user_id] = now
    return True, 0.0


def reset_rate_limit(user_id: int) -> None:
    """Clear rate limit for a user (e.g. after an admin reply)."""
    _last_message_time.pop(user_id, None)


# ─── Reference ID Generator ──────────────────────────────────────────
def generate_reference() -> str:
    """
    Generates a unique enquiry reference.
    Format: ENQ-YYYYMMDD-XXXXX (5 uppercase letters/digits)
    """
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    return f"ENQ-{date_part}-{random_part}"


# ─── Text Helpers ────────────────────────────────────────────────────
def truncate_text(text: str, max_length: int = 4000) -> str:
    """
    Telegram messages must be under 4096 characters.
    Safely truncates long text with an ellipsis.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def truncate_for_ai(text: str, max_length: int = 2000) -> str:
    """
    Limits user input sent to DeepSeek to control API cost.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + " [truncated]"


def safe_display_name(username: str | None, first_name: str | None, telegram_id: int) -> str:
    """
    Returns a readable name for logs and admin display.
    Falls back to telegram ID if no name is available.
    """
    if username:
        return f"@{username}"
    if first_name:
        return first_name
    return f"User {telegram_id}"


def escape_markdown(text: str) -> str:
    """
    Escapes characters that break Telegram Markdown parsing.
    Use this before sending text with parse_mode='Markdown'.
    """
    special_chars = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text