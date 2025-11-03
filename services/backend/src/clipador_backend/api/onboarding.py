"""API de onboarding para configuração inicial do usuário"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.streamer import Streamer
from clipador_backend.models.config import ConfiguracaoCanal
from clipador_backend.services.plan_service import PlanService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingData(BaseModel):
    """Dados do onboarding do usuário"""
    twitch_client_id: str = Field(..., min_length=1)
    twitch_client_secret: str = Field(..., min_length=1)
    streamers: List[str] = Field(..., min_items=1)
    mode: str = Field(..., regex="^(AUTOMATICO|MANUAL)$")
    channel_name: Optional[str] = Field(None)
    partner_mode: str = Field(default="somente_bot")


class StreamerValidationResponse(BaseModel):
    """Resposta da validação de streamers"""
    username: str
    display_name: str
    is_valid: bool
    profile_image_url: Optional[str] = None
    follower_count: Optional[int] = None
    error_message: Optional[str] = None


@router.post("/validate-streamers")
async def validate_streamers(
    streamers: List[str],
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[StreamerValidationResponse]:
    """Validar se os streamers existem na Twitch."""
    try:
        # TODO: Implementar validação com API da Twitch
        results = []
        
        for username in streamers:
            # Por enquanto, assumimos que todos são válidos
            # Na implementação real, fazer chamada para API da Twitch
            results.append(StreamerValidationResponse(
                username=username.lower(),
                display_name=username.capitalize(),
                is_valid=True,
                profile_image_url=f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{username.lower()}-300x300.jpg",
                follower_count=1000  # Placeholder
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Erro ao validar streamers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/complete")
async def complete_onboarding(
    data: OnboardingData,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Finalizar configuração inicial do usuário."""
    try:
        plan_service = PlanService(db)
        
        # Verificar se o usuário tem slots suficientes
        slots_base = plan_service.obter_slots_base_plano(current_user.plan)
        if len(data.streamers) > slots_base:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Você pode adicionar no máximo {slots_base} streamers com seu plano atual"
            )
        
        # Criar ou atualizar configuração do canal
        existing_config = db.query(ConfiguracaoCanal).filter(
            ConfiguracaoCanal.user_id == current_user.id
        ).first()
        
        if existing_config:
            # Atualizar configuração existente
            existing_config.twitch_client_id = data.twitch_client_id
            existing_config.twitch_client_secret = data.twitch_client_secret
            existing_config.streamers_monitorados = ",".join(data.streamers)
            existing_config.modo_monitoramento = data.mode
            existing_config.modo_parceiro = data.partner_mode
            existing_config.slots_ativos = slots_base
            config = existing_config
        else:
            # Criar nova configuração
            config = ConfiguracaoCanal(
                user_id=current_user.id,
                twitch_client_id=data.twitch_client_id,
                twitch_client_secret=data.twitch_client_secret,
                streamers_monitorados=",".join(data.streamers),
                modo_monitoramento=data.mode,
                modo_parceiro=data.partner_mode,
                slots_ativos=slots_base
            )
            db.add(config)
        
        # Criar registros de streamers
        added_streamers = []
        for username in data.streamers:
            username = username.strip().lower()
            if not username:
                continue
            
            # Verificar se já existe
            existing = db.query(Streamer).filter(
                Streamer.user_id == current_user.id,
                Streamer.username == username
            ).first()
            
            if existing:
                existing.is_active = True
                added_streamers.append({
                    "id": existing.id,
                    "username": existing.username,
                    "display_name": existing.display_name
                })
            else:
                # Criar novo streamer
                new_streamer = Streamer(
                    user_id=current_user.id,
                    username=username,
                    display_name=username.capitalize(),
                    twitch_user_id=f"fake_{username}",  # TODO: Obter ID real da Twitch
                    is_active=True
                )
                
                db.add(new_streamer)
                db.flush()  # Para obter o ID
                
                added_streamers.append({
                    "id": new_streamer.id,
                    "username": new_streamer.username,
                    "display_name": new_streamer.display_name
                })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Configuração inicial concluída com sucesso!",
            "addedStreamers": added_streamers,
            "totalAdded": len(added_streamers),
            "mode": data.mode,
            "channelName": data.channel_name or "Meu Canal"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao completar onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/status")
async def get_onboarding_status(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Status do onboarding do usuário."""
    try:
        # Verificar se tem configuração
        config = db.query(ConfiguracaoCanal).filter(
            ConfiguracaoCanal.user_id == current_user.id
        ).first()
        
        # Verificar se tem streamers configurados
        streamers_count = db.query(Streamer).filter(
            Streamer.user_id == current_user.id,
            Streamer.is_active == True
        ).count()
        
        has_twitch_config = bool(
            config and config.twitch_client_id and config.twitch_client_secret
        )
        has_streamers = streamers_count > 0
        has_monitoring_mode = bool(config and config.modo_monitoramento)
        
        is_completed = has_twitch_config and has_streamers and has_monitoring_mode
        
        return {
            "completed": is_completed,
            "hasConfig": config is not None,
            "hasTwitchConfig": has_twitch_config,
            "hasStreamers": has_streamers,
            "streamersCount": streamers_count,
            "hasMonitoringMode": has_monitoring_mode,
            "needsSetup": not is_completed,
            "steps": {
                "twitchApi": has_twitch_config,
                "streamers": has_streamers,
                "monitoring": has_monitoring_mode
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status do onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/progress")
async def get_onboarding_progress(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Progresso detalhado do onboarding."""
    try:
        config = db.query(ConfiguracaoCanal).filter(
            ConfiguracaoCanal.user_id == current_user.id
        ).first()
        
        if not config:
            return {
                "currentStep": 1,
                "totalSteps": 4,
                "progress": 0,
                "completedSteps": []
            }
        
        completed_steps = []
        current_step = 1
        
        # Passo 1: API da Twitch
        if config.twitch_client_id and config.twitch_client_secret:
            completed_steps.append(1)
            current_step = 2
        
        # Passo 2: Streamers
        if config.streamers_monitorados:
            completed_steps.append(2)
            current_step = 3
        
        # Passo 3: Modo de monitoramento
        if config.modo_monitoramento:
            completed_steps.append(3)
            current_step = 4
        
        # Passo 4: Finalização
        if len(completed_steps) >= 3:
            completed_steps.append(4)
            current_step = 4
        
        progress = (len(completed_steps) / 4) * 100
        
        return {
            "currentStep": current_step,
            "totalSteps": 4,
            "progress": int(progress),
            "completedSteps": completed_steps,
            "isComplete": len(completed_steps) >= 4
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter progresso do onboarding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )