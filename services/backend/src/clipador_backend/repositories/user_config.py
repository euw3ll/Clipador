"""Repository helpers for user channel configuration and deliveries."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    ClipDelivery,
    Streamer,
    StreamerStatus,
    UserChannelConfig,
    UserStreamer,
)


class UserConfigRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_config(self, user_id: int) -> UserChannelConfig | None:
        stmt = select(UserChannelConfig).where(UserChannelConfig.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_config(self, user_id: int) -> UserChannelConfig:
        result = await self.session.execute(
            select(UserChannelConfig).where(UserChannelConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        if config:
            return config

        config = UserChannelConfig(user_id=user_id)
        self.session.add(config)
        await self.session.flush()
        return config

    async def update_config(self, user_id: int, **fields) -> UserChannelConfig:
        config = await self.ensure_config(user_id)
        for key, value in fields.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return config

    async def list_user_streamers(self, user_id: int) -> list[tuple[UserStreamer, Streamer]]:
        stmt = (
            select(UserStreamer, Streamer)
            .join(Streamer, Streamer.id == UserStreamer.streamer_id)
            .where(UserStreamer.user_id == user_id)
            .order_by(UserStreamer.order_index, Streamer.display_name)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def attach_streamer(
        self,
        *,
        user_id: int,
        streamer_id: int,
        label: str | None = None,
        order_index: int | None = None,
    ) -> UserStreamer:
        await self.ensure_config(user_id)
        existing = await self.session.execute(
            select(UserStreamer).where(
                UserStreamer.user_id == user_id, UserStreamer.streamer_id == streamer_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Streamer already associated with user")
        if order_index is None:
            order_stmt = select(func.coalesce(func.max(UserStreamer.order_index), 0)).where(
                UserStreamer.user_id == user_id
            )
            order_index = (await self.session.execute(order_stmt)).scalar_one() + 1

        mapping = UserStreamer(
            user_id=user_id,
            streamer_id=streamer_id,
            label=label,
            order_index=order_index,
        )
        self.session.add(mapping)
        await self.session.flush()
        return mapping

    async def detach_streamer(self, *, user_id: int, streamer_id: int) -> None:
        stmt = (
            delete(UserStreamer)
            .where(UserStreamer.user_id == user_id)
            .where(UserStreamer.streamer_id == streamer_id)
        )
        await self.session.execute(stmt)

    async def set_streamer_order(self, user_id: int, streamer_order: Sequence[int]) -> None:
        existing = await self.session.execute(
            select(UserStreamer).where(UserStreamer.user_id == user_id)
        )
        mapping = {item.streamer_id: item for item in existing.scalars()}
        for index, streamer_id in enumerate(streamer_order):
            if streamer_id in mapping:
                mapping[streamer_id].order_index = index
        await self.session.flush()

    async def list_users_for_streamer(self, streamer_id: int) -> list[tuple[UserStreamer, UserChannelConfig | None]]:
        stmt = (
            select(UserStreamer, UserChannelConfig)
            .join(UserChannelConfig, UserChannelConfig.user_id == UserStreamer.user_id, isouter=True)
            .where(UserStreamer.streamer_id == streamer_id)
            .order_by(UserStreamer.created_at)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def count_user_streamers(self, user_id: int) -> int:
        stmt = select(func.count(UserStreamer.id)).where(UserStreamer.user_id == user_id)
        return (await self.session.execute(stmt)).scalar_one()

    async def record_delivery(
        self,
        *,
        user_id: int,
        streamer_id: int,
        burst_start: datetime,
        burst_end: datetime,
        clip_external_id: str | None,
        burst_id: int | None = None,
        clip_id: int | None = None,
        extra_payload: str | None = None,
        delivery_channel: str = "web",
    ) -> ClipDelivery:
        delivery = ClipDelivery(
            user_id=user_id,
            streamer_id=streamer_id,
            burst_start=burst_start,
            burst_end=burst_end,
            clip_external_id=clip_external_id,
            burst_id=burst_id,
            clip_id=clip_id,
            extra_payload=extra_payload,
            delivery_channel=delivery_channel,
        )
        self.session.add(delivery)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Delivery already recorded for this window")
        return delivery

    async def recent_deliveries(self, user_id: int, limit: int = 50) -> list[ClipDelivery]:
        stmt = (
            select(ClipDelivery)
            .where(ClipDelivery.user_id == user_id)
            .order_by(ClipDelivery.delivered_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def recent_deliveries_with_streamer(
        self, user_id: int, limit: int = 50
    ) -> list[tuple[ClipDelivery, Streamer]]:
        stmt = (
            select(ClipDelivery, Streamer)
            .join(Streamer, Streamer.id == ClipDelivery.streamer_id)
            .where(ClipDelivery.user_id == user_id)
            .order_by(ClipDelivery.delivered_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def upsert_streamer_status(
        self,
        *,
        user_id: int,
        streamer_id: int,
        status: str,
        last_seen: datetime | None = None,
        last_notified: datetime | None = None,
    ) -> StreamerStatus:
        stmt = (
            select(StreamerStatus)
            .where(StreamerStatus.user_id == user_id)
            .where(StreamerStatus.streamer_id == streamer_id)
        )
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            entity = StreamerStatus(
                user_id=user_id,
                streamer_id=streamer_id,
                status=status,
                last_seen=last_seen,
                last_notified=last_notified,
            )
            self.session.add(entity)
        else:
            entity.status = status
            if last_seen is not None:
                entity.last_seen = last_seen
            if last_notified is not None:
                entity.last_notified = last_notified
        await self.session.flush()
        return entity

    async def list_streamer_status(self, user_id: int) -> list[StreamerStatus]:
        stmt = (
            select(StreamerStatus)
            .where(StreamerStatus.user_id == user_id)
            .order_by(StreamerStatus.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


__all__ = ["UserConfigRepository"]
