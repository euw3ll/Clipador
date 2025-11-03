"""Endpoints for managing monitored streamers."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from ...dependencies import get_streamer_repository
from ...repositories.streamers import StreamerRepository

router = APIRouter(prefix="/streams", tags=["streams"])


class StreamerCreate(BaseModel):
    twitch_user_id: str = Field(..., description="Twitch user id")
    display_name: str
    avatar_url: str | None = None
    monitor_interval_seconds: int = 180
    monitor_min_clips: int = 2
    api_mode: str = Field(default="clipador_only", description="clipador_only | clipador_trial | client")
    trial_expires_at: datetime | None = None
    client_twitch_client_id: str | None = None
    client_twitch_client_secret: str | None = None


class StreamerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    twitch_user_id: str
    display_name: str
    avatar_url: str | None
    is_active: bool
    monitor_interval_seconds: int
    monitor_min_clips: int
    api_mode: str
    trial_expires_at: datetime | None
    has_client_credentials: bool

@router.get("", response_model=list[StreamerResponse])
async def list_streamers(repo: StreamerRepository = Depends(get_streamer_repository)) -> list[StreamerResponse]:
    streamers = await repo.list_streamers()
    return [
        StreamerResponse(
            id=streamer.id,
            twitch_user_id=streamer.twitch_user_id,
            display_name=streamer.display_name,
            avatar_url=streamer.avatar_url,
            is_active=streamer.is_active,
            monitor_interval_seconds=streamer.monitor_interval_seconds,
            monitor_min_clips=streamer.monitor_min_clips,
            api_mode=streamer.api_mode,
            trial_expires_at=streamer.trial_expires_at,
            has_client_credentials=bool(
                streamer.client_twitch_client_id and streamer.client_twitch_client_secret
            ),
        )
        for streamer in streamers
    ]


@router.post("", response_model=StreamerResponse, status_code=status.HTTP_201_CREATED)
async def create_streamer(
    payload: StreamerCreate,
    repo: StreamerRepository = Depends(get_streamer_repository),
) -> StreamerResponse:
    existing = await repo.get_by_twitch_id(payload.twitch_user_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Streamer already exists")

    streamer = await repo.create_streamer(
        twitch_user_id=payload.twitch_user_id,
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
        monitor_interval_seconds=payload.monitor_interval_seconds,
        monitor_min_clips=payload.monitor_min_clips,
        api_mode=payload.api_mode,
        trial_expires_at=payload.trial_expires_at,
        client_twitch_client_id=payload.client_twitch_client_id,
        client_twitch_client_secret=payload.client_twitch_client_secret,
    )
    return StreamerResponse(
        id=streamer.id,
        twitch_user_id=streamer.twitch_user_id,
        display_name=streamer.display_name,
        avatar_url=streamer.avatar_url,
        is_active=streamer.is_active,
        monitor_interval_seconds=streamer.monitor_interval_seconds,
        monitor_min_clips=streamer.monitor_min_clips,
        api_mode=streamer.api_mode,
        trial_expires_at=streamer.trial_expires_at,
        has_client_credentials=bool(
            streamer.client_twitch_client_id and streamer.client_twitch_client_secret
        ),
    )


@router.delete("/{streamer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_streamer(
    streamer_id: int,
    repo: StreamerRepository = Depends(get_streamer_repository),
) -> None:
    await repo.delete_streamer(streamer_id)
