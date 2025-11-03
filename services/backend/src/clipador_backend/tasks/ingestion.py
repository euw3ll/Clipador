"""Celery task definitions for ingestion."""

from __future__ import annotations

import asyncio
import logging

from ..celery_app import celery_app
from ..adapters.twitch import TwitchAPI
from ..services.ingestion import ClipIngestionService

logger = logging.getLogger(__name__)


@celery_app.task(name="clipador.ingestion.sync")
def run_ingestion_task() -> None:
    """Task executed periodicamente pelo Celery Beat para sincronizar clipes."""

    async def _run() -> None:
        service = ClipIngestionService(TwitchAPI())
        try:
            await service.sync_once()
        finally:
            await service.aclose()

    try:
        asyncio.run(_run())
        logger.info("ingestion_task_completed", extra={"task": "clipador.ingestion.sync"})
    except Exception as exc:  # pragma: no cover - logged for monitoring
        logger.exception("ingestion_task_failed", extra={"error": str(exc)})
        raise
