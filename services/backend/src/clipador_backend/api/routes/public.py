"""Rotas públicas para landing page."""

from fastapi import APIRouter, Depends, Query

from ...dependencies import get_public_clip_repository
from ...repositories.clips import ClipRepository

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/clips")
async def list_public_clips(
    limit: int = Query(12, ge=1, le=50),
    repo: ClipRepository = Depends(get_public_clip_repository),
) -> dict[str, object]:
    clips = await repo.list_public_clips(limit=limit)
    return {"data": clips}
