"""Billing and subscription helpers for Kirvano integration."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from sqlalchemy import func, select

from ..db import session_scope
from ..models import PurchaseRecord, UserAccount

logger = logging.getLogger(__name__)

TEST_TRIAL_DAYS = 3
PLAN_DURATIONS = {
    "teste gratuito": TEST_TRIAL_DAYS,
    "mensal solo": 31,
    "mensal plus": 31,
    "parceiro": 365,
    "anual pro": 365,
    "super": 365,
}


def _normalize_name(plan: str | None) -> str:
    if not plan:
        return "free"
    normalized = plan.strip().lower()
    translations = {
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
    for src, dst in translations.items():
        normalized = normalized.replace(src, dst)
    return normalized


def _calculate_expiration(plan_name: str, base: datetime | None = None) -> datetime:
    normalized = _normalize_name(plan_name)
    days = PLAN_DURATIONS.get(normalized, 31)
    now = datetime.now(timezone.utc)
    if base:
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)
        current = base if base > now else now
    else:
        current = now
    return current + timedelta(days=days)


async def _find_user_by_email(email: str) -> UserAccount | None:
    async with session_scope() as session:
        result = await session.execute(
            select(UserAccount).where(func.lower(UserAccount.email) == email.strip().lower())
        )
        return result.scalar_one_or_none()


async def register_purchase(email: str, plan: str, status: str, sale_id: str, payload: Dict[str, Any]) -> None:
    async with session_scope() as session:
        existing = await session.execute(select(PurchaseRecord).where(PurchaseRecord.sale_id == sale_id))
        if existing.scalar_one_or_none():
            logger.info("purchase_already_recorded", extra={"sale_id": sale_id})
            return

        customer = payload.get("customer", {})
        purchase = PurchaseRecord(
            sale_id=sale_id,
            email=email,
            plan=plan,
            status=status,
            payment_method=payload.get("payment", {}).get("method"),
            raw_payload=json.dumps(payload, ensure_ascii=False),
        )
        session.add(purchase)

        user_result = await session.execute(
            select(UserAccount).where(func.lower(UserAccount.email) == email.strip().lower())
        )
        user = user_result.scalar_one_or_none()
        if not user:
            logger.warning("purchase_without_user", extra={"email": email, "sale_id": sale_id})
            return

        expires_at = _calculate_expiration(plan, base=user.plan_expires_at)
        user.plan = plan
        user.plan_expires_at = expires_at
        user.status = "active"
        user.kirvano_last_sale_id = sale_id
        if not user.email:
            user.email = email
        if customer.get("id"):
            user.kirvano_customer_id = customer.get("id")
        if "teste" in plan.lower():
            user.trial_used = True

        logger.info(
            "plan_assigned",
            extra={
                "email": email,
                "plan": plan,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )


async def mark_subscription_ended(email: str, status: str) -> None:
    async with session_scope() as session:
        result = await session.execute(
            select(UserAccount).where(func.lower(UserAccount.email) == email.strip().lower())
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning("cancel_without_user", extra={"email": email})
            return

        user.plan = "free"
        user.plan_expires_at = None
        user.status = status or "inactive"
        logger.info("plan_revoked", extra={"email": email, "status": status})


async def mark_subscription_renewed(email: str, plan: str) -> None:
    async with session_scope() as session:
        result = await session.execute(
            select(UserAccount).where(func.lower(UserAccount.email) == email.strip().lower())
        )
        user = result.scalar_one_or_none()
        if not user:
            logger.warning("renew_without_user", extra={"email": email})
            return

        expires_at = _calculate_expiration(plan, base=user.plan_expires_at)
        user.plan = plan
        user.plan_expires_at = expires_at
        user.status = "active"
        logger.info(
            "plan_renewed",
            extra={
                "email": email,
                "plan": plan,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )
