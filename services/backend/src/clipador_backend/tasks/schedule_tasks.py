"""Tasks Celery para alertas, lembretes e automações recorrentes"""

import logging
from datetime import datetime, timedelta

from celery import shared_task
from sqlalchemy.orm import Session

from clipador_backend.db import get_db_session
from clipador_backend.services.monitoring_service import MonitoringService
from clipador_backend.services.plan_service import PlanService

logger = logging.getLogger(__name__)


@shared_task(name="monitoramento:executar")
def executar_monitoramento_clipes():
    """Executa ciclo de monitoramento para todos os usuários ativos (a cada 15min)."""
    try:
        with get_db_session() as db:
            service = MonitoringService(db)
            import asyncio
            asyncio.run(service.executar_ciclo_monitoramento())
        logger.info("✅ Monitoramento concluído")
    except Exception:
        logger.exception("Falha no monitoramento")
        raise


@shared_task(name="assinaturas:verificar-expiracoes")
def verificar_expiracoes_planos():
    """Envia lembretes de expiração em 7/3/1/0 dias e atualiza ultimo_aviso_expiracao."""
    try:
        with get_db_session() as db:
            plan = PlanService(db)
            usuarios = plan.verificar_expiracao_planos()
            enviados = 0
            for u in usuarios:
                # Placeholder: enviar notificação por e-mail/in-app
                logger.info(
                    "Aviso de expiração: user=%s dias_restantes=%s plano=%s",
                    u["user_id"], u["dias_restantes"], u["plan"],
                )
                enviados += 1
            logger.info("✅ %d avisos de expiração enviados", enviados)
    except Exception:
        logger.exception("Falha ao verificar expirações")
        raise


@shared_task(name="assinaturas:revogar-testes")
def revogar_testes_expirados():
    """Revoga testes gratuitos expirados diariamente."""
    try:
        from clipador_backend.services._plan_helpers import revogar_acesso_teste_expirado_impl
        with get_db_session() as db:
            from clipador_backend.models.user import UserAccount
            now = datetime.now()
            expirados = (
                db.query(UserAccount)
                .filter(
                    UserAccount.plan.ilike("%teste%"),
                    UserAccount.plan_expires_at.isnot(None),
                    UserAccount.plan_expires_at < now,
                    UserAccount.status == "active",
                )
                .all()
            )
            for user in expirados:
                revogar_acesso_teste_expirado_impl(db, user.id)
            logger.info("✅ Testes revogados: %d", len(expirados))
    except Exception:
        logger.exception("Falha ao revogar testes")
        raise


@shared_task(name="sistema:limpeza-diaria")
def limpeza_diaria_dados():
    """Remove históricos muito antigos e dados temporários (diário)."""
    try:
        with get_db_session() as db:
            from clipador_backend.models.config import HistoricoEnvio
            limite = datetime.now() - timedelta(days=90)
            removidos = (
                db.query(HistoricoEnvio)
                .filter(HistoricoEnvio.criado_em < limite)
                .delete()
            )
            db.commit()
            logger.info("✅ Limpeza concluída, removidos: %d", removidos)
    except Exception:
        logger.exception("Falha na limpeza diária")
        raise


@shared_task(name="streamers:atualizar-estatisticas")
def atualizar_estatisticas_streamers():
    """Atualiza estatísticas básicas de streamers (4h)."""
    try:
        with get_db_session() as db:
            from clipador_backend.models.streamer import Streamer
            streamers = db.query(Streamer).filter(Streamer.is_active == True).all()
            for s in streamers:
                s.last_checked = datetime.now()
            db.commit()
            logger.info("✅ Streamers atualizados: %d", len(streamers))
    except Exception:
        logger.exception("Falha ao atualizar estatísticas")
        raise


@shared_task(name="canal-gratuito:processar")
def processar_canal_gratuito():
    """Seleciona clipes populares recentes para o canal gratuito (2h)."""
    try:
        with get_db_session() as db:
            from clipador_backend.models.config import HistoricoEnvioGratuito
            from clipador_backend.models.clip import Clip
            janela = datetime.now() - timedelta(hours=6)
            clipes = (
                db.query(Clip)
                .filter(Clip.created_at >= janela, Clip.view_count > 1000)
                .order_by(Clip.view_count.desc())
                .limit(5)
                .all()
            )
            enviados = 0
            for c in clipes:
                h = HistoricoEnvioGratuito(
                    streamer_id=c.broadcaster_name,
                    grupo_inicio=c.created_at_twitch or c.created_at,
                    grupo_fim=c.created_at_twitch or c.created_at,
                )
                db.add(h)
                enviados += 1
            db.commit()
            logger.info("✅ Canal gratuito processado: %d clipes", enviados)
    except Exception:
        logger.exception("Falha no canal gratuito")
        raise
