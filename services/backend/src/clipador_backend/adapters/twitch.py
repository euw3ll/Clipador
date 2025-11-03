"""Cliente assíncrono para a Twitch API."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from clipador_adapters import TwitchClient

from ..settings import get_settings

_BASE_URL = "https://api.twitch.tv/helix"


class TwitchAPI(TwitchClient):
    def __init__(self, *, client: httpx.AsyncClient | None = None):
        self._client = client or httpx.AsyncClient(timeout=15)
        self._settings = get_settings()
        self._tokens: dict[tuple[str, str], tuple[str, float]] = {}

    async def _ensure_token(self, client_id: str | None, client_secret: str | None) -> str:
        cid = client_id or self._settings.twitch_client_id
        secret = client_secret or self._settings.twitch_client_secret
        if not cid or not secret:
            raise RuntimeError("Twitch credentials not configured")

        key = (cid, secret)
        cached = self._tokens.get(key)
        if cached and cached[1] > time.time() + 60:
            return cached[0]

        response = await self._client.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": cid,
                "client_secret": secret,
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        data = response.json()
        token = data["access_token"]
        expiry = time.time() + data.get("expires_in", 3600)
        self._tokens[key] = (token, expiry)
        return token

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> dict[str, Any]:
        token = await self._ensure_token(client_id, client_secret)
        cid = client_id or self._settings.twitch_client_id
        headers = {
            "Client-ID": cid,
            "Authorization": f"Bearer {token}",
        }
        url = f"{_BASE_URL}{path}"
        response = await self._client.request(method, url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_stream_info(self, user_id: str) -> dict[str, Any] | None:
        data = await self._request("GET", "/streams", params={"user_id": user_id})
        return data.get("data", [None])[0]

    async def get_vod_by_id(self, vod_id: str) -> dict[str, Any] | None:
        data = await self._request("GET", "/videos", params={"id": vod_id})
        return data.get("data", [None])[0]

    async def get_clips(
        self,
        broadcaster_id: str,
        started_at: datetime,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {
            "broadcaster_id": broadcaster_id,
            "started_at": started_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "first": 50,
        }
        clips: list[dict[str, Any]] = []
        cursor: str | None = None

        while True:
            if cursor:
                params["after"] = cursor
            data = await self._request("GET", "/clips", params=params, client_id=client_id, client_secret=client_secret)
            page_clips = data.get("data", [])
            clips.extend(page_clips)
            cursor = data.get("pagination", {}).get("cursor")
            if not cursor or not page_clips:
                break

        return clips

    async def aclose(self):  # pragma: no cover - only on shutdown
        await self._client.aclose()
