"""User-specific channel configuration and delivery tracking."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserChannelConfig(Base):
    __tablename__ = "user_channel_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    channel_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    channel_slug: Mapped[str | None] = mapped_column(String(150), nullable=True, unique=True)
    monitor_mode: Mapped[str] = mapped_column(String(32), default="AUTOMATICO")
    partner_mode: Mapped[str] = mapped_column(String(32), default="somente_bot")
    clipador_chefe_username: Mapped[str | None] = mapped_column(String(80), nullable=True)
    manual_min_clips: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manual_interval_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manual_min_clips_vod: Mapped[int | None] = mapped_column(Integer, nullable=True)
    slots_configured: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_streamers_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notify_online: Mapped[bool] = mapped_column(Boolean, default=True)
    twitch_client_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    twitch_client_secret: Mapped[str | None] = mapped_column(String(160), nullable=True)
    public_share_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    public_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
    )


class UserStreamer(Base):
    __tablename__ = "user_streamers"
    __table_args__ = (
        UniqueConstraint("user_id", "streamer_id", name="uq_user_streamer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    streamer_id: Mapped[int] = mapped_column(ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)


class ClipDelivery(Base):
    __tablename__ = "clip_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "streamer_id",
            "burst_start",
            "burst_end",
            "clip_external_id",
            name="uq_clip_delivery_window",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    streamer_id: Mapped[int] = mapped_column(ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False)
    burst_id: Mapped[int | None] = mapped_column(ForeignKey("bursts.id", ondelete="SET NULL"), nullable=True)
    clip_id: Mapped[int | None] = mapped_column(ForeignKey("clips.id", ondelete="SET NULL"), nullable=True)
    clip_external_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    burst_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    burst_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)
    delivery_channel: Mapped[str] = mapped_column(String(32), default="web")
    extra_payload: Mapped[str | None] = mapped_column(Text, nullable=True)


class StreamerStatus(Base):
    __tablename__ = "streamer_status"
    __table_args__ = (
        UniqueConstraint("user_id", "streamer_id", name="uq_streamer_status_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    streamer_id: Mapped[int] = mapped_column(ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="offline")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_notified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now)


__all__ = [
    "UserChannelConfig",
    "UserStreamer",
    "ClipDelivery",
    "StreamerStatus",
]
