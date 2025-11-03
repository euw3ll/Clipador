"""Endpoints adicionais de histórico e notificações do pipeline"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import HistoricoEnvio, StatusStreamer

router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/history")
async def historico_envios(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    streamer_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
) -> Dict[str, Any]:
    """Retorna grupos de envios (HistoricoEnvio) por período/streamer."""
    q = db.query(HistoricoEnvio).filter(HistoricoEnvio.user_id == current_user.id)

    if streamer_id:
        q = q.filter(HistoricoEnvio.streamer_id == streamer_id)

    if days:
        start = datetime.now() - timedelta(days=days)
        q = q.filter(HistoricoEnvio.criado_em >= start)

    total = q.count()
    rows = q.order_by(desc(HistoricoEnvio.criado_em)).offset((page - 1) * per_page).limit(per_page).all()

    items = []
    for h in rows:
        items.append({
            "id": h.id,
            "streamer_id": h.streamer_id,
            "grupo_inicio": h.grupo_inicio.isoformat() if h.grupo_inicio else None,
            "grupo_fim": h.grupo_fim.isoformat() if h.grupo_fim else None,
            "criado_em": h.criado_em.isoformat() if h.criado_em else None,
            "clipe_id": getattr(h, "clipe_id", None),
        })

    return {"total": total, "page": page, "perPage": per_page, "items": items}


@router.get("/online-notifications")
async def listar_online_notifications(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """Lista últimas mudanças de status de streamers (online/offline)."""
    statuses = (
        db.query(StatusStreamer)
        .filter(StatusStreamer.user_id == current_user.id)
        .order_by(desc(StatusStreamer.ultima_verificacao))
        .limit(limit)
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
