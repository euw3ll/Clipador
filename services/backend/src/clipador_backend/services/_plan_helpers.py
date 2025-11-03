from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal

# Extensões ao PlanService: revogar_acesso_teste_expirado e utilitários

def revogar_acesso_teste_expirado_impl(db: Session, user_id: int):
    """Revoga o teste gratuito, desativando configuração e ajustando status/plano."""
    user = db.query(UserAccount).filter(UserAccount.id == user_id).first()
    if not user:
        raise ValueError("Usuário não encontrado")

    # Desativar configuração do canal (sem excluir dados)
    config = db.query(ConfiguracaoCanal).filter(ConfiguracaoCanal.user_id == user_id).first()
    if config:
        config.modo_monitoramento = "DESATIVADO"

    # Resetar dados de plano
    user.plan = "free"
    user.status = "trial_expired"
    user.plan_expires_at = None

    db.commit()

