"""Delivery service to fan out bursts to subscribed users."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ClipRecord, Streamer, BurstRecord, UserAccount, UserStreamer
from ..repositories.user_config import UserConfigRepository
from .plan import is_active, resolve_total_slots


class DeliveryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_config_repo = UserConfigRepository(session)

    async def dispatch_burst(
        self,
        streamer: Streamer,
        burst: BurstRecord,
        clips: Iterable[ClipRecord],
    ) -> None:
        clips = list(clips)
        if not clips:
            return

        user_links = await self.user_config_repo.list_users_for_streamer(streamer.id)
        if not user_links:
            return

        user_ids = {link.user_id for link, _ in user_links}
        users_result = await self.session.execute(
            select(UserAccount).where(UserAccount.id.in_(user_ids))
        )
        user_map = {user.id: user for user in users_result.scalars()}
        counts_result = await self.session.execute(
            select(UserStreamer.user_id, func.count(UserStreamer.id))
            .where(UserStreamer.user_id.in_(user_ids))
            .group_by(UserStreamer.user_id)
        )
        user_streamer_counts = {row[0]: row[1] for row in counts_result.all()}

        now = datetime.now(timezone.utc)
        for user_streamer, config in user_links:
            user = user_map.get(user_streamer.user_id)
            if user is None:
                continue
            if not is_active(user, now=now):
                continue

            max_slots = resolve_total_slots(user, config)
            current_total = user_streamer_counts.get(user.id, 0)
            if current_total > max_slots:
                continue

            await self.user_config_repo.upsert_streamer_status(
                user_id=user.id,
                streamer_id=streamer.id,
                status="online",
                last_seen=now,
            )

            for clip in clips:
                payload = json.dumps(
                    {
                        "streamer_display_name": streamer.display_name,
                        "streamer_external_id": streamer.twitch_user_id,
                        "clip_title": clip.title,
                        "viewer_count": clip.viewer_count,
                    },
                    ensure_ascii=False,
                )
                try:
                    await self.user_config_repo.record_delivery(
                        user_id=user.id,
                        streamer_id=streamer.id,
                        burst_start=burst.start_time,
                        burst_end=burst.end_time,
                        clip_external_id=clip.clip_id,
                        burst_id=burst.id,
                        clip_id=clip.id,
                        extra_payload=payload,
                        delivery_channel="web",
                    )
                except ValueError:
                    # entrega já registrada para esse recorte
                    continue


__all__ = ["DeliveryService"]
