"""
config.py
Reads and validates all environment variables.
Every other module imports `settings` from this file.
"""

import os
import logging
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load .env file for local testing. On Railway, variables are set in the dashboard.
load_dotenv()


def _get_env(name: str, required: bool = True, default: str = "") -> str:
    """Fetch an environment variable, optionally required."""
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Please set it in Railway Variables or your .env file."
        )
    return value


@dataclass(frozen=True)
class Settings:
    # Telegram
    telegram_bot_token: str = field(default_factory=lambda: _get_env("TELEGRAM_BOT_TOKEN"))
    bot_username: str = field(default_factory=lambda: _get_env("BOT_USERNAME", required=False, default="OlamideskAssistantBot"))

    # DeepSeek / OpenAI-compatible
    deepseek_api_key: str = field(default_factory=lambda: _get_env("DEEPSEEK_API_KEY"))
    deepseek_base_url: str = field(default_factory=lambda: _get_env("DEEPSEEK_BASE_URL", required=False, default="https://api.deepseek.com/v1"))
    deepseek_model: str = field(default_factory=lambda: _get_env("DEEPSEEK_MODEL", required=False, default="deepseek-chat"))

    # Admin (password-based authentication, not telegram_id)
    admin_password: str = field(default_factory=lambda: _get_env("ADMIN_PASSWORD"))
    support_username: str = field(default_factory=lambda: _get_env("SUPPORT_USERNAME", required=False, default=""))

    # Database
    database_url: str = field(default_factory=lambda: _get_env("DATABASE_URL"))

    # Behaviour
    max_history_messages: int = field(default_factory=lambda: int(_get_env("MAX_HISTORY_MESSAGES", required=False, default="20")))
    rate_limit_seconds: int = field(default_factory=lambda: int(_get_env("RATE_LIMIT_SECONDS", required=False, default="3")))
    log_level: str = field(default_factory=lambda: _get_env("LOG_LEVEL", required=False, default="INFO"))


settings = Settings()


def configure_logging() -> None:
    """Set up logging once at startup."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )