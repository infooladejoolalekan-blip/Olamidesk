"""
deepseek.py
Handles communication with the DeepSeek API.
Uses the OpenAI-compatible client since DeepSeek follows that standard.
"""

import logging
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError

from config import settings
from knowledge_base import SYSTEM_PROMPT
from utils import truncate_for_ai

logger = logging.getLogger(__name__)

# Initialize the client using the DeepSeek base URL
client = AsyncOpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url,
    timeout=30.0,  # 30-second timeout to prevent hanging
    max_retries=2  # Automatically retry failed requests twice
)


async def generate_ai_response(user_message: str, history: list[dict]) -> str:
    """
    Sends the user message and conversation history to DeepSeek.
    Returns the AI's text response, or a fallback error message.
    """
    # Truncate the user message to prevent massive API costs from a single long message
    safe_user_message = truncate_for_ai(user_message)

    # Build the message list: System prompt first, then history, then the new message
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add previous conversation history
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Add the current user message
    messages.append({"role": "user", "content": safe_user_message})

    try:
        # Call the DeepSeek API
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            temperature=0.7,  # 0.7 gives a natural, conversational tone
            max_tokens=800,   # Limit response length
        )
        
        # Extract the text
        ai_text = response.choices[0].message.content
        return ai_text.strip() if ai_text else "I'm sorry, I couldn't generate a response just now."

    except RateLimitError:
        logger.warning("DeepSeek API rate limit reached.")
        return "I'm receiving too many requests right now. Please try again in a minute."
        
    except APIConnectionError:
        logger.error("DeepSeek API connection error.")
        return "I'm having trouble connecting to my AI brain. Please try again shortly."
        
    except APIError as e:
        logger.error(f"DeepSeek API returned an error: {e}")
        return "I encountered a temporary issue while thinking. Please try again."
        
    except Exception as e:
        logger.error(f"Unexpected error in DeepSeek call: {e}")
        return "Something went wrong on my end. Please try again or type /contact for support."