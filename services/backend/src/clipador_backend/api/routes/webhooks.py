"""Webhook endpoints (Kirvano)."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from ...security.dependencies import get_current_user
from ...services import billing
from ...settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/kirvano")
async def kirvano_webhook(request: Request) -> dict[str, str]:
    settings = get_settings()
    token = request.headers.get("Security-Token")
    if not settings.kirvano_token or token != settings.kirvano_token:
        logger.warning("kirvano_invalid_token", extra={"token": token})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    payload = await request.json()
    event_type = payload.get("event")
    email = payload.get("customer", {}).get("email")
    status_value = payload.get("status")

    if not email:
        logger.warning("kirvano_missing_email", extra={"payload": payload})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing")

    logger.info("kirvano_event", extra={"event": event_type, "email": email})

    if event_type in {
        "subscription.canceled",
        "subscription.expired",
        "purchase.refunded",
        "purchase.chargeback",
        "subscription.late",
    }:
        await billing.mark_subscription_ended(email, status_value or "canceled")
    elif event_type == "subscription.renewed":
        plan = payload.get("plan", {}).get("name", "")
        await billing.mark_subscription_renewed(email, plan)
    elif event_type == "SALE_APPROVED":
        sale_id = payload.get("sale_id")
        if not sale_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sale_id missing")
        product = (payload.get("products") or [{}])[0]
        plan = product.get("offer_name") or payload.get("plan", {}).get("name", "")
        await billing.register_purchase(email, plan, status_value or "approved", sale_id, payload)
    else:
        logger.info("kirvano_event_unhandled", extra={"event": event_type})

    return {"status": "success"}
