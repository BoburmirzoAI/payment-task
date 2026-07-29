import logging
from typing import TypedDict, Any, Dict, Optional

from apps.shared.messages import MESSAGES, MessageTemplate

logger = logging.getLogger(__name__)


class MessageDetail(TypedDict):
    id: str
    message: str
    status_code: int


def get_message_detail(
        message_key: str,
        lang: str = "en",
        context: Optional[Dict[str, Any]] = None
) -> MessageDetail:
    message = MESSAGES.get(message_key)

    if not message:
        logger.warning(f"Message key not found: {message_key}")
        message = MESSAGES.get("UNKNOWN_ERROR")
        if not message:
            return {"id": "SYSTEM_ERROR", "message": "An unexpected error occurred", "status_code": 500}

    context = context or {}
    messages_dict = message["messages"]

    base_lang = lang.split('-')[0].split('_')[0]
    template = (
        messages_dict.get(lang)
        or messages_dict.get(base_lang)
        or messages_dict.get("en", "Error occurred")
    )

    try:
        formatted_message: str = template.format(**context)
    except (KeyError, ValueError) as e:
        logger.warning(f"Message formatting failed - key: {message_key}, lang: {lang}, error: {e}")
        formatted_message = template

    return {
        "id": message["id"],
        "message": formatted_message,
        "status_code": message["status_code"],
    }


def get_raw_message(message_key: str) -> Optional[MessageTemplate]:
    return MESSAGES.get(message_key)
