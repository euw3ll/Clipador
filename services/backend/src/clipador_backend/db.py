"""Camada de acesso ao banco usando SQLAlchemy async."""

from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .settings import get_settings

_ENGINE: AsyncEngine | None = None
_SESSION_FACTORY: async_sessionmaker[AsyncSession] | None = None


def _ensure_engine() -> AsyncEngine:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None and _SESSION_FACTORY is not None:
        return _ENGINE

    settings = get_settings()
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    _ENGINE = create_async_engine(database_url, echo=settings.app_env == "development")
    _SESSION_FACTORY = async_sessionmaker(_ENGINE, expire_on_commit=False)
    return _ENGINE


def get_engine() -> AsyncEngine:
    return _ensure_engine()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    _ensure_engine()
    assert _SESSION_FACTORY is not None
    return _SESSION_FACTORY


@asynccontextmanager
async def session_scope():
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
