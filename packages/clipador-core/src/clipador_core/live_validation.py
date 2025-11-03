"""Rotinas relacionadas à validação de clipes ao vivo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from clipador_adapters import TwitchClient


MAX_CLOCK_DRIFT_SECONDS = 120


async def is_real_live_clip(
    clip: dict,
    *,
    twitch_client: TwitchClient,
    user_id: str,
) -> bool:
    """Verifica se um clipe corresponde a uma transmissão ao vivo em andamento."""

    stream = await twitch_client.get_stream_info(user_id)
    if not stream:
        return False

    agora = datetime.now(timezone.utc)
    clip_created = datetime.fromisoformat(clip["created_at"].replace("Z", "+00:00"))
    stream_start = datetime.fromisoformat(stream["started_at"].replace("Z", "+00:00"))

    max_clock_drift = timedelta(seconds=MAX_CLOCK_DRIFT_SECONDS)
    if clip_created < stream_start - max_clock_drift:
        return False
    if clip_created > agora + max_clock_drift:
        return False

    video_id = clip.get("video_id")
    vod_info = None
    if video_id:
        try:
            vod_info = await twitch_client.get_vod_by_id(str(video_id))
        except Exception:  # pragma: no cover - rede/SDK
            vod_info = None

    if vod_info:
        vod_tipo = (vod_info.get("type") or "").lower()
        if vod_tipo != "archive":
            return False

        vod_start = datetime.fromisoformat(vod_info["created_at"].replace("Z", "+00:00"))
        if vod_start < stream_start - timedelta(minutes=10):
            return False

    return True
