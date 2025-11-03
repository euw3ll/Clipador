"""API extra: download configurável e exportação de clipes"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.clip import Clip
from clipador_backend.settings import settings

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/{clip_id}/download")
async def baixar_clipe(
    clip_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Resolve URL de download conforme preferência: domínio próprio/Clipr ou URL original."""
    clip = db.query(Clip).filter(and_(Clip.id == clip_id, Clip.user_id == current_user.id)).first()
    if not clip:
        raise HTTPException(status_code=404, detail="Clipe não encontrado")

    base = (getattr(settings, "DOWNLOAD_BASE_URL", None) or "").rstrip("/")
    if base:
        # Monta URL via domínio próprio/Clipr
        # Exemplo: https://clipr.seu-dominio/clip/{external_id}
        external_id = getattr(clip, "external_id", None)
        if external_id:
            return {"url": f"{base}/clip/{external_id}"}

    # Fallback para URL original
    return {"url": clip.url}


@router.get("/export")
async def exportar_clipes(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    fmt: str = Query("csv", regex="^(csv|json)$"),
    days: int = Query(30, ge=1, le=365),
    streamer: Optional[str] = None,
) -> Response:
    """Exporta clipes em CSV/JSON por período e streamer."""
    q = db.query(Clip).filter(Clip.user_id == current_user.id)

    if streamer:
        q = q.filter(Clip.broadcaster_name.ilike(f"%{streamer}%"))

    inicio = datetime.now() - timedelta(days=days)
    q = q.filter(Clip.created_at >= inicio).order_by(desc(Clip.created_at))

    rows = q.all()

    if fmt == "json":
        data = [
            {
                "id": c.id,
                "external_id": getattr(c, "external_id", None),
                "title": c.title,
                "url": c.url,
                "thumbnail": c.thumbnail_url,
                "broadcaster": c.broadcaster_name,
                "creator": c.creator_name,
                "views": c.view_count,
                "duration": c.duration,
                "createdAt": c.created_at.isoformat() if c.created_at else None,
                "createdAtTwitch": c.created_at_twitch.isoformat() if c.created_at_twitch else None,
            }
            for c in rows
        ]
        from fastapi.responses import JSONResponse
        return JSONResponse(content=data)

    # CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id", "external_id", "title", "url", "thumbnail", "broadcaster",
        "creator", "views", "duration", "createdAt", "createdAtTwitch",
    ])
    for c in rows:
        writer.writerow([
            c.id,
            getattr(c, "external_id", None),
            c.title,
            c.url,
            c.thumbnail_url,
            c.broadcaster_name,
            c.creator_name,
            c.view_count,
            c.duration,
            c.created_at.isoformat() if c.created_at else None,
            c.created_at_twitch.isoformat() if c.created_at_twitch else None,
        ])

    content = output.getvalue()
    output.close()
    from fastapi.responses import Response as FastResponse
    return FastResponse(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clipes.csv"},
    )
