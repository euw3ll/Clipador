"""Adaptadores para serviços externos (Twitch, storage, IA, etc.)."""

from datetime import datetime
from typing import Any, Protocol


class TwitchClient(Protocol):
    """Contrato assíncrono mínimo para interação com a API da Twitch."""

    async def get_stream_info(self, user_id: str) -> dict[str, Any] | None:  # pragma: no cover - stub
        ...

    async def get_vod_by_id(self, vod_id: str) -> dict[str, Any] | None:  # pragma: no cover - stub
        ...

    async def get_clips(self, broadcaster_id: str, started_at: datetime) -> list[dict[str, Any]]:  # pragma: no cover - stub
        ...


__all__ = ["TwitchClient"]
