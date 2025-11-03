"""Repository for burst persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clipador_core import ClipGroup

from ..models import BurstClip, BurstRecord


class BurstRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_time(self, streamer_id: int, start_time: datetime, end_time: datetime) -> BurstRecord | None:
        result = await self.session.execute(
            select(BurstRecord).where(
                BurstRecord.streamer_id == streamer_id,
                BurstRecord.start_time == start_time,
                BurstRecord.end_time == end_time,
            )
        )
        return result.scalar_one_or_none()

    async def create_from_group(
        self,
        streamer_id: int,
        group: ClipGroup,
        clip_ids: list[int],
        clip_external_ids: list[str],
    ) -> BurstRecord:
        existing = await self.find_by_time(streamer_id, group.start, group.end)
        if existing:
            return existing

        burst = BurstRecord(
            streamer_id=streamer_id,
            start_time=group.start,
            end_time=group.end,
            clip_count=len(clip_ids),
        )
        self.session.add(burst)
        await self.session.flush()

        for clip_db_id, clip_external_id in zip(clip_ids, clip_external_ids):
            self.session.add(
                BurstClip(
                    burst_id=burst.id,
                    clip_id=clip_db_id,
                    clip_external_id=clip_external_id,
                )
            )

        await self.session.flush()
        return burst

    async def list_recent(self, since: datetime) -> list[BurstRecord]:
        result = await self.session.execute(
            select(BurstRecord).where(BurstRecord.start_time >= since).order_by(BurstRecord.start_time.desc())
        )
        return result.scalars().all()
