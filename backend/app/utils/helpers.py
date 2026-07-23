"""Production helpers for the entire application."""
import uuid
import json
import structlog
from datetime import datetime, timezone
from typing import Any

logger = structlog.get_logger()


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sanitize_phone(phone: str) -> str:
    cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
    if not cleaned.startswith("+"):
        if len(cleaned) == 10:
            cleaned = f"+92{cleaned}"
        elif len(cleaned) == 11 and cleaned.startswith("0"):
            cleaned = f"+92{cleaned[1:]}"
        elif len(cleaned) == 12 and cleaned.startswith("92"):
            cleaned = f"+{cleaned}"
    return cleaned


def truncate(text: str, max_length: int = 500) -> str:
    return text[:max_length] + "..." if len(text) > max_length else text


def safe_json_loads(data: str | bytes, default: Any = None) -> Any:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def pagination_meta(page: int, page_size: int, total: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "has_next": page * page_size < total,
        "has_prev": page > 1,
    }


class PhoneFormatter:
    @staticmethod
    def format_pakistani(phone: str) -> str:
        clean = "".join(c for c in phone if c.isdigit())
        if len(clean) == 10:
            return f"+92 {clean[:3]} {clean[3:6]} {clean[6:]}"
        elif len(clean) == 12 and clean.startswith("92"):
            return f"+92 {clean[2:5]} {clean[5:8]} {clean[8:]}"
        return phone
