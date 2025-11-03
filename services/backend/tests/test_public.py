import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.main import create_app
from clipador_backend.models import Base, ClipRecord, Streamer
from clipador_backend.settings import Settings


@pytest.mark.asyncio
async def test_public_clips_endpoint(monkeypatch):
    settings = Settings(
        app_env="test",
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret="secret",
    )

    monkeypatch.setattr("clipador_backend.settings.get_settings", lambda: settings)
    monkeypatch.setattr("clipador_backend.db.get_settings", lambda: settings)

    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_scope() as session:
        streamer = Streamer(
            twitch_user_id="123",
            display_name="Streamer",
            avatar_url=None,
        )
        session.add(streamer)
        await session.flush()
        session.add(
            ClipRecord(
                clip_id="abc",
                streamer_id=streamer.id,
                streamer_name=streamer.display_name,
                streamer_external_id=streamer.twitch_user_id,
                created_at=datetime.datetime.now(datetime.timezone.utc),
                viewer_count=100,
                video_id="vid",
                title="Clip",
                duration=30,
                fetched_at=datetime.datetime.now(datetime.timezone.utc),
            )
        )
        await session.flush()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/public/clips")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["id"] == "abc"

    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
