"""Streamer and monitoring configuration models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Streamer(Base):
    __tablename__ = "streamers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    twitch_user_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    monitor_interval_seconds: Mapped[int] = mapped_column(Integer, default=180)
    monitor_min_clips: Mapped[int] = mapped_column(Integer, default=2)
    api_mode: Mapped[str] = mapped_column(String(32), default="clipador_only")
    trial_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_twitch_client_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    client_twitch_client_secret: Mapped[str | None] = mapped_column(String(256), nullable=True)
    last_clip_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


__all__ = ["Streamer"]
