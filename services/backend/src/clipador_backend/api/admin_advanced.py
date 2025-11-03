"""Admin API avançada: filtros, estatísticas, broadcast persistente e utilitários"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount, UserRole
from clipador_backend.models.config import ConfiguracaoCanal
from clipador_backend.services.plan_service import PlanService

router = APIRouter(prefix="/admin", tags=["admin"])


# Modelo simples para persistir broadcasts (tabela leve via SQLAlchemy Core)
try:
    from sqlalchemy import Column, Integer, String, DateTime, Text
    from clipador_backend.models.base import Base

    class AdminBroadcast(Base):
        __tablename__ = "admin_broadcasts"
        id = Column(Integer, primary_key=True, autoincrement=True)
        author = Column(String(100), nullable=False)
        segment = Column(String(50), nullable=False)  # "todos|assinantes|teste|ex|sem_plano"
        message = Column(Text, nullable=False)
        created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
except Exception:
    AdminBroadcast = None  # Se migrations não estiverem rodadas ainda


def ensure_admin(user: UserAccount):
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")


@router.get("/users")
async def list_users(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    filtro: str = Query("todos"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(50, ge=1, le=200),
    ordenar: str = Query("id:asc"),
    termo: Optional[str] = None,
    plano: Optional[str] = None,
    telegram_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Lista usuários com filtros avançados (compatível com tokens do legado)."""
    ensure_admin(current_user)

    # Parsing de tokens estilo "plano:<nome>", "q:<termo>", "id:<num>"
    parsed_filtro = (filtro or "").strip()
    if parsed_filtro and ":" in parsed_filtro:
        token, valor = parsed_filtro.split(":", 1)
        token = token.strip().lower()
        valor = valor.strip()
        if token == "plano" and valor:
            plano = valor
            filtro = "plano"
        elif token == "q" and valor:
            termo = valor
            filtro = "q"
        elif token == "id" and valor.isdigit():
            telegram_id = int(valor)
            filtro = "id"

    q = db.query(UserAccount)

    # Filtros principais
    filtro_key = (filtro or "todos").strip().lower()
    now = datetime.now(timezone.utc)
    if filtro_key in ("todos", "", None):
        pass
    elif filtro_key == "teste":
        q = q.filter(or_(UserAccount.plan.ilike("%teste%"), UserAccount.trial_used.is_(True)))
    elif filtro_key == "assinantes":
        q = q.filter(and_(UserAccount.status == "active", or_(UserAccount.plan_expires_at.is_(None), UserAccount.plan_expires_at >= now)))
    elif filtro_key == "ex":
        q = q.filter(or_(UserAccount.status != "active", and_(UserAccount.plan_expires_at.is_not(None), UserAccount.plan_expires_at < now)))
    elif filtro_key == "sem_plano":
        q = q.filter(or_(UserAccount.plan == None, UserAccount.plan == "free"))
    elif filtro_key == "plano":
        # aplicado abaixo via "plano"
        pass
    elif filtro_key == "q":
        pass
    elif filtro_key == "id":
        pass
    else:
        raise HTTPException(status_code=400, detail=f"Filtro inválido: {filtro_key}")

    # Filtros complementares
    if plano:
        q = q.filter(UserAccount.plan.ilike(f"%{plano}%"))
    if termo:
        like_term = f"%{termo}%"
        q = q.filter(or_(UserAccount.username.ilike(like_term), UserAccount.email.ilike(like_term)))
    if telegram_id is not None:
        # Compat: não temos telegram_id em UserAccount; manter como filtro no username/email
        q = q.filter(or_(UserAccount.username == str(telegram_id), UserAccount.email.ilike(f"%{telegram_id}%")))

    # Ordenação
    allowed = {
        "id": UserAccount.id,
        "username": UserAccount.username,
        "email": UserAccount.email,
        "plan": UserAccount.plan,
        "plan_expires_at": UserAccount.plan_expires_at,
        "status": UserAccount.status,
    }
    try:
        campo, direcao = (ordenar or "id:asc").split(":", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Parâmetro 'ordenar' deve estar no formato 'campo:asc|desc'")
    campo = campo.strip().lower()
    direcao = (direcao or "asc").strip().lower()
    if campo not in allowed:
        raise HTTPException(status_code=400, detail=f"Campo de ordenação inválido: {campo}")
    if direcao not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail=f"Direção inválida: {direcao}")

    order_col = allowed[campo]
    q = q.order_by(order_col.asc().nullslast() if direcao == "asc" else order_col.desc().nullslast())

    total = q.count()
    rows = q.offset((pagina - 1) * limite).limit(limite).all()

    itens = []
    for u in rows:
        itens.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "plan": u.plan,
                "plan_expires_at": u.plan_expires_at.isoformat() if u.plan_expires_at else None,
                "status": u.status,
                "trial_used": u.trial_used,
            }
        )

    return {"total": total, "pagina": pagina, "limite": limite, "itens": itens}


@router.get("/stats")
async def obter_estatisticas(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, int]:
    """Estatísticas agregadas equivalentes ao legado."""
    ensure_admin(current_user)

    total_usuarios = db.query(func.count(UserAccount.id)).scalar() or 0
    assinantes_ativos = db.query(func.count(UserAccount.id)).filter(UserAccount.status == "active").scalar() or 0
    canais_monitorados = db.query(func.count(ConfiguracaoCanal.id)).filter(ConfiguracaoCanal.id_canal_telegram.isnot(None)).scalar() or 0

    return {
        "total_usuarios": int(total_usuarios),
        "assinantes_ativos": int(assinantes_ativos),
        "canais_monitorados": int(canais_monitorados),
    }


@router.post("/broadcast")
async def criar_broadcast(
    message: str,
    segment: str = Query("todos", regex="^(todos|assinantes|teste|ex|sem_plano)$"),
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Cria um broadcast persistente para processamento assíncrono por Celery."""
    ensure_admin(current_user)
    if not AdminBroadcast:
        raise HTTPException(status_code=503, detail="Tabela de broadcast indisponível (rodar migrations)")

    obj = AdminBroadcast(author=current_user.username, segment=segment, message=message)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    # TODO: enfileirar task Celery para processar broadcast por segmento

    return {"ok": True, "id": obj.id, "segment": segment}


@router.post("/users/{user_id}/reset-trial-flag")
async def reset_trial_flag(
    user_id: int,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reseta a flag de teste gratuito (compat com resetar_flag_teste_gratuito)."""
    ensure_admin(current_user)
    service = PlanService(db)
    service.resetar_flag_teste_gratuito(user_id)
    return {"ok": True}


@router.post("/users/{user_id}/set-plan-expires")
async def set_plan_expires(
    user_id: int,
    new_expiration_iso: str,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ajusta manualmente a data de expiração do plano (suporte)."""
    ensure_admin(current_user)
    user = db.query(UserAccount).filter(UserAccount.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    try:
        user.plan_expires_at = datetime.fromisoformat(new_expiration_iso)
    except Exception:
        raise HTTPException(status_code=400, detail="Data inválida (usar ISO 8601)")
    db.commit()
    return {"ok": True}


@router.post("/users/{user_id}/set-plan")
async def set_plan(
    user_id: int,
    plan: str,
    keep_extras: bool = True,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Define o plano do usuário e preserva extras (compat conceder_plano_usuario)."""
    ensure_admin(current_user)
    # Reutiliza conceder_plano_usuario com dias=31 quando não houver data explícita
    PlanService(db).conceder_plano_usuario(user_id, plan, dias=31)
    return {"ok": True}
