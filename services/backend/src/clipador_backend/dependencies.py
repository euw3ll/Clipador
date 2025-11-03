"""Dependências compartilhadas do FastAPI."""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from .db import session_scope
from .repositories.clips import ClipRepository
from .repositories.streamers import StreamerRepository
from .repositories.user_config import UserConfigRepository
from .security.dependencies import get_current_user


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_scope() as session:
        yield session


async def get_clip_repository(
    session: AsyncSession = Depends(get_db_session),
    _user=Depends(get_current_user),  # ensures authentication
) -> ClipRepository:
    return ClipRepository(session)


async def get_streamer_repository(
    session: AsyncSession = Depends(get_db_session),
    _user=Depends(get_current_user),
) -> StreamerRepository:
    return StreamerRepository(session)


async def get_user_config_repository(
    session: AsyncSession = Depends(get_db_session),
    _user=Depends(get_current_user),
) -> UserConfigRepository:
    return UserConfigRepository(session)


async def get_public_clip_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ClipRepository:
    return ClipRepository(session)
