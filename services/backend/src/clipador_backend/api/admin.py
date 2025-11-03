"""Endpoints administrativos para gestão de usuários, slots e broadcast"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount, UserRole
from clipador_backend.services.plan_service import PlanService

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: UserAccount):
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")


@router.get("/users")
async def list_users(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    filtro: str = "todos",
    pagina: int = 1,
    limite: int = 50,
    ordenar: str = "id:asc",
) -> Dict[str, Any]:
    """Lista usuários com filtros básicos, inspirado no legado."""
    ensure_admin(current_user)

    q = db.query(UserAccount)

    if filtro == "assinantes":
        q = q.filter(UserAccount.status == "active")
    elif filtro == "ex":
        q = q.filter(UserAccount.status.in_(["expired", "trial_expired"]))
    elif filtro == "teste":
        q = q.filter(UserAccount.plan.ilike("%teste%"))

    campo, _, direcao = ordenar.partition(":")
    direcao = direcao or "asc"
    col = getattr(UserAccount, campo, UserAccount.id)
    q = q.order_by(col.asc() if direcao == "asc" else col.desc())

    total = q.count()
    items = q.offset((pagina - 1) * limite).limit(limite).all()

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "itens": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "plano": u.plan,
                "expira_em": u.plan_expires_at.isoformat() if u.plan_expires_at else None,
                "status": u.status,
                "trial_used": u.trial_used,
            }
            for u in items
        ],
    }


@router.post("/users/{user_id}/addslot")
async def add_slot(
    user_id: int,
    quantidade: int = 1,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adiciona slots extras para um usuário (equivalente ao /addslot do bot)."""
    ensure_admin(current_user)
    PlanService(db).adicionar_slot_extra(user_id, quantidade)
    return {"ok": True, "message": f"{quantidade} slot(s) adicionados"}


@router.post("/users/{user_id}/removeslots")
async def remove_extra_slots(
    user_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove slots extras mantendo a base do plano."""
    ensure_admin(current_user)
    PlanService(db).remover_slots_extras(user_id)
    return {"ok": True, "message": "Slots extras removidos"}


@router.post("/broadcast")
async def broadcast(
    mensagem: str,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enfileira uma mensagem de broadcast para usuários ativos (placeholder)."""
    ensure_admin(current_user)
    destinatarios = db.query(UserAccount).filter(UserAccount.status == "active").count()
    # TODO: persistir mensagem para processamento por task Celery
    return {"ok": True, "destinatarios": destinatarios, "mensagem": mensagem}
