from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.models import Base, UserAccount
from clipador_backend.security.auth import hash_password
from clipador_backend.services import billing
from clipador_backend.services.billing import _calculate_expiration
from clipador_backend.settings import Settings


def _make_settings(database_url: str = "sqlite+aiosqlite:///:memory:") -> Settings:
    return Settings(
        app_env="test",
        database_url=database_url,
        jwt_secret="test-secret",
        redis_url="redis://localhost:6379/0",
        kirvano_token="kirvano-test",
    )


@pytest.mark.asyncio
async def test_calculate_expiration_extends_future() -> None:
    future = datetime.now(timezone.utc) + timedelta(days=10)
    extended = _calculate_expiration("mensal solo", base=future)
    assert extended > future
    assert (extended - future).days >= 31


@pytest.mark.asyncio
async def test_register_purchase_updates_user(monkeypatch):
    test_settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: test_settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: test_settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        user = UserAccount(
            username="member",
            hashed_password=hash_password("secret"),
            email="member@example.com",
            plan="free",
            plan_expires_at=None,
        )
        session.add(user)
        await session.flush()

    payload = {
        "sale_id": "sale-123",
        "plan": {"name": "Mensal Solo"},
        "status": "approved",
        "customer": {"email": "member@example.com", "id": "cust-999"},
        "products": [{"offer_name": "Mensal Solo"}],
    }

    await billing.register_purchase("member@example.com", "Mensal Solo", "approved", "sale-123", payload)

    async with session_scope() as session:
        refreshed = await session.get(UserAccount, 1)
        assert refreshed is not None
        assert refreshed.plan.lower() == "mensal solo".lower()
        assert refreshed.plan_expires_at is not None
        assert refreshed.status == "active"
        assert refreshed.kirvano_customer_id == "cust-999"
        assert refreshed.kirvano_last_sale_id == "sale-123"

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None


@pytest.mark.asyncio
async def test_renewal_extends_existing_period(monkeypatch):
    test_settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: test_settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: test_settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    future = datetime.now(timezone.utc) + timedelta(days=15)

    async with session_scope() as session:
        user = UserAccount(
            username="member",
            hashed_password=hash_password("secret"),
            email="member@example.com",
            plan="Mensal Solo",
            plan_expires_at=future,
        )
        session.add(user)
        await session.flush()

    await billing.mark_subscription_renewed("member@example.com", "Mensal Solo")

    async with session_scope() as session:
        refreshed = await session.get(UserAccount, 1)
        assert refreshed is not None
        assert refreshed.plan_expires_at is not None
        renewed_exp = refreshed.plan_expires_at
        if renewed_exp.tzinfo is None:
            renewed_exp = renewed_exp.replace(tzinfo=timezone.utc)
        assert renewed_exp > future

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
