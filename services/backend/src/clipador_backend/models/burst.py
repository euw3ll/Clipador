"""Burst models mapping grouped clips."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BurstRecord(Base):
    __tablename__ = "bursts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    streamer_id: Mapped[int] = mapped_column(Integer, ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    clip_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    clips = relationship("BurstClip", back_populates="burst", cascade="all, delete-orphan")


class BurstClip(Base):
    __tablename__ = "burst_clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    burst_id: Mapped[int] = mapped_column(Integer, ForeignKey("bursts.id", ondelete="CASCADE"), nullable=False)
    clip_id: Mapped[int] = mapped_column(Integer, ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    clip_external_id: Mapped[str] = mapped_column(String(64), nullable=False)

    burst = relationship("BurstRecord", back_populates="clips")
    clip = relationship("ClipRecord", back_populates="burst_links")

    __table_args__ = (UniqueConstraint("burst_id", "clip_external_id", name="uq_burst_clip"),)


__all__ = ["BurstRecord", "BurstClip"]
