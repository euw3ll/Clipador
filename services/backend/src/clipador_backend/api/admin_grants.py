"""Endpoints administrativos: concessão de plano e revogação de teste gratuito"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount, UserRole
from clipador_backend.services.plan_service import PlanService

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: UserAccount):
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")


@router.post("/users/{user_id}/revoke-trial")
async def revoke_trial(
    user_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoga o teste gratuito do usuário, desativando configuração e ajustando status/planos."""
    ensure_admin(current_user)
    service = PlanService(db)
    service.revogar_acesso_teste_expirado(user_id)
    return {"ok": True, "message": "Teste gratuito revogado"}


@router.post("/users/{user_id}/grant-plan")
async def grant_plan(
    user_id: int,
    plano: str,
    dias: int = 30,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Concede um plano ao usuário por X dias, preservando slots extras já pagos."""
    ensure_admin(current_user)
    service = PlanService(db)
    service.conceder_plano_usuario(user_id, plano, dias)
    return {"ok": True, "message": f"Plano '{plano}' concedido por {dias} dias"}
