"""Tabela de clipes monitorados."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClipRecord(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    clip_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    streamer_id: Mapped[int] = mapped_column(Integer, ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False)
    streamer_name: Mapped[str] = mapped_column(String(256), nullable=False)
    streamer_external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    viewer_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    video_id: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    broadcaster_level: Mapped[int | None] = mapped_column(Integer)
    burst_links = relationship("BurstClip", back_populates="clip", cascade="all, delete-orphan")

    def to_domain(self) -> dict[str, object]:
        return {
            "id": self.clip_id,
            "streamer_id": self.streamer_id,
            "streamer_external_id": self.streamer_external_id,
            "streamer_name": self.streamer_name,
            "streamer_external_id": self.streamer_external_id,
            "created_at": self.created_at.isoformat(),
            "viewer_count": self.viewer_count,
            "video_id": self.video_id,
            "title": self.title,
            "duration": self.duration,
        }
