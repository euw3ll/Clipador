"""API de configuração de canal/streamers equivalente ao legado"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal
from clipador_backend.services.plan_service import PlanService

router = APIRouter(prefix="/config", tags=["config"])


class SaveFullConfigDTO(BaseModel):
    twitch_client_id: str
    twitch_client_secret: str
    streamers: List[str] = Field(default_factory=list)
    modo: str = Field(pattern="^(AUTOMATICO|MANUAL)$")
    clipador_chefe: Optional[str] = None
    modo_parceiro: str = Field(default="somente_bot")


class UpdateManualDTO(BaseModel):
    min_clips: Optional[int] = None
    interval_sec: Optional[int] = None
    min_clips_vod: Optional[int] = None


class UpdateStreamersDTO(BaseModel):
    streamers: List[str]


@router.get("/me")
async def buscar_configuracao(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        return {"config": None}

    return {
        "id": cfg.id,
        "twitch_client_id": cfg.twitch_client_id,
        "twitch_client_secret": bool(cfg.twitch_client_secret),
        "link_canal_telegram": cfg.link_canal_telegram,
        "streamers_monitorados": cfg.streamers_monitorados,
        "modo_monitoramento": cfg.modo_monitoramento,
        "slots_ativos": cfg.slots_ativos,
        "data_criacao": cfg.data_criacao.isoformat() if cfg.data_criacao else None,
        "streamers_ultima_modificacao": cfg.streamers_ultima_modificacao.isoformat() if cfg.streamers_ultima_modificacao else None,
        "manual_min_clips": cfg.manual_min_clips,
        "manual_interval_sec": cfg.manual_interval_sec,
        "manual_min_clips_vod": cfg.manual_min_clips_vod,
        "clipador_chefe_username": cfg.clipador_chefe_username,
        "modo_parceiro": cfg.modo_parceiro,
    }


@router.post("/full")
async def salvar_configuracao_canal_completa(
    payload: SaveFullConfigDTO,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = PlanService(db)

    streamers = [s.strip().lower() for s in payload.streamers if s.strip()]
    slots_iniciais = plan.obter_slots_base_plano(current_user.plan)

    if len(streamers) > slots_iniciais:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plano atual permite até {slots_iniciais} streamers. Você informou {len(streamers)}."
        )

    existing = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )

    values = dict(
        twitch_client_id=payload.twitch_client_id,
        twitch_client_secret=payload.twitch_client_secret,
        streamers_monitorados=",".join(streamers) or None,
        modo_monitoramento=payload.modo,
        slots_ativos=slots_iniciais,
        streamers_ultima_modificacao=func.now(),
        clipador_chefe_username=payload.clipador_chefe,
        modo_parceiro=payload.modo_parceiro,
    )

    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
        cfg = existing
    else:
        cfg = ConfiguracaoCanal(user_id=current_user.id, **values)
        db.add(cfg)

    db.commit()

    return {"ok": True, "id": cfg.id}


@router.post("/manual")
async def atualizar_configuracao_manual(
    payload: UpdateManualDTO,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    if payload.min_clips is not None:
        cfg.manual_min_clips = payload.min_clips
    if payload.interval_sec is not None:
        cfg.manual_interval_sec = payload.interval_sec
    if payload.min_clips_vod is not None:
        cfg.manual_min_clips_vod = payload.min_clips_vod

    db.commit()
    return {"ok": True}


@router.post("/modo")
async def atualizar_modo_monitoramento(
    novo_modo: str,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if novo_modo not in {"AUTOMATICO", "MANUAL", "DESATIVADO"}:
        raise HTTPException(status_code=400, detail="Modo inválido")

    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    cfg.modo_monitoramento = novo_modo
    db.commit()
    return {"ok": True}


@router.post("/streamers")
async def atualizar_streamers_monitorados(
    payload: UpdateStreamersDTO,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    plan = PlanService(db)
    slots = plan.obter_slots_base_plano(current_user.plan)

    streamers = [s.strip().lower() for s in payload.streamers if s.strip()]
    if len(streamers) > slots:
        raise HTTPException(status_code=400, detail=f"Plano atual permite até {slots} streamers")

    cfg.streamers_monitorados = ",".join(streamers) or None
    cfg.streamers_ultima_modificacao = func.now()
    db.commit()
    return {"ok": True}


@router.post("/streamers/reset-cooldown")
async def resetar_cooldown_streamers(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    cfg.streamers_ultima_modificacao = None
    db.commit()
    return {"ok": True}


@router.post("/link-canal")
async def salvar_link_canal(
    id_canal: str,
    link_canal: str,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cfg = (
        db.query(ConfiguracaoCanal)
        .filter(ConfiguracaoCanal.user_id == current_user.id)
        .first()
    )
    if not cfg:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    cfg.id_canal_telegram = id_canal
    cfg.link_canal_telegram = link_canal
    db.commit()
    return {"ok": True}

