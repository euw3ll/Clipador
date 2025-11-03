import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from clipador_backend import db as db_module
from clipador_backend.db import get_engine, session_scope
from clipador_backend.models import Base, Streamer
from clipador_backend.repositories.bursts import BurstRepository
from clipador_backend.repositories.clips import ClipRepository
from clipador_backend.repositories.streamers import StreamerRepository
from clipador_backend.services.ingestion import ClipIngestionService
from clipador_backend.settings import Settings


class FakeTwitch:
    def __init__(self, clips):
        self._clips = clips
        self.calls = 0

    async def get_clips(self, broadcaster_id: str, started_at: datetime, **kwargs):
        self.calls += 1
        return self._clips

    async def get_stream_info(self, user_id: str):  # pragma: no cover
        return None

    async def get_vod_by_id(self, vod_id: str):  # pragma: no cover
        return None

    async def aclose(self):
        return None


@pytest.mark.asyncio
async def test_ingestion_creates_clips_and_bursts(monkeypatch):
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

    now = datetime.now(timezone.utc)

    async with session_scope() as session:
        streamer = Streamer(
            twitch_user_id="12345",
            display_name="Streamer",
            avatar_url=None,
        )
        session.add(streamer)
        await session.flush()

    fake_clips = [
        {
            "id": "clipA",
            "created_at": (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
            "broadcaster_name": "Streamer",
            "broadcaster_id": "12345",
            "view_count": 150,
            "duration": 30,
            "title": "Clip A",
            "video_id": "vid1",
        },
        {
            "id": "clipB",
            "created_at": (now - timedelta(minutes=4, seconds=30)).isoformat().replace("+00:00", "Z"),
            "broadcaster_name": "Streamer",
            "broadcaster_id": "12345",
            "view_count": 200,
            "duration": 28,
            "title": "Clip B",
            "video_id": "vid2",
        },
    ]

    service = ClipIngestionService(FakeTwitch(fake_clips))
    await service.sync_once()

    async with session_scope() as session:
        clip_repo = ClipRepository(session)
        burst_repo = BurstRepository(session)

        clips = await clip_repo.list_recent_clips(since_minutes=60, streamer_id="12345")
        assert len(clips) == 2

        recent_bursts = await burst_repo.list_recent(now - timedelta(minutes=10))
        assert len(recent_bursts) == 1
        burst = recent_bursts[0]
        assert burst.clip_count == 2

    await service.aclose()
    await engine.dispose()
    db_module._ENGINE = None
    db_module._SESSION_FACTORY = None
