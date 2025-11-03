import pytest
from httpx import ASGITransport, AsyncClient

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.main import create_app
from clipador_backend.models import Base, UserAccount
from clipador_backend.security.auth import hash_password
from clipador_backend.settings import Settings


@pytest.mark.asyncio
async def test_stream_crud_requires_auth(monkeypatch):
    settings = Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret="secret",
    )

    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.security.auth.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        session.add(UserAccount(username="admin", hashed_password=hash_password("123456")))
        await session.flush()

    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post("/auth/login", json={"username": "admin", "password": "123456"})
        assert login.status_code == 200
        token = login.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        create_resp = await client.post(
            "/streams",
            json={
                "twitch_user_id": "user123",
                "display_name": "Streamer",
                "monitor_interval_seconds": 180,
                "monitor_min_clips": 2,
                "api_mode": "clipador_only",
            },
            headers=headers,
        )
        assert create_resp.status_code == 201, create_resp.text
        created = create_resp.json()
        streamer_id = created["id"]
        assert created["api_mode"] == "clipador_only"
        assert created["has_client_credentials"] is False

        list_resp = await client.get("/streams", headers=headers)
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert len(data) == 1
        assert data[0]["id"] == streamer_id
        assert data[0]["has_client_credentials"] is False
        assert data[0]["api_mode"] == "clipador_only"

        delete_resp = await client.delete(f"/streams/{streamer_id}", headers=headers)
        assert delete_resp.status_code == 204

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
