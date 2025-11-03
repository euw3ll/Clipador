"""Service responsável por sincronizar clipes com a Twitch."""

from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime, timedelta, timezone

import logging

from clipador_core import BurstConfig, group_clips_by_burst

from ..adapters.twitch import TwitchAPI
from ..db import session_scope
from ..repositories.bursts import BurstRepository
from ..repositories.clips import ClipRepository
from ..repositories.streamers import StreamerRepository
from ..services.delivery import DeliveryService

DEFAULT_LOOKBACK_MINUTES = 60
DEFAULT_SYNC_INTERVAL = 180  # seconds

logger = logging.getLogger(__name__)


class ClipIngestionService:
    def __init__(self, twitch_client: TwitchAPI):
        self._twitch = twitch_client
        self._task: asyncio.Task | None = None
        self._running = False

    async def sync_once(self) -> None:
        async with session_scope() as session:
            streamer_repo = StreamerRepository(session)
            clip_repo = ClipRepository(session)
            burst_repo = BurstRepository(session)
            delivery_service = DeliveryService(session)

            streamers = await streamer_repo.list_active_streamers()
            now = datetime.now(timezone.utc)
            for streamer in streamers:
                since = streamer.last_clip_synced_at or now - timedelta(minutes=DEFAULT_LOOKBACK_MINUTES)
                client_id = None
                client_secret = None
                mode = (streamer.api_mode or "clipador_only").lower()

                if mode == "clipador_only":
                    pass
                elif mode == "clipador_trial":
                    if streamer.trial_expires_at and streamer.trial_expires_at < now:
                        if streamer.client_twitch_client_id and streamer.client_twitch_client_secret:
                            client_id = streamer.client_twitch_client_id
                            client_secret = streamer.client_twitch_client_secret
                        else:
                            # Sem credenciais do cliente após o trial expirar
                            continue
                elif mode == "client":
                    if streamer.client_twitch_client_id and streamer.client_twitch_client_secret:
                        client_id = streamer.client_twitch_client_id
                        client_secret = streamer.client_twitch_client_secret
                    else:
                        continue
                else:
                    # modo desconhecido, pula
                    continue

                logger.info(
                    "ingestion_fetching",
                    extra={
                        "streamer": streamer.twitch_user_id,
                        "mode": mode,
                        "since": since.isoformat(),
                    },
                )

                try:
                    clips_data = await self._twitch.get_clips(
                        streamer.twitch_user_id,
                        since,
                        client_id=client_id,
                        client_secret=client_secret,
                    )
                except RuntimeError as exc:
                    logger.warning(
                        "ingestion_credentials_missing",
                        extra={
                            "streamer": streamer.twitch_user_id,
                            "mode": mode,
                            "error": str(exc),
                        },
                    )
                    continue
                except Exception as exc:
                    logger.exception(
                        "ingestion_fetch_failed",
                        extra={
                            "streamer": streamer.twitch_user_id,
                            "error": str(exc),
                        },
                    )
                    continue

                if not clips_data:
                    await streamer_repo.update_last_synced(streamer)
                    continue

                for clip in clips_data:
                    clip_id = clip.get("id")
                    if not clip_id or await clip_repo.clip_exists(clip_id):
                        continue

                    created_at = datetime.fromisoformat(clip["created_at"].replace("Z", "+00:00"))
                    await clip_repo.create_clip(
                        clip_id=clip_id,
                        streamer_id=streamer.id,
                        streamer_name=clip.get("broadcaster_name", streamer.display_name),
                        streamer_external_id=clip.get("broadcaster_id", streamer.twitch_user_id),
                        created_at=created_at,
                        viewer_count=int(clip.get("view_count", 0)),
                        video_id=clip.get("video_id"),
                        title=clip.get("title"),
                        duration=int(float(clip.get("duration", 0)) or 0),
                        broadcaster_level=None,
                    )

                await streamer_repo.update_last_synced(streamer)

                recent_clips = await clip_repo.list_recent_clips(
                    since_minutes=DEFAULT_LOOKBACK_MINUTES,
                    streamer_id=streamer.twitch_user_id,
                )
                if not recent_clips:
                    continue

                config = BurstConfig(
                    interval_seconds=streamer.monitor_interval_seconds,
                    min_clips=streamer.monitor_min_clips,
                )
                bursts = group_clips_by_burst(recent_clips, config)
                clip_records_map = await clip_repo.get_clips_by_external_ids([clip.id for clip in recent_clips])

                for burst in bursts:
                    clip_db_records = [clip_records_map.get(clip.id) for clip in burst.clips]
                    clip_db_records = [record for record in clip_db_records if record is not None]
                    if not clip_db_records:
                        continue
                    burst_record = await burst_repo.create_from_group(
                        streamer.id,
                        burst,
                        [record.id for record in clip_db_records],
                        [record.clip_id for record in clip_db_records],
                    )
                    await delivery_service.dispatch_burst(streamer, burst_record, clip_db_records)
                    logger.info(
                        "ingestion_burst_created",
                        extra={
                            "streamer": streamer.twitch_user_id,
                            "start": burst.start.isoformat(),
                            "end": burst.end.isoformat(),
                            "count": len(clip_db_records),
                        },
                    )

    async def run_loop(self, interval_seconds: int = DEFAULT_SYNC_INTERVAL) -> None:
        self._running = True
        while self._running:
            try:
                await self.sync_once()
            except Exception:  # pragma: no cover - log futuramente
                pass
            await asyncio.sleep(interval_seconds)

    def start_background(
        self,
        interval_seconds: int = DEFAULT_SYNC_INTERVAL,
    ) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self.run_loop(interval_seconds))

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    async def aclose(self) -> None:
        await self.stop()
        await self._twitch.aclose()
