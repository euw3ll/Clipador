"""Rotas relacionadas a clipes e bursts."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ...dependencies import get_clip_repository
from ...repositories.clips import ClipRepository

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/bursts/recent", summary="Lista bursts detectados recentemente")
async def list_recent_bursts(
    since_minutes: int = Query(60, ge=1, le=240),
    repo: ClipRepository = Depends(get_clip_repository),
) -> dict[str, object]:
    bursts = await repo.recent_bursts(since_minutes=since_minutes)
    return {"data": bursts}
