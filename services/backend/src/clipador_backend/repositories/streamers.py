"""Repository handling streamer configuration."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Streamer


class StreamerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_streamers(self) -> list[Streamer]:
        result = await self.session.execute(select(Streamer).order_by(Streamer.display_name))
        return result.scalars().all()

    async def list_active_streamers(self) -> list[Streamer]:
        result = await self.session.execute(
            select(Streamer).where(Streamer.is_active.is_(True)).order_by(Streamer.display_name)
        )
        return result.scalars().all()

    async def create_streamer(
        self,
        *,
        twitch_user_id: str,
        display_name: str,
        avatar_url: str | None,
        monitor_interval_seconds: int,
        monitor_min_clips: int,
        api_mode: str,
        trial_expires_at: datetime | None,
        client_twitch_client_id: str | None,
        client_twitch_client_secret: str | None,
    ) -> Streamer:
        streamer = Streamer(
            twitch_user_id=twitch_user_id,
            display_name=display_name,
            avatar_url=avatar_url,
            monitor_interval_seconds=monitor_interval_seconds,
            monitor_min_clips=monitor_min_clips,
            api_mode=api_mode,
            trial_expires_at=trial_expires_at,
            client_twitch_client_id=client_twitch_client_id,
            client_twitch_client_secret=client_twitch_client_secret,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(streamer)
        await self.session.flush()
        return streamer

    async def get_by_twitch_id(self, twitch_user_id: str) -> Streamer | None:
        result = await self.session.execute(
            select(Streamer).where(Streamer.twitch_user_id == twitch_user_id)
        )
        return result.scalar_one_or_none()

    async def delete_streamer(self, streamer_id: int) -> None:
        streamer = await self.session.get(Streamer, streamer_id)
        if streamer:
            await self.session.delete(streamer)

    async def touch(self, streamer: Streamer) -> None:
        streamer.updated_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def update_last_synced(self, streamer: Streamer) -> None:
        streamer.last_clip_synced_at = datetime.now(timezone.utc)


__all__ = ["StreamerRepository"]
