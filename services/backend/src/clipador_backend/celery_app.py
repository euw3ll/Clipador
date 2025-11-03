"""Celery application configuration for Clipador."""

from __future__ import annotations

import os

from celery import Celery

REDIS_URL = os.environ.get("CLIPADOR_REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "clipador",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["clipador_backend.tasks.ingestion"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    beat_schedule={
        "sync-clips": {
            "task": "clipador.ingestion.sync",
            "schedule": 180.0,
        }
    },
)
