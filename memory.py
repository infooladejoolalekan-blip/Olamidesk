"""
memory.py
Handles conversation memory and user database records.
"""

import logging
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from config import settings
from database import get_session
from models import User, Conversation

logger = logging.getLogger(__name__)


async def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> User:
    """Ensures the user exists in the database. Updates their name if changed."""
    async with get_session() as session:
        # Check if user exists
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # Update names if they changed
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            return user
            
        # If not, create a new user
        new_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        session.add(new_user)
        return new_user


async def add_message_to_history(telegram_id: int, role: str, content: str) -> None:
    """Saves a single message (user or assistant) to the database."""
    async with get_session() as session:
        msg = Conversation(
            telegram_id=telegram_id,
            role=role,
            content=content
        )
        session.add(msg)


async def get_conversation_history(telegram_id: int) -> list[dict]:
    """
    Fetches the most recent messages for the AI context.
    Returns a list of dicts: [{"role": "user", "content": "..."}, ...]
    """
    async with get_session() as session:
        # Fetch the most recent N messages (ordered newest first)
        stmt = (
            select(Conversation)
            .where(Conversation.telegram_id == telegram_id)
            .order_by(Conversation.created_at.desc())
            .limit(settings.max_history_messages)
        )
        result = await session.execute(stmt)
        messages = result.scalars().all()

        # Reverse the list so it is oldest-to-newest (as AI APIs require)
        messages.reverse()

        # Format for the API
        return [{"role": m.role, "content": m.content} for m in messages]


async def clear_user_history(telegram_id: int) -> None:
    """Deletes all conversation history for a user (used by /reset)."""
    async with get_session() as session:
        stmt = delete(Conversation).where(Conversation.telegram_id == telegram_id)
        await session.execute(stmt)
        logger.info(f"Cleared AI conversation history for user {telegram_id}")