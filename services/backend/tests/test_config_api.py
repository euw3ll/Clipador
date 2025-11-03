from __future__ import annotations

from datetime import datetime, timedelta, timezone

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
        jwt_secret="secret",
        redis_url="redis://localhost:6379/0",
        kirvano_token="token",
    )


@pytest.mark.asyncio
async def test_user_config_endpoints(monkeypatch):
    settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.security.auth.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        user = UserAccount(
            username="tester",
            hashed_password=hash_password("password"),
            role="admin",
            plan="Mensal Solo",
            plan_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            status="active",
        )
        session.add(user)
        await session.flush()

    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            login_resp = await client.post(
                "/auth/login",
                json={"username": "tester", "password": "password"},
            )
        except Exception as exc:  # pragma: no cover - surface server errors
            assert False, f"login failed: {exc!r}"
        assert login_resp.status_code == 200, login_resp.text
        tokens = login_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        config_resp = await client.get("/config/me", headers=headers)
        assert config_resp.status_code == 200
        assert config_resp.json()["streamers"] == []

        attach_resp = await client.post(
            "/config/me/streamers",
            headers=headers,
            json={"twitch_user_id": "streamer_one", "display_name": "Streamer One"},
        )
        assert attach_resp.status_code == 201
        config_payload = attach_resp.json()
        assert config_payload["slots_used"] == 1
        streamer_entry = config_payload["streamers"][0]
        streamer_id = streamer_entry["streamer_id"]

        history_empty = await client.get("/config/me/history", headers=headers)
        assert history_empty.status_code == 200
        assert history_empty.json()["items"] == []

        # Record delivery directly via repository to simulate ingestion fan-out
        async with session_scope() as session:
            from clipador_backend.repositories.user_config import UserConfigRepository

            repo = UserConfigRepository(session)
            await repo.record_delivery(
                user_id=1,
                streamer_id=streamer_id,
                burst_start=datetime.now(timezone.utc) - timedelta(minutes=1),
                burst_end=datetime.now(timezone.utc),
                clip_external_id="clip123",
                extra_payload='{"viewer_count": 10}',
            )

        history_resp = await client.get("/config/me/history", headers=headers)
        assert history_resp.status_code == 200
        history_payload = history_resp.json()
        assert len(history_payload["items"]) == 1
        assert history_payload["items"][0]["clip_external_id"] == "clip123"

        detach_resp = await client.delete(f"/config/me/streamers/{streamer_id}", headers=headers)
        assert detach_resp.status_code == 200
        assert detach_resp.json()["streamers"] == []

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
