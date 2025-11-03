"""Seed database with streamers and clips from CSV files."""

from __future__ import annotations

import argparse
import asyncio
import csv
import datetime
from pathlib import Path
from typing import Optional

from clipador_backend.db import session_scope
from clipador_backend.models import ClipRecord, Streamer
from sqlalchemy import select


def parse_datetime(value: str) -> Optional[datetime.datetime]:
    if not value:
        return None
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


async def seed_streamers(path: Path) -> None:
    async with session_scope() as session:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                twitch_user_id = row.get("twitch_user_id")
                if not twitch_user_id:
                    continue
                existing = await session.execute(select(Streamer).where(Streamer.twitch_user_id == twitch_user_id))
                if existing.scalar_one_or_none():
                    continue
                streamer = Streamer(
                    twitch_user_id=twitch_user_id,
                    display_name=row.get("display_name") or twitch_user_id,
                    avatar_url=row.get("avatar_url"),
                    monitor_interval_seconds=int(row.get("monitor_interval_seconds") or 180),
                    monitor_min_clips=int(row.get("monitor_min_clips") or 2),
                    api_mode=(row.get("api_mode") or "clipador_only").lower(),
                    trial_expires_at=parse_datetime(row.get("trial_expires_at", "")),
                    client_twitch_client_id=row.get("client_twitch_client_id"),
                    client_twitch_client_secret=row.get("client_twitch_client_secret"),
                )
                session.add(streamer)
            await session.flush()


async def seed_clips(path: Path) -> None:
    async with session_scope() as session:
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                clip_id = row.get("clip_id")
                if not clip_id:
                    continue
                existing = await session.execute(select(ClipRecord).where(ClipRecord.clip_id == clip_id))
                if existing.scalar_one_or_none():
                    continue

                streamer_external_id = row.get("streamer_twitch_user_id")
                if not streamer_external_id:
                    continue

                streamer_result = await session.execute(
                    select(Streamer).where(Streamer.twitch_user_id == streamer_external_id)
                )
                streamer = streamer_result.scalar_one_or_none()
                if streamer is None:
                    continue

                created_at = parse_datetime(row.get("created_at")) or datetime.datetime.now(datetime.timezone.utc)

                clip = ClipRecord(
                    clip_id=clip_id,
                    streamer_id=streamer.id,
                    streamer_name=row.get("streamer_name") or streamer.display_name,
                    streamer_external_id=streamer.twitch_user_id,
                    created_at=created_at,
                    viewer_count=int(row.get("viewer_count") or 0),
                    video_id=row.get("video_id"),
                    title=row.get("title"),
                    duration=int(float(row.get("duration") or 0)),
                )
                session.add(clip)
            await session.flush()


async def run(streamers: Optional[Path], clips: Optional[Path]) -> None:
    if streamers:
        await seed_streamers(streamers)
        print(f"Seeded streamers from {streamers}")
    if clips:
        await seed_clips(clips)
        print(f"Seeded clips from {clips}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Clipador data from CSV files")
    parser.add_argument("--streamers", type=Path, help="CSV with streamers", required=False)
    parser.add_argument("--clips", type=Path, help="CSV with clips", required=False)
    args = parser.parse_args()

    asyncio.run(run(args.streamers, args.clips))


if __name__ == "__main__":
    main()
