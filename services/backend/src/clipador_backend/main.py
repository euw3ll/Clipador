"""FastAPI application factory for Clipador."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import auth, clips, monitoring, streamers, public, webhooks, config
from .db import get_engine
from .models import Base
from .celery_app import celery_app


def create_app() -> FastAPI:
    app = FastAPI(title="Clipador API", version="0.1.0")

    from .settings import get_settings

    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["support"], summary="Health check")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.on_event("startup")
    async def startup():
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    app.include_router(auth.router)
    app.include_router(clips.router)
    app.include_router(monitoring.router)
    app.include_router(streamers.router)
    app.include_router(public.router)
    app.include_router(webhooks.router)
    app.include_router(config.router)

    @app.get("/health/worker", tags=["support"], summary="Verifica saúde do worker Celery")
    async def worker_health() -> dict[str, object]:
        try:
            response = celery_app.control.ping(timeout=1.0)
            return {"status": "ok", "workers": response}
        except Exception as exc:  # pragma: no cover - fallback para monitoramento
            return {"status": "error", "detail": str(exc)}

    return app


app = create_app()
