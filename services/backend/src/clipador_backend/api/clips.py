"""API de clipes do usuário e ajustes do pipeline"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.clip import Clip
from clipador_backend.models.config import HistoricoEnvio, StatusStreamer

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/me")
async def listar_meus_clipes(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    streamer: Optional[str] = None,
    days: int = Query(30, ge=1, le=180),
    order: str = Query("created_at:desc"),
) -> Dict[str, Any]:
    """Lista paginada de clipes recebidos pelo usuário com filtros equivalentes ao legado."""
    q = db.query(Clip).filter(Clip.user_id == current_user.id)

    if streamer:
        q = q.filter(Clip.broadcaster_name.ilike(f"%{streamer}%"))

    if days:
        start = datetime.now() - timedelta(days=days)
        q = q.filter(Clip.created_at >= start)

    campo, _, direcao = (order or "created_at:desc").partition(":")
    col = getattr(Clip, campo, Clip.created_at)
    q = q.order_by(col.asc() if direcao == "asc" else col.desc())

    total = q.count()
    rows = q.offset((page - 1) * per_page).limit(per_page).all()

    itens = []
    for c in rows:
        itens.append({
            "id": c.id,
            "title": c.title,
            "url": c.url,
            "thumbnail": c.thumbnail_url,
            "broadcaster": c.broadcaster_name,
            "creator": c.creator_name,
            "views": c.view_count,
            "duration": c.duration,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
            "createdAtTwitch": c.created_at_twitch.isoformat() if c.created_at_twitch else None,
        })

    return {"total": total, "page": page, "perPage": per_page, "items": itens}


@router.get("/status/streamers")
async def status_streamers(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Retorna o status online/offline dos streamers do usuário (Última verificação)."""
    statuses = (
        db.query(StatusStreamer)
        .filter(StatusStreamer.user_id == current_user.id)
        .order_by(desc(StatusStreamer.ultima_verificacao))
        .all()
    )
    return [
        {
            "streamer_id": s.streamer_id,
            "status": s.status,
            "ultima_verificacao": s.ultima_verificacao.isoformat() if s.ultima_verificacao else None,
        }
        for s in statuses
    ]
