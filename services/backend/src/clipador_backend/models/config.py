from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ConfiguracaoCanal(Base):
    """Configuração completa do canal do usuário - migrado do legado"""
    
    __tablename__ = "configuracao_canal"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Configurações da API Twitch
    twitch_client_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    twitch_client_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Canal do Telegram (migração legacy)
    id_canal_telegram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link_canal_telegram: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Streamers e modo de monitoramento
    streamers_monitorados: Mapped[str | None] = mapped_column(Text, nullable=True)  # CSV dos streamers
    modo_monitoramento: Mapped[str] = mapped_column(String(50), default="AUTOMATICO")  # "AUTOMATICO" ou "MANUAL"
    
    # Sistema de slots
    slots_ativos: Mapped[int] = mapped_column(Integer, default=1)
    
    # Configurações do modo manual
    manual_min_clips: Mapped[int] = mapped_column(Integer, default=3)
    manual_interval_sec: Mapped[int] = mapped_column(Integer, default=3600)  # 1 hora
    manual_min_clips_vod: Mapped[int] = mapped_column(Integer, default=5)
    
    # Modo parceiro e clipador chefe
    modo_parceiro: Mapped[str] = mapped_column(String(50), default="somente_bot")
    clipador_chefe_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    data_criacao: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    streamers_ultima_modificacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserAccount", back_populates="configuracao_canal")


class HistoricoEnvio(Base):
    """Histórico de envios de clipes por usuário - migrado do legado"""
    
    __tablename__ = "historico_envio"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    streamer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    clipe_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Para clipador chefe
    
    # Agrupamento de clipes
    grupo_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    grupo_fim: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Timestamp
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("UserAccount")


class HistoricoEnvioGratuito(Base):
    """Histórico de envios do canal gratuito - migrado do legado"""
    
    __tablename__ = "historico_envio_gratuito"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    streamer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Agrupamento de clipes
    grupo_inicio: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    grupo_fim: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Timestamp
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class StatusStreamer(Base):
    """Status atual dos streamers monitorados - migrado do legado"""
    
    __tablename__ = "status_streamer"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    streamer_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # "online", "offline", etc.
    
    # Timestamps
    ultima_verificacao: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("UserAccount")


class NotificacaoConfig(Base):
    """Configurações de notificação do usuário - migrado do legado"""
    
    __tablename__ = "notificacao_config"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    notificar_online: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserAccount")


class Transacao(Base):
    """Registro de transações do Kirvano - migrado e melhorado do legado"""
    
    __tablename__ = "transacoes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dados da compra
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    plano: Mapped[str] = mapped_column(String(255), nullable=False)
    metodo_pagamento: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # IDs do Kirvano
    sale_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    offer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Dados do cliente
    nome_completo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Dados da transação
    data_criacao_kirvano: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Formato original do Kirvano
    valor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserAccount")