from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.main import create_app
from clipador_backend.models import Base, UserAccount
from clipador_backend.security.auth import hash_password
from clipador_backend.settings import Settings


def _make_settings(database_url: str = "sqlite+aiosqlite:///:memory:") -> Settings:
    return Settings(
        app_env="test",
        database_url=database_url,
        jwt_secret="test-secret",
        redis_url="redis://localhost:6379/0",
        kirvano_token="webhook-secret",
    )


@pytest.mark.asyncio
async def test_kirvano_webhook_requires_token(monkeypatch):
    settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.api.routes.webhooks.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/webhooks/kirvano", json={})
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_kirvano_webhook_processes_sale(monkeypatch):
    settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.api.routes.webhooks.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        session.add(
            UserAccount(
                username="member",
                email="member@example.com",
                hashed_password=hash_password("secret"),
                plan="free",
            )
        )

    app = create_app()
    payload = {
        "event": "SALE_APPROVED",
        "sale_id": "sale-001",
        "status": "approved",
        "customer": {"email": "member@example.com", "id": "cust-001"},
        "products": [{"offer_name": "Mensal Solo"}],
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/kirvano",
            headers={"Security-Token": "webhook-secret"},
            json=payload,
        )
        assert response.status_code == 200, response.text

    async with session_scope() as session:
        user = await session.get(UserAccount, 1)
        assert user is not None
        assert user.plan.lower() == "mensal solo".lower()
        assert user.plan_expires_at is not None
        assert user.kirvano_last_sale_id == "sale-001"

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
