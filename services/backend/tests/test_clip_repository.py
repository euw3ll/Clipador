import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from clipador_backend.models import Base, ClipRecord, Streamer, BurstRecord, BurstClip
from clipador_backend.repositories.clips import ClipRepository


@pytest.mark.asyncio
async def test_recent_bursts_returns_grouped_clips():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        now = datetime.now(timezone.utc)
        streamer = Streamer(
            twitch_user_id="streamer1",
            display_name="Streamer 1",
            avatar_url=None,
            monitor_interval_seconds=180,
            monitor_min_clips=2,
        )
        session.add(streamer)
        await session.flush()

        session.add_all(
            [
                ClipRecord(
                    clip_id="a",
                    streamer_id=streamer.id,
                    streamer_name="Streamer 1",
                    streamer_external_id="streamer1",
                    created_at=now - timedelta(minutes=5),
                    viewer_count=150,
                    video_id="va",
                    fetched_at=now,
                ),
                ClipRecord(
                    clip_id="b",
                    streamer_id=streamer.id,
                    streamer_name="Streamer 1",
                    streamer_external_id="streamer1",
                    created_at=now - timedelta(minutes=4, seconds=30),
                    viewer_count=160,
                    video_id="vb",
                    fetched_at=now,
                ),
                ClipRecord(
                    clip_id="c",
                    streamer_id=streamer.id,
                    streamer_name="Streamer 1",
                    streamer_external_id="streamer1",
                    created_at=now - timedelta(minutes=30),
                    viewer_count=200,
                    video_id="vc",
                    fetched_at=now,
                ),
            ]
        )
        await session.flush()

        burst = BurstRecord(
            streamer_id=streamer.id,
            start_time=now - timedelta(minutes=5),
            end_time=now - timedelta(minutes=4),
            clip_count=2,
        )
        session.add(burst)
        await session.flush()

        clips = await session.execute(select(ClipRecord).order_by(ClipRecord.created_at))
        for clip_record in list(clips.scalars())[-2:]:
            session.add(
                BurstClip(
                    burst_id=burst.id,
                    clip_id=clip_record.id,
                    clip_external_id=clip_record.clip_id,
                )
            )
        await session.commit()

    async with session_factory() as session:
        repo = ClipRepository(session)
        bursts = await repo.recent_bursts(since_minutes=60)

    assert len(bursts) == 1
    assert len(bursts[0]["clipes"]) == 2
    assert {clip["id"] for clip in bursts[0]["clipes"]} == {"a", "b"}
    assert bursts[0]["clipes"][0]["streamer_name"] == "Streamer 1"
    assert bursts[0]["clipes"][0]["streamer_external_id"] == "streamer1"

    await engine.dispose()
