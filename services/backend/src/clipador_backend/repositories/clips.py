"""Repositório de acesso a clipes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clipador_core import BurstConfig, Clip, group_clips_by_burst, minimo_clipes_por_viewers

from ..models import BurstClip, BurstRecord, ClipRecord, Streamer


class ClipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def clip_exists(self, clip_external_id: str) -> bool:
        result = await self.session.execute(
            select(ClipRecord.id).where(ClipRecord.clip_id == clip_external_id)
        )
        return result.scalar_one_or_none() is not None

    async def create_clip(
        self,
        *,
        clip_id: str,
        streamer_id: int,
        streamer_name: str,
        streamer_external_id: str,
        created_at: datetime,
        viewer_count: int,
        video_id: str | None,
        title: str | None,
        duration: int | None,
        broadcaster_level: int | None,
    ) -> ClipRecord:
        record = ClipRecord(
            clip_id=clip_id,
            streamer_id=streamer_id,
            streamer_name=streamer_name,
            streamer_external_id=streamer_external_id,
            created_at=created_at,
            viewer_count=viewer_count,
            video_id=video_id,
            title=title,
            duration=duration,
            broadcaster_level=broadcaster_level,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_clips_by_external_ids(self, clip_ids: list[str]) -> dict[str, ClipRecord]:
        if not clip_ids:
            return {}
        result = await self.session.execute(
            select(ClipRecord).where(ClipRecord.clip_id.in_(clip_ids))
        )
        return {clip.clip_id: clip for clip in result.scalars()}

    async def list_recent_clips(
        self,
        *,
        since_minutes: int = 60,
        streamer_id: str | None = None,
    ) -> list[Clip]:
        min_created = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
        stmt = (
            select(ClipRecord, Streamer)
            .join(Streamer, Streamer.id == ClipRecord.streamer_id)
            .where(ClipRecord.created_at >= min_created)
            .order_by(ClipRecord.created_at)
        )
        if streamer_id:
            stmt = stmt.where(Streamer.twitch_user_id == streamer_id)

        rows = await self.session.execute(stmt)
        records = rows.all()
        return [
            Clip(
                id=clip.clip_id,
                created_at=clip.created_at,
                viewer_count=clip.viewer_count,
                video_id=clip.video_id,
                streamer_name=streamer.display_name,
                streamer_external_id=streamer.twitch_user_id,
            )
            for clip, streamer in records
        ]

    async def recent_bursts(
        self,
        *,
        since_minutes: int = 60,
    ) -> list[dict[str, object]]:
        min_start = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)

        stmt = (
            select(BurstRecord, ClipRecord, Streamer)
            .join(BurstClip, BurstClip.burst_id == BurstRecord.id)
            .join(ClipRecord, ClipRecord.id == BurstClip.clip_id)
            .join(Streamer, Streamer.id == BurstRecord.streamer_id)
            .where(BurstRecord.start_time >= min_start)
            .order_by(BurstRecord.start_time, ClipRecord.created_at)
        )

        result = await self.session.execute(stmt)
        bursts_map: dict[int, dict[str, object]] = {}
        clip_lists: dict[int, list[dict[str, object]]] = defaultdict(list)

        for burst, clip, streamer in result.all():
            if burst.id not in bursts_map:
                bursts_map[burst.id] = {
                    "inicio": burst.start_time.isoformat(),
                    "inicio_iso": burst.start_time.isoformat(),
                    "fim": burst.end_time.isoformat(),
                    "streamer": {
                        "id": streamer.id,
                        "display_name": streamer.display_name,
                        "twitch_user_id": streamer.twitch_user_id,
                    },
                }

            clip_lists[burst.id].append(
                {
                    "id": clip.clip_id,
                    "created_at": clip.created_at.isoformat(),
                    "viewer_count": clip.viewer_count,
                    "video_id": clip.video_id,
                    "streamer_name": clip.streamer_name,
                    "streamer_external_id": clip.streamer_external_id,
                }
            )

        payload = []
        for burst_id, info in bursts_map.items():
            clips_payload = clip_lists.get(burst_id, [])
            payload.append({"inicio": info["inicio"], "inicio_iso": info["inicio_iso"], "fim": info["fim"], "streamer": info["streamer"], "clipes": clips_payload})

        payload.sort(key=lambda item: item["inicio"], reverse=True)
        return payload

    async def list_public_clips(self, *, limit: int = 12) -> list[dict[str, object]]:
        stmt = (
            select(ClipRecord, Streamer)
            .join(Streamer, Streamer.id == ClipRecord.streamer_id)
            .order_by(ClipRecord.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        clips = []
        for clip, streamer in result.all():
            clips.append(
                {
                    "id": clip.clip_id,
                    "created_at": clip.created_at.isoformat(),
                    "viewer_count": clip.viewer_count,
                    "title": clip.title,
                    "duration": clip.duration,
                    "streamer_name": streamer.display_name,
                    "streamer_external_id": streamer.twitch_user_id,
                }
            )
        return clips
