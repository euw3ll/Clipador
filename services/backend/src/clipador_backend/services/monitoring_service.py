"""Serviço de monitoramento de clipes - migrado do core/monitor_clientes.py"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal, HistoricoEnvio, StatusStreamer
from clipador_backend.models.clip import Clip
from clipador_backend.models.streamer import Streamer
from clipador_backend.adapters.twitch_api import TwitchAPI

logger = logging.getLogger(__name__)


class MonitoringService:
    """Serviço principal de monitoramento de clipes - migrado do legado"""
    
    def __init__(self, db: Session):
        self.db = db
        self.twitch_api = TwitchAPI()
    
    async def executar_ciclo_monitoramento(self):
        """Executa um ciclo completo de monitoramento para todos os usuários ativos."""
        logger.info("🔄 Iniciando ciclo de monitoramento")
        
        try:
            usuarios_ativos = self.buscar_usuarios_ativos_configurados()
            logger.info(f"Found {len(usuarios_ativos)} usuários ativos para monitorar.")
            
            for usuario in usuarios_ativos:
                try:
                    await self.monitorar_usuario(usuario)
                    # Pequena pausa entre usuários para evitar rate limiting
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Erro ao monitorar usuário {usuario['user_id']}: {e}", exc_info=True)
            
            logger.info("✅ Ciclo de monitoramento concluído")
        except Exception as e:
            logger.error(f"Erro no ciclo de monitoramento: {e}", exc_info=True)
    
    def buscar_usuarios_ativos_configurados(self) -> List[Dict[str, Any]]:
        """Busca todos os usuários ativos com configuração completa."""
        configs = (
            self.db.query(ConfiguracaoCanal)
            .join(UserAccount, UserAccount.id == ConfiguracaoCanal.user_id)
            .filter(
                and_(
                    UserAccount.status == "active",
                    ConfiguracaoCanal.twitch_client_id.is_not(None),
                    ConfiguracaoCanal.streamers_monitorados.is_not(None),
                )
            )
            .all()
        )
        
        result = []
        for config in configs:
            result.append({
                "user_id": config.user_id,
                "twitch_client_id": config.twitch_client_id,
                "twitch_client_secret": config.twitch_client_secret,
                "streamers_monitorados": config.streamers_monitorados,
                "modo_monitoramento": config.modo_monitoramento,
                "slots_ativos": config.slots_ativos,
                "manual_min_clips": config.manual_min_clips,
                "manual_interval_sec": config.manual_interval_sec,
                "modo_parceiro": config.modo_parceiro,
                "clipador_chefe_username": config.clipador_chefe_username,
            })
        
        return result
    
    async def monitorar_usuario(self, usuario_config: Dict[str, Any]):
        """Monitora clipes para um usuário específico."""
        user_id = usuario_config["user_id"]
        streamers = usuario_config["streamers_monitorados"].split(",")
        modo = usuario_config["modo_monitoramento"]
        
        logger.info(f"Monitorando {len(streamers)} streamers para usuário {user_id} (modo: {modo})")
        
        # Configura API da Twitch para este usuário
        await self.twitch_api.configure(
            usuario_config["twitch_client_id"],
            usuario_config["twitch_client_secret"]
        )
        
        for streamer_name in streamers:
            streamer_name = streamer_name.strip()
            if not streamer_name:
                continue
            
            try:
                await self.monitorar_streamer(user_id, streamer_name, usuario_config)
            except Exception as e:
                logger.error(f"Erro ao monitorar streamer {streamer_name}: {e}", exc_info=True)
    
    async def monitorar_streamer(self, user_id: int, streamer_name: str, config: Dict[str, Any]):
        """Monitora clipes de um streamer específico."""
        try:
            # Busca informações do streamer
            streamer_info = await self.twitch_api.get_user_by_login(streamer_name)
            if not streamer_info:
                logger.warning(f"Streamer {streamer_name} não encontrado")
                return
            
            streamer_id = streamer_info['id']
            
            # Atualiza status do streamer
            await self.atualizar_status_streamer(user_id, streamer_id, streamer_info)
            
            # Busca clipes recentes
            clips = await self.twitch_api.get_clips(
                broadcaster_id=streamer_id,
                started_at=datetime.now() - timedelta(hours=24),  # Últimas 24h
                first=20
            )
            
            if not clips:
                logger.debug(f"Nenhum clipe encontrado para {streamer_name}")
                return
            
            # Processa clipes baseado no modo
            if config["modo_monitoramento"] == "AUTOMATICO":
                await self.processar_clipes_automatico(user_id, streamer_id, clips, config)
            else:
                await self.processar_clipes_manual(user_id, streamer_id, clips, config)
            
        except Exception as e:
            logger.error(f"Erro no monitoramento do streamer {streamer_name}: {e}", exc_info=True)
    
    async def atualizar_status_streamer(self, user_id: int, streamer_id: str, streamer_info: Dict):
        """Atualiza o status do streamer (online/offline)."""
        is_live = await self.twitch_api.is_stream_live(streamer_id)
        status = "online" if is_live else "offline"
        
        # Upsert do status
        existing = (
            self.db.query(StatusStreamer)
            .filter(
                and_(
                    StatusStreamer.user_id == user_id,
                    StatusStreamer.streamer_id == streamer_id,
                )
            )
            .first()
        )
        
        if existing:
            existing.status = status
            existing.ultima_verificacao = datetime.now()
        else:
            self.db.add(
                StatusStreamer(
                    user_id=user_id,
                    streamer_id=streamer_id,
                    status=status,
                )
            )
        
        self.db.commit()
    
    async def processar_clipes_automatico(self, user_id: int, streamer_id: str, clips: List[Dict], config: Dict):
        """Processa clipes no modo automático."""
        clips_filtrados = self.filtrar_clipes_duplicados(user_id, clips)
        
        if not clips_filtrados:
            return
        
        # Agrupa clipes por proximidade temporal
        grupos = self.agrupar_clipes_por_proximidade(clips_filtrados)
        
        for grupo in grupos:
            if self.deve_enviar_grupo(user_id, streamer_id, grupo):
                await self.enviar_grupo_clipes(user_id, streamer_id, grupo, config)
    
    async def processar_clipes_manual(self, user_id: int, streamer_id: str, clips: List[Dict], config: Dict):
        """Processa clipes no modo manual."""
        min_clips = config.get("manual_min_clips", 3)
        interval_sec = config.get("manual_interval_sec", 3600)
        
        clips_filtrados = self.filtrar_clipes_duplicados(user_id, clips)
        
        if len(clips_filtrados) < min_clips:
            logger.debug(f"Poucos clipes para modo manual: {len(clips_filtrados)} < {min_clips}")
            return
        
        # Verifica se já passou o intervalo mínimo
        ultimo_envio = self.obter_ultimo_envio(user_id, streamer_id)
        if ultimo_envio:
            tempo_desde_ultimo = (datetime.now() - ultimo_envio).total_seconds()
            if tempo_desde_ultimo < interval_sec:
                logger.debug(f"Ainda em cooldown: {tempo_desde_ultimo}s < {interval_sec}s")
                return
        
        # Agrupa e envia
        grupos = self.agrupar_clipes_por_proximidade(clips_filtrados)
        for grupo in grupos:
            if len(grupo) >= min_clips:
                await self.enviar_grupo_clipes(user_id, streamer_id, grupo, config)
    
    def filtrar_clipes_duplicados(self, user_id: int, clips: List[Dict]) -> List[Dict]:
        """Remove clipes já enviados para o usuário."""
        clips_existentes = {
            clip.external_id for clip in 
            self.db.query(Clip).filter(Clip.user_id == user_id).all()
        }
        
        return [clip for clip in clips if clip['id'] not in clips_existentes]
    
    def agrupar_clipes_por_proximidade(self, clips: List[Dict], janela_minutos: int = 30) -> List[List[Dict]]:
        """Agrupa clipes por proximidade temporal - migrado do legado."""
        if not clips:
            return []
        
        # Ordena clips por data de criação
        clips_ordenados = sorted(clips, key=lambda x: x['created_at'])
        
        grupos = []
        grupo_atual = [clips_ordenados[0]]
        
        for i in range(1, len(clips_ordenados)):
            clip_atual = clips_ordenados[i]
            ultimo_clip = grupo_atual[-1]
            
            # Calcula diferença temporal
            tempo_atual = datetime.fromisoformat(clip_atual['created_at'].replace('Z', '+00:00'))
            tempo_ultimo = datetime.fromisoformat(ultimo_clip['created_at'].replace('Z', '+00:00'))
            diferenca = (tempo_atual - tempo_ultimo).total_seconds() / 60
            
            if diferenca <= janela_minutos:
                grupo_atual.append(clip_atual)
            else:
                grupos.append(grupo_atual)
                grupo_atual = [clip_atual]
        
        if grupo_atual:
            grupos.append(grupo_atual)
        
        return grupos
    
    def deve_enviar_grupo(self, user_id: int, streamer_id: str, grupo: List[Dict]) -> bool:
        """Verifica se um grupo de clipes deve ser enviado."""
        if not grupo:
            return False
        
        # Pega timestamps do primeiro e último clipe
        primeiro_clip = min(grupo, key=lambda x: x['created_at'])
        ultimo_clip = max(grupo, key=lambda x: x['created_at'])
        
        grupo_inicio = datetime.fromisoformat(primeiro_clip['created_at'].replace('Z', '+00:00'))
        grupo_fim = datetime.fromisoformat(ultimo_clip['created_at'].replace('Z', '+00:00'))
        
        # Verifica se já foi enviado um grupo similar
        return not self.verificar_grupo_ja_enviado(user_id, streamer_id, grupo_inicio, grupo_fim)
    
    def verificar_grupo_ja_enviado(self, user_id: int, streamer_id: str, inicio: datetime, fim: datetime) -> bool:
        """Verifica se um grupo similar já foi enviado."""
        exists = (
            self.db.query(HistoricoEnvio)
            .filter(
                and_(
                    HistoricoEnvio.user_id == user_id,
                    HistoricoEnvio.streamer_id == streamer_id,
                    HistoricoEnvio.grupo_inicio <= fim,
                    HistoricoEnvio.grupo_fim >= inicio,
                )
            )
            .first()
        )
        return exists is not None
    
    async def enviar_grupo_clipes(self, user_id: int, streamer_id: str, grupo: List[Dict], config: Dict):
        """Envia um grupo de clipes para o usuário."""
        logger.info(f"Enviando {len(grupo)} clipes para usuário {user_id}")
        
        try:
            # Salva clipes no banco
            for clip_data in grupo:
                clip = Clip(
                    user_id=user_id,
                    external_id=clip_data['id'],
                    title=clip_data['title'],
                    url=clip_data['url'],
                    thumbnail_url=clip_data['thumbnail_url'],
                    broadcaster_name=clip_data['broadcaster_name'],
                    creator_name=clip_data['creator_name'],
                    view_count=clip_data['view_count'],
                    duration=float(clip_data['duration']),
                    created_at_twitch=datetime.fromisoformat(clip_data['created_at'].replace('Z', '+00:00')),
                )
                self.db.add(clip)
            
            # Registra histórico de envio
            primeiro_clip = min(grupo, key=lambda x: x['created_at'])
            ultimo_clip = max(grupo, key=lambda x: x['created_at'])
            
            grupo_inicio = datetime.fromisoformat(primeiro_clip['created_at'].replace('Z', '+00:00'))
            grupo_fim = datetime.fromisoformat(ultimo_clip['created_at'].replace('Z', '+00:00'))
            
            historico = HistoricoEnvio(
                user_id=user_id,
                streamer_id=streamer_id,
                grupo_inicio=grupo_inicio,
                grupo_fim=grupo_fim,
            )
            self.db.add(historico)
            
            self.db.commit()
            
            # TODO: Aqui seria onde o sistema legacy enviaria para o Telegram
            # Na versão web, isso pode ser uma notificação in-app ou email
            logger.info(f"Grupo de {len(grupo)} clipes salvo com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao enviar grupo de clipes: {e}", exc_info=True)
            self.db.rollback()
    
    def obter_ultimo_envio(self, user_id: int, streamer_id: str) -> Optional[datetime]:
        """Obtém a data do último envio para um streamer."""
        ultimo = (
            self.db.query(HistoricoEnvio)
            .filter(
                and_(
                    HistoricoEnvio.user_id == user_id,
                    HistoricoEnvio.streamer_id == streamer_id,
                )
            )
            .order_by(HistoricoEnvio.criado_em.desc())
            .first()
        )
        return ultimo.criado_em if ultimo else None
    
    async def eh_clipe_ao_vivo_real(self, clip_data: Dict) -> bool:
        """Verifica se um clipe é realmente de uma live recente - migrado do legado."""
        try:
            # Verifica se o clipe foi criado recentemente (menos de 2 horas)
            clip_time = datetime.fromisoformat(clip_data['created_at'].replace('Z', '+00:00'))
            tempo_limite = datetime.now() - timedelta(hours=2)
            
            if clip_time < tempo_limite:
                return False
            
            # Verifica se o streamer está realmente ao vivo
            broadcaster_id = clip_data.get('broadcaster_id')
            if broadcaster_id:
                is_live = await self.twitch_api.is_stream_live(broadcaster_id)
                return is_live
            
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar clipe ao vivo: {e}")
            return False