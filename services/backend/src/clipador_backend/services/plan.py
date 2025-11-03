"""Plan enforcement utilities for Clipador."""

from __future__ import annotations

from datetime import datetime, timezone

from ..models.user import UserAccount
from ..models.channel import UserChannelConfig

PLAN_SLOT_MAP = {
    "teste gratuito": 3,
    "gratuito": 3,
    "mensal solo": 3,
    "mensal plus": 8,
    "anual pro": 15,
    "parceiro": 1,
    "super": 999,
}


def _normalize(plan: str | None) -> str:
    if not plan:
        return "free"
    normalized = plan.strip().lower()
    replacements = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for src, dst in replacements.items():
        normalized = normalized.replace(src, dst)
    return normalized


def base_slots(plan: str | None) -> int:
    normalized = _normalize(plan)
    for key, slots in PLAN_SLOT_MAP.items():
        if key in normalized:
            return slots
    return 1


def resolve_total_slots(user: UserAccount, config: UserChannelConfig | None) -> int:
    base = base_slots(user.plan)
    configured = config.slots_configured if config and config.slots_configured else base
    return max(base, configured)


def is_active(user: UserAccount, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    status_value = (user.status or "").lower()
    if status_value not in {"active", "trial"} and "active" not in status_value:
        return False
    if user.plan_expires_at and user.plan_expires_at < now:
        return False
    return True


def remaining_slots(user: UserAccount, config: UserChannelConfig | None, current_count: int) -> int:
    total = resolve_total_slots(user, config)
    remaining = total - current_count
    return remaining if remaining > 0 else 0


__all__ = ["base_slots", "resolve_total_slots", "is_active", "remaining_slots"]
