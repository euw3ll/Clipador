from datetime import datetime, timezone

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.models import Base, UserAccount
from clipador_backend.security.auth import (
    ALGORITHM,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from clipador_backend.settings import Settings
from clipador_backend.main import create_app


def test_create_and_decode_access_token(monkeypatch):
    fake_secret = "secret-key"

    class FakeSettings:
        jwt_secret = fake_secret
        app_env = "test"
        jwt_access_minutes = 5
        jwt_refresh_days = 7

    monkeypatch.setattr("clipador_backend.security.auth.get_settings", lambda: FakeSettings())

    token = create_access_token("user-123", extra={"role": "admin"})
    decoded = decode_token(token)

    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "admin"
    assert decoded["exp"] > decoded["iat"]
    jwt.decode(token, fake_secret, algorithms=[ALGORITHM])  # não levanta exceção

    refresh = create_refresh_token("user-123")
    decoded_refresh = decode_token(refresh)
    assert decoded_refresh["type"] == "refresh"


def test_password_hashing():
    hashed = hash_password("super-secret")
    assert hashed != "super-secret"
    assert verify_password("super-secret", hashed) is True
    assert verify_password("wrong", hashed) is False


@pytest.mark.asyncio
async def test_login_route_authenticates(monkeypatch):
    test_settings = Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret="test-secret",
    )

    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: test_settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: test_settings)
    monkeypatch.setattr("clipador_backend.security.auth.get_settings", lambda: test_settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        user = UserAccount(username="admin", hashed_password=hash_password("123456"))
        session.add(user)
        await session.flush()

    app = create_app()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/login", json={"username": "admin", "password": "123456"})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert "access_token" in payload
        assert "refresh_token" in payload
        assert payload["token_type"] == "bearer"

        refresh_resp = await client.post("/auth/refresh", json={"refresh_token": payload["refresh_token"]})
        assert refresh_resp.status_code == 200
        new_tokens = refresh_resp.json()
        assert new_tokens["access_token"]
        me_resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {new_tokens['access_token']}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == "admin"

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
