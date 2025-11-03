"""Serviços de gerenciamento de planos - migrado do legado"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select, update

from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal, Transacao


class PlanName(str, Enum):
    """Nomes dos planos disponíveis"""
    MENSAL_SOLO = "Mensal Solo"
    MENSAL_PLUS = "Mensal Plus"
    ANUAL_PRO = "Anual Pro"
    PARCEIRO = "Parceiro"
    TESTE_GRATUITO = "Teste Gratuito"
    SUPER = "Super"


class PaymentStatus(str, Enum):
    """Status de pagamento"""
    APROVADO = "approved"
    PENDENTE = "pending"
    CANCELADO = "cancelled"
    EXPIRADO = "expired"
    TRIAL_EXPIRED = "trial_expired"
    APROVADO_ADMIN = "approved_admin"


class PlanService:
    """Serviço de gerenciamento de planos e slots"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obter_slots_base_plano(self, plano: Optional[str]) -> int:
        """Retorna a franquia de slots do plano, aceitando variações de escrita."""
        if plano is None:
            return 1
        
        # Normaliza para string
        name = plano.value if isinstance(plano, PlanName) else str(plano)
        
        # Normalização simples de acentos/espacos/caixa
        s = name.strip().lower()
        # Remoção leve de acentos comuns
        for a, b in [
            ("á", "a"), ("à", "a"), ("â", "a"), ("ã", "a"),
            ("é", "e"), ("ê", "e"), ("í", "i"),
            ("ó", "o"), ("ô", "o"), ("õ", "o"),
            ("ú", "u"), ("ç", "c"),
        ]:
            s = s.replace(a, b)
        
        if s == "mensal solo" or "mensal solo" in s:
            return 3
        if s == "mensal plus" or "mensal plus" in s:
            return 8
        if s == "anual pro" or "anual pro" in s:
            return 15
        if s == "parceiro" or "parceiro" in s:
            return 1
        # Teste gratuito se comporta como Mensal Solo (3 slots)
        if s == "teste gratuito" or "teste" in s or "gratis" in s or "gratuito" in s:
            return 3
        if s == "super" or "super" in s:
            return 999
        return 1
    
    def calcular_slots_base_e_extras(
        self, plano: Optional[str], slots_configurados: Optional[int]
    ) -> Dict[str, int]:
        """Calcula slots base/extras/total de forma consistente."""
        base = self.obter_slots_base_plano(plano)
        total = slots_configurados if (slots_configurados or 0) > 0 else base
        if total < base:
            total = base
        extras = max(0, total - base)
        return {"base": base, "extras": extras, "total": total}
    
    def usuario_ja_usou_teste(self, user_id: int) -> bool:
        """Verifica se o usuário já utilizou o teste gratuito."""
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        return bool(user.trial_used) if user else False
    
    def vincular_compra_e_ativar_usuario(
        self, user_id: int, email: str, plano: str, status: str
    ):
        """Vincula compra aprovada ao usuário e ativa o plano."""
        TESTE_GRATUITO_DURACAO_DIAS = 7  # Configurável
        
        is_trial_plan = any(
            keyword in plano.lower() for keyword in ["gratuito", "grátis", "teste"]
        )
        
        if is_trial_plan and self.usuario_ja_usou_teste(user_id):
            raise ValueError("Você já utilizou o período de teste gratuito.")
        
        # Captura plano antigo e config atual (se existir) antes da mudança
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user:
            raise ValueError("Usuário não encontrado")
        
        plano_antigo = user.plan
        config_atual = (
            self.db.query(ConfiguracaoCanal)
            .filter(ConfiguracaoCanal.user_id == user_id)
            .first()
        )
        
        # Vincula transações aprovadas pendentes ao usuário
        self.db.execute(
            update(Transacao)
            .where(
                and_(
                    func.lower(Transacao.email) == email.strip().lower(),
                    Transacao.status == PaymentStatus.APROVADO.value,
                    Transacao.user_id.is_(None),
                )
            )
            .values(user_id=user_id)
        )
        
        # Atualiza email do usuário
        user.email = email
        
        # Calcula data de expiração
        if "Anual" in plano:
            data_expiracao = datetime.now() + timedelta(days=365)
        elif is_trial_plan:
            data_expiracao = datetime.now() + timedelta(days=TESTE_GRATUITO_DURACAO_DIAS)
        else:
            data_expiracao = datetime.now() + timedelta(days=31)
        
        # Atualiza dados do usuário
        user.plan = plano
        user.plan_expires_at = data_expiracao
        user.status = "active"
        
        if is_trial_plan:
            user.trial_used = True
        
        # Ajusta a franquia de slots conforme o novo plano, preservando extras já pagos
        if config_atual:
            slots_atuais = config_atual.slots_ativos or 1
            base_antigo = self.obter_slots_base_plano(plano_antigo)
            extras = max(0, slots_atuais - base_antigo)
            base_novo = self.obter_slots_base_plano(plano)
            novos_slots = base_novo + extras
            config_atual.slots_ativos = novos_slots
        
        self.db.commit()
    
    def adicionar_slot_extra(self, user_id: int, quantidade: int = 1):
        """Adiciona slots extras ao usuário."""
        config = (
            self.db.query(ConfiguracaoCanal)
            .filter(ConfiguracaoCanal.user_id == user_id)
            .first()
        )
        if config:
            config.slots_ativos = (config.slots_ativos or 1) + quantidade
            self.db.commit()
    
    def remover_slots_extras(self, user_id: int):
        """Remove slots extras, mantendo apenas os do plano base."""
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user:
            raise ValueError("Usuário não encontrado")
        
        config = (
            self.db.query(ConfiguracaoCanal)
            .filter(ConfiguracaoCanal.user_id == user_id)
            .first()
        )
        if not config:
            raise ValueError("Usuário não possui um canal configurado para remover slots.")
        
        slots_base = self.obter_slots_base_plano(user.plan)
        config.slots_ativos = slots_base
        self.db.commit()
    
    def conceder_plano_usuario(self, user_id: int, plano: str, dias: int):
        """Concede plano administrativamente."""
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user:
            raise ValueError("Usuário não encontrado")
        
        plano_antigo = user.plan
        data_expiracao = datetime.now() + timedelta(days=dias)
        
        user.plan = plano
        user.plan_expires_at = data_expiracao
        user.status = "active"
        
        # Ajusta slots preservando extras
        config = (
            self.db.query(ConfiguracaoCanal)
            .filter(ConfiguracaoCanal.user_id == user_id)
            .first()
        )
        if config:
            slots_atuais = config.slots_ativos or 1
            slots_base_antigo = self.obter_slots_base_plano(plano_antigo)
            slots_extras = max(0, slots_atuais - slots_base_antigo)
            novos_slots = self.obter_slots_base_plano(plano) + slots_extras
            config.slots_ativos = novos_slots
        
        self.db.commit()
    
    def resetar_flag_teste_gratuito(self, user_id: int):
        """Reseta a flag de teste gratuito usado."""
        user = self.db.query(UserAccount).filter(UserAccount.id == user_id).first()
        if not user:
            raise ValueError(f"Usuário com ID {user_id} não encontrado.")
        
        user.trial_used = False
        self.db.commit()
    
    def verificar_expiracao_planos(self) -> list:
        """Retorna usuários com planos próximos do vencimento."""
        dias_alerta = [7, 3, 1, 0]  # Avisos em 7, 3, 1 dias e no vencimento
        usuarios_para_notificar = []
        
        for dias in dias_alerta:
            data_limite = datetime.now() + timedelta(days=dias)
            
            users = (
                self.db.query(UserAccount)
                .filter(
                    and_(
                        UserAccount.status == "active",
                        UserAccount.plan_expires_at <= data_limite,
                        UserAccount.plan_expires_at > datetime.now(),
                    )
                )
                .all()
            )
            
            for user in users:
                dias_restantes = (user.plan_expires_at - datetime.now()).days
                usuarios_para_notificar.append({
                    "user_id": user.id,
                    "email": user.email,
                    "plan": user.plan,
                    "dias_restantes": dias_restantes,
                })
        
        return usuarios_para_notificar