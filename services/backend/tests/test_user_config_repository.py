from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.models import Base, Streamer, UserAccount
from clipador_backend.repositories.user_config import UserConfigRepository
from clipador_backend.security.auth import hash_password
from clipador_backend.settings import Settings


def _make_settings(database_url: str = "sqlite+aiosqlite:///:memory:") -> Settings:
    return Settings(
        app_env="test",
        database_url=database_url,
        jwt_secret="test",
    )


@pytest.mark.asyncio
async def test_ensure_config_and_streamers(monkeypatch):
    settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        user = UserAccount(username="demo", hashed_password=hash_password("secret"))
        streamer = Streamer(
            twitch_user_id="streamer_1",
            display_name="Streamer 1",
            is_active=True,
        )
        session.add_all([user, streamer])
        await session.flush()

        repo = UserConfigRepository(session)
        config = await repo.ensure_config(user.id)
        assert config.user_id == user.id
        assert config.monitor_mode == "AUTOMATICO"

        attached = await repo.attach_streamer(user_id=user.id, streamer_id=streamer.id)
        assert attached.user_id == user.id
        assert attached.streamer_id == streamer.id

        with pytest.raises(ValueError):
            await repo.attach_streamer(user_id=user.id, streamer_id=streamer.id)

        count = await repo.count_user_streamers(user.id)
        assert count == 1

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None


@pytest.mark.asyncio
async def test_record_delivery(monkeypatch):
    settings = _make_settings()
    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        user = UserAccount(username="demo", hashed_password=hash_password("secret"))
        streamer = Streamer(
            twitch_user_id="streamer_1",
            display_name="Streamer 1",
            is_active=True,
        )
        session.add_all([user, streamer])
        await session.flush()

        repo = UserConfigRepository(session)
        await repo.ensure_config(user.id)

        start = datetime.now(timezone.utc) - timedelta(minutes=5)
        end = start + timedelta(minutes=1)

        delivery = await repo.record_delivery(
            user_id=user.id,
            streamer_id=streamer.id,
            burst_start=start,
            burst_end=end,
            clip_external_id="clip123",
        )
        assert delivery.clip_external_id == "clip123"

        with pytest.raises(ValueError):
            await repo.record_delivery(
                user_id=user.id,
                streamer_id=streamer.id,
                burst_start=start,
                burst_end=end,
                clip_external_id="clip123",
            )

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
