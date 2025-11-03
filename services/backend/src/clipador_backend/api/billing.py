"""API de webhook Kirvano end-to-end (idempotência, associação e autoativação)"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import hmac
import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from clipador_backend.dependencies import get_db
from clipador_backend.models.user import UserAccount
from clipador_backend.models.config import ConfiguracaoCanal
from clipador_backend.models.config import Transacao as TransacaoModel
from clipador_backend.services.plan_service import PlanService, PaymentStatus

router = APIRouter(prefix="/billing/kirvano", tags=["billing"])


# Utilitário opcional de assinatura (caso Kirvano envie HMAC)
def _validate_signature(secret: Optional[str], body: bytes, signature: Optional[str]) -> bool:
    if not secret:
        return True
    if not signature:
        return False
    mac = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, signature)


@router.post("/webhook")
async def kirvano_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_kirvano_signature: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Webhook de compras do Kirvano com idempotência por sale_id e autoativação de plano.
    Espera payload com campos: email, plano, metodo_pagamento, status, sale_id, data_criacao, offer_id, nome_completo, telefone.
    """
    raw = await request.body()
    # Se houver segredo em env, validar assinatura (opcional)
    secret = None  # TODO: colocar em settings
    if not _validate_signature(secret, raw, x_kirvano_signature):
        raise HTTPException(status_code=401, detail="Assinatura inválida")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    required = ["email", "plano", "status", "sale_id"]
    for k in required:
        if k not in payload or not payload[k]:
            raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {k}")

    email = payload["email"].strip().lower()
    plano = payload["plano"].strip()
    status_pag = payload["status"].strip()
    sale_id = str(payload["sale_id"]).strip()

    metodo_pagamento = payload.get("metodo_pagamento")
    data_criacao = payload.get("data_criacao")
    offer_id = payload.get("offer_id")
    nome_completo = payload.get("nome_completo")
    telefone = payload.get("telefone")

    # Idempotência: verificar se sale_id já está registrado
    existente = db.query(TransacaoModel).filter(TransacaoModel.sale_id == sale_id).first()
    if existente:
        # Já processado; retornar 200 idempotente
        return {"ok": True, "id": existente.id, "idempotent": True}

    # Criar transação
    trans = TransacaoModel(
        user_id=None,
        email=email,
        plano=plano,
        metodo_pagamento=metodo_pagamento,
        status=status_pag,
        sale_id=sale_id,
        offer_id=offer_id,
        nome_completo=nome_completo,
        telefone=telefone,
        data_criacao_kirvano=data_criacao,
    )
    db.add(trans)
    db.flush()

    # Associar ao usuário pelo e-mail (se existir)
    user = db.query(UserAccount).filter(UserAccount.email == email).first()
    if user:
        trans.user_id = user.id
        db.flush()

    # Autoativação: somente quando status aprovado
    if status_pag.lower() in {PaymentStatus.APROVADO.value, "approved", "pago", "aprovado"}:
        # Se usuário não existe, tentar criar mínimo (opcional). Aqui, apenas associa quando existe.
        if not user:
            # Opcional: criar conta básica
            user = db.query(UserAccount).filter(UserAccount.email == email).first()
        if user:
            plan_service = PlanService(db)
            # Vincula compra e ativa usuário (ajuste de slots conforme plano)
            plan_service.vincular_compra_e_ativar_usuario(
                user_id=user.id,
                email=email,
                plano=plano,
                status=PaymentStatus.APROVADO.value,
            )

    db.commit()

    return {"ok": True, "transacao_id": trans.id, "user_id": trans.user_id}
