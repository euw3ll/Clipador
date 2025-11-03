"""API endpoints para o dashboard do usuário"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from clipador_backend.dependencies import get_current_user, get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal, HistoricoEnvio
from clipador_backend.models.clip import Clip
from clipador_backend.models.streamer import Streamer
from clipador_backend.services.plan_service import PlanService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Estatísticas do dashboard do usuário."""
    
    # Total de clipes do usuário
    total_clips = db.query(Clip).filter(
        Clip.user_id == current_user.id
    ).count()
    
    # Clipes desta semana
    week_ago = datetime.now() - timedelta(days=7)
    this_week_clips = db.query(Clip).filter(
        Clip.user_id == current_user.id,
        Clip.created_at >= week_ago
    ).count()
    
    # Streamers ativos (configurados pelo usuário)
    active_streamers = db.query(Streamer).filter(
        Streamer.user_id == current_user.id,
        Streamer.is_active == True
    ).count()
    
    # Dias até expiração
    days_until_expiration = 0
    if current_user.plan_expires_at:
        days_until_expiration = max(0, 
            (current_user.plan_expires_at - datetime.now()).days
        )
    
    # Uso de slots
    plan_service = PlanService(db)
    config = db.query(ConfiguracaoCanal).filter(
        ConfiguracaoCanal.user_id == current_user.id
    ).first()
    
    slots_info = plan_service.calcular_slots_base_e_extras(
        current_user.plan,
        config.slots_ativos if config else None
    )
    
    return {
        "totalClips": total_clips,
        "thisWeekClips": this_week_clips,
        "activeStreamers": active_streamers,
        "daysUntilExpiration": days_until_expiration,
        "slotsUsed": slots_info["total"],
        "slotsTotal": slots_info["total"],
        "slotsBase": slots_info["base"],
        "slotsExtras": slots_info["extras"]
    }


@router.get("/recent-clips")
async def get_recent_clips(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, le=50)
) -> List[Dict[str, Any]]:
    """Clipes recentes do usuário."""
    
    clips = (
        db.query(Clip)
        .filter(Clip.user_id == current_user.id)
        .order_by(Clip.created_at.desc())
        .limit(limit)
        .all()
    )
    
    result = []
    for clip in clips:
        result.append({
            "id": clip.id,
            "title": clip.title,
            "thumbnail": clip.thumbnail_url,
            "streamer": clip.broadcaster_name,
            "creator": clip.creator_name,
            "timeAgo": _calculate_time_ago(clip.created_at),
            "url": clip.url,
            "viewCount": clip.view_count,
            "duration": clip.duration,
            "createdAt": clip.created_at_twitch.isoformat() if clip.created_at_twitch else None
        })
    
    return result


@router.get("/streamers")
async def get_user_streamers(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Streamers configurados pelo usuário."""
    
    # Busca configuração do usuário
    config = db.query(ConfiguracaoCanal).filter(
        ConfiguracaoCanal.user_id == current_user.id
    ).first()
    
    if not config or not config.streamers_monitorados:
        return []
    
    streamers_names = config.streamers_monitorados.split(",")
    result = []
    
    for streamer_name in streamers_names:
        streamer_name = streamer_name.strip()
        if not streamer_name:
            continue
        
        # Busca informações do streamer na tabela de streamers
        streamer = db.query(Streamer).filter(
            Streamer.user_id == current_user.id,
            Streamer.username == streamer_name
        ).first()
        
        # TODO: Buscar status online/offline da tabela StatusStreamer
        is_live = False  # Placeholder
        
        result.append({
            "id": streamer.id if streamer else None,
            "name": streamer_name,
            "displayName": streamer.display_name if streamer else streamer_name.capitalize(),
            "avatar": streamer.profile_image_url if streamer else None,
            "isLive": is_live,
            "mode": config.modo_monitoramento,
            "isActive": streamer.is_active if streamer else True
        })
    
    return result


@router.get("/user-info")
async def get_user_info(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Informações completas do usuário para o dashboard."""
    
    plan_service = PlanService(db)
    config = db.query(ConfiguracaoCanal).filter(
        ConfiguracaoCanal.user_id == current_user.id
    ).first()
    
    slots_info = plan_service.calcular_slots_base_e_extras(
        current_user.plan,
        config.slots_ativos if config else None
    )
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "plan": current_user.plan,
        "planExpiresAt": current_user.plan_expires_at.isoformat() if current_user.plan_expires_at else None,
        "status": current_user.status,
        "trialUsed": current_user.trial_used,
        "slotsUsed": slots_info["total"],
        "slotsTotal": slots_info["total"],
        "slotsBase": slots_info["base"],
        "slotsExtras": slots_info["extras"],
        "isConfigured": config is not None and config.streamers_monitorados is not None,
        "createdAt": current_user.created_at.isoformat(),
        "updatedAt": current_user.updated_at.isoformat()
    }


@router.get("/activity")
async def get_user_activity(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, le=30)
) -> Dict[str, Any]:
    """Atividade do usuário (clipes por dia, etc.)."""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Clipes por dia
    clips_by_day = []
    for i in range(days):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        count = db.query(Clip).filter(
            Clip.user_id == current_user.id,
            Clip.created_at >= day_start,
            Clip.created_at < day_end
        ).count()
        
        clips_by_day.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "clips": count
        })
    
    # Streamers mais ativos
    top_streamers = (
        db.query(
            Clip.broadcaster_name,
            db.func.count(Clip.id).label("clip_count")
        )
        .filter(
            Clip.user_id == current_user.id,
            Clip.created_at >= start_date
        )
        .group_by(Clip.broadcaster_name)
        .order_by(db.func.count(Clip.id).desc())
        .limit(5)
        .all()
    )
    
    return {
        "clipsByDay": clips_by_day,
        "topStreamers": [
            {"name": name, "clipCount": count}
            for name, count in top_streamers
        ],
        "totalClips": sum(day["clips"] for day in clips_by_day)
    }


@router.get("/configuration-status")
async def get_configuration_status(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Status da configuração do usuário."""
    
    config = db.query(ConfiguracaoCanal).filter(
        ConfiguracaoCanal.user_id == current_user.id
    ).first()
    
    if not config:
        return {
            "isConfigured": False,
            "needsOnboarding": True,
            "steps": {
                "twitchApi": False,
                "streamers": False,
                "monitoring": False
            }
        }
    
    has_twitch_api = bool(config.twitch_client_id and config.twitch_client_secret)
    has_streamers = bool(config.streamers_monitorados)
    has_monitoring = bool(config.modo_monitoramento)
    
    is_fully_configured = has_twitch_api and has_streamers and has_monitoring
    
    return {
        "isConfigured": is_fully_configured,
        "needsOnboarding": not is_fully_configured,
        "steps": {
            "twitchApi": has_twitch_api,
            "streamers": has_streamers,
            "monitoring": has_monitoring
        },
        "configuration": {
            "mode": config.modo_monitoramento,
            "streamersCount": len(config.streamers_monitorados.split(",")) if config.streamers_monitorados else 0,
            "slots": config.slots_ativos,
            "partnerMode": config.modo_parceiro,
            "createdAt": config.data_criacao.isoformat()
        } if is_fully_configured else None
    }


def _calculate_time_ago(created_at: datetime) -> str:
    """Calcula tempo desde criação."""
    now = datetime.now(created_at.tzinfo) if created_at.tzinfo else datetime.now()
    delta = now - created_at
    
    if delta.days > 0:
        return f"{delta.days}d atrás"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours}h atrás"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes}m atrás"
    else:
        return "agora"