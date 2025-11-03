"""API pública para canal gratuito (landing dinâmica)"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from clipador_backend.db import get_db_session
from clipador_backend.dependencies import get_db
from clipador_backend.models.clip import Clip
from clipador_backend.models.config import HistoricoEnvioGratuito

router = APIRouter(prefix="/public", tags=["public"]) 


@router.get("/free-channel")
async def listar_canal_gratuito(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    hours: int = Query(24, ge=1, le=168),
) -> Dict[str, Any]:
    """Lista clipes selecionados para o canal gratuito nas últimas N horas."""
    inicio = datetime.now() - timedelta(hours=hours)

    # Buscar histórico do canal gratuito no período
    hist_q = (
        db.query(HistoricoEnvioGratuito)
        .filter(HistoricoEnvioGratuito.grupo_inicio >= inicio)
        .order_by(desc(HistoricoEnvioGratuito.criado_em))
    )
    total = hist_q.count()
    hist = hist_q.offset((page - 1) * per_page).limit(per_page).all()

    items: List[Dict[str, Any]] = []
    for h in hist:
        # Tentar localizar um clipe do streamer na janela do grupo
        clip = (
            db.query(Clip)
            .filter(
                and_(
                    Clip.broadcaster_name == h.streamer_id,
                    Clip.created_at_twitch >= h.grupo_inicio,
                    Clip.created_at_twitch <= h.grupo_fim,
                )
            )
            .order_by(desc(Clip.view_count))
            .first()
        )
        if not clip:
            # Fallback por created_at
            clip = (
                db.query(Clip)
                .filter(
                    and_(
                        Clip.broadcaster_name == h.streamer_id,
                        Clip.created_at >= h.grupo_inicio,
                        Clip.created_at <= h.grupo_fim,
                    )
                )
                .order_by(desc(Clip.view_count))
                .first()
            )
        if clip:
            items.append(
                {
                    "streamer": clip.broadcaster_name,
                    "title": clip.title,
                    "thumbnail": clip.thumbnail_url,
                    "url": clip.url,
                    "views": clip.view_count,
                    "createdAt": (clip.created_at_twitch or clip.created_at).isoformat() if (clip.created_at_twitch or clip.created_at) else None,
                }
            )

    return {"total": total, "page": page, "perPage": per_page, "items": items}
