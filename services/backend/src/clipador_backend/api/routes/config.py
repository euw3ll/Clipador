"""User channel configuration endpoints."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from ...dependencies import (
    get_streamer_repository,
    get_user_config_repository,
)
from ...models import Streamer, UserAccount
from ...repositories.streamers import StreamerRepository
from ...repositories.user_config import UserConfigRepository
from ...security.dependencies import get_current_user
from ...services.plan import base_slots, remaining_slots, resolve_total_slots

router = APIRouter(prefix="/config", tags=["config"])


class StreamerStatusPayload(BaseModel):
    status: str | None = None
    last_seen: str | None = None
    last_notified: str | None = None


class UserStreamerPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    streamer_id: int
    twitch_user_id: str
    display_name: str
    avatar_url: str | None
    order_index: int
    label: str | None = None
    monitor_interval_seconds: int
    monitor_min_clips: int
    status: StreamerStatusPayload | None = None


class ConfigResponse(BaseModel):
    monitor_mode: str
    partner_mode: str
    clipador_chefe_username: str | None
    manual_min_clips: int | None
    manual_interval_seconds: int | None
    manual_min_clips_vod: int | None
    notify_online: bool
    public_share_enabled: bool
    public_description: str | None
    slots_base: int
    slots_total: int
    slots_used: int
    slots_remaining: int
    streamers: list[UserStreamerPayload]


class ConfigUpdate(BaseModel):
    monitor_mode: str | None = Field(default=None, max_length=32)
    partner_mode: str | None = Field(default=None, max_length=32)
    clipador_chefe_username: str | None = Field(default=None, max_length=80)
    manual_min_clips: int | None = Field(default=None, ge=1, le=20)
    manual_interval_seconds: int | None = Field(default=None, ge=30, le=600)
    manual_min_clips_vod: int | None = Field(default=None, ge=1, le=20)
    notify_online: bool | None = None
    public_share_enabled: bool | None = None
    public_description: str | None = Field(default=None, max_length=2000)
    slots_configured: int | None = Field(default=None, ge=1, le=999)


class StreamerAttach(BaseModel):
    twitch_user_id: str = Field(..., min_length=2, max_length=64)
    display_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=500)
    monitor_interval_seconds: int | None = Field(default=None, ge=30, le=600)
    monitor_min_clips: int | None = Field(default=None, ge=1, le=10)
    api_mode: str | None = Field(default=None, description="clipador_only | clipador_trial | client")
    label: str | None = Field(default=None, max_length=120)


class StreamerReorder(BaseModel):
    streamer_ids: list[int] = Field(..., min_length=1)


class DeliveryRecordPayload(BaseModel):
    clip_external_id: str | None
    delivered_at: str
    streamer_display_name: str
    streamer_twitch_id: str
    viewer_count: int | None = None
    clip_title: str | None = None


class DeliveryHistoryResponse(BaseModel):
    items: list[DeliveryRecordPayload]


def _serialize_status(raw_status) -> StreamerStatusPayload | None:
    if raw_status is None:
        return None
    return StreamerStatusPayload(
        status=raw_status.status,
        last_seen=raw_status.last_seen.isoformat() if raw_status.last_seen else None,
        last_notified=raw_status.last_notified.isoformat() if raw_status.last_notified else None,
    )


async def _config_payload(
    user: UserAccount,
    config_repo: UserConfigRepository,
) -> ConfigResponse:
    config = await config_repo.ensure_config(user.id)
    attachments = await config_repo.list_user_streamers(user.id)
    statuses = await config_repo.list_streamer_status(user.id)
    status_map = {item.streamer_id: item for item in statuses}

    base = base_slots(user.plan)
    total = resolve_total_slots(user, config)
    used = len(attachments)
    remaining = remaining_slots(user, config, used)

    payload_streamers: list[UserStreamerPayload] = []
    for mapping, streamer in attachments:
        status_payload = _serialize_status(status_map.get(streamer.id))
        payload_streamers.append(
            UserStreamerPayload(
                id=mapping.id,
                streamer_id=streamer.id,
                twitch_user_id=streamer.twitch_user_id,
                display_name=streamer.display_name,
                avatar_url=streamer.avatar_url,
                order_index=mapping.order_index,
                label=mapping.label,
                monitor_interval_seconds=streamer.monitor_interval_seconds,
                monitor_min_clips=streamer.monitor_min_clips,
                status=status_payload,
            )
        )

    return ConfigResponse(
        monitor_mode=config.monitor_mode,
        partner_mode=config.partner_mode,
        clipador_chefe_username=config.clipador_chefe_username,
        manual_min_clips=config.manual_min_clips,
        manual_interval_seconds=config.manual_interval_seconds,
        manual_min_clips_vod=config.manual_min_clips_vod,
        notify_online=config.notify_online,
        public_share_enabled=config.public_share_enabled,
        public_description=config.public_description,
        slots_base=base,
        slots_total=total,
        slots_used=used,
        slots_remaining=remaining,
        streamers=sorted(payload_streamers, key=lambda item: (item.order_index, item.display_name.lower())),
    )


@router.get("/me", response_model=ConfigResponse)
async def get_my_config(
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
) -> ConfigResponse:
    return await _config_payload(user, config_repo)


@router.put("/me", response_model=ConfigResponse)
async def update_my_config(
    payload: ConfigUpdate,
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
) -> ConfigResponse:
    data: dict[str, Any] = {}
    for field, value in payload.model_dump(exclude_none=True).items():
        if field == "monitor_mode" and value:
            data[field] = value.upper()
        elif field == "partner_mode" and value:
            data[field] = value.lower()
        else:
            data[field] = value

    if "slots_configured" in data:
        base = base_slots(user.plan)
        if data["slots_configured"] < base:
            data["slots_configured"] = base

    await config_repo.update_config(user.id, **data)
    return await _config_payload(user, config_repo)


async def _ensure_global_streamer(
    payload: StreamerAttach,
    streamer_repo: StreamerRepository,
) -> Streamer:
    existing = await streamer_repo.get_by_twitch_id(payload.twitch_user_id)
    if existing:
        needs_update = False
        if payload.display_name and payload.display_name != existing.display_name:
            existing.display_name = payload.display_name
            needs_update = True
        if payload.avatar_url and payload.avatar_url != existing.avatar_url:
            existing.avatar_url = payload.avatar_url
            needs_update = True
        if payload.monitor_interval_seconds and payload.monitor_interval_seconds != existing.monitor_interval_seconds:
            existing.monitor_interval_seconds = payload.monitor_interval_seconds
            needs_update = True
        if payload.monitor_min_clips and payload.monitor_min_clips != existing.monitor_min_clips:
            existing.monitor_min_clips = payload.monitor_min_clips
            needs_update = True
        if payload.api_mode and payload.api_mode != existing.api_mode:
            existing.api_mode = payload.api_mode
            needs_update = True
        if needs_update:
            await streamer_repo.touch(existing)
        return existing

    return await streamer_repo.create_streamer(
        twitch_user_id=payload.twitch_user_id,
        display_name=payload.display_name or payload.twitch_user_id,
        avatar_url=payload.avatar_url,
        monitor_interval_seconds=payload.monitor_interval_seconds or 180,
        monitor_min_clips=payload.monitor_min_clips or 2,
        api_mode=payload.api_mode or "clipador_only",
        trial_expires_at=None,
        client_twitch_client_id=None,
        client_twitch_client_secret=None,
    )


@router.post("/me/streamers", response_model=ConfigResponse, status_code=status.HTTP_201_CREATED)
async def attach_streamer_to_me(
    payload: StreamerAttach,
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
    streamer_repo: StreamerRepository = Depends(get_streamer_repository),
) -> ConfigResponse:
    config = await config_repo.ensure_config(user.id)
    max_slots = resolve_total_slots(user, config)
    current = await config_repo.count_user_streamers(user.id)
    if current >= max_slots:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Limite de slots atingido para o seu plano.",
        )

    streamer = await _ensure_global_streamer(payload, streamer_repo)
    try:
        await config_repo.attach_streamer(
            user_id=user.id,
            streamer_id=streamer.id,
            label=payload.label,
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Streamer já configurado.")

    return await _config_payload(user, config_repo)


@router.delete("/me/streamers/{streamer_id}", response_model=ConfigResponse)
async def detach_streamer_from_me(
    streamer_id: int,
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
) -> ConfigResponse:
    await config_repo.detach_streamer(user_id=user.id, streamer_id=streamer_id)
    return await _config_payload(user, config_repo)


@router.post("/me/streamers/reorder", response_model=ConfigResponse)
async def reorder_streamers(
    payload: StreamerReorder,
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
) -> ConfigResponse:
    await config_repo.set_streamer_order(user.id, payload.streamer_ids)
    return await _config_payload(user, config_repo)


@router.get("/me/history", response_model=DeliveryHistoryResponse)
async def get_delivery_history(
    limit: int = 50,
    user: UserAccount = Depends(get_current_user),
    config_repo: UserConfigRepository = Depends(get_user_config_repository),
) -> DeliveryHistoryResponse:
    rows = await config_repo.recent_deliveries_with_streamer(user.id, limit=limit)
    items: list[DeliveryRecordPayload] = []
    for delivery, streamer in rows:
        extra = {}
        if delivery.extra_payload:
            try:
                extra = json.loads(delivery.extra_payload)
            except json.JSONDecodeError:
                extra = {}
        items.append(
            DeliveryRecordPayload(
                clip_external_id=delivery.clip_external_id,
                delivered_at=delivery.delivered_at.isoformat(),
                streamer_display_name=streamer.display_name,
                streamer_twitch_id=streamer.twitch_user_id,
                viewer_count=extra.get("viewer_count"),
                clip_title=extra.get("clip_title"),
            )
        )
    return DeliveryHistoryResponse(items=items)
