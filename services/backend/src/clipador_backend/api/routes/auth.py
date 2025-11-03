"""Rotas de autenticação (MVP)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from ...db import session_scope
from ...models import UserAccount, UserRole
from ...security.auth import create_access_token, create_refresh_token, decode_token, verify_password
from ...security.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/login", summary="Autentica usuário e gera token", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    if not payload.username or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciais inválidas")

    async with session_scope() as session:
        result = await session.execute(select(UserAccount).where(UserAccount.username == payload.username))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais incorretas")

    token = create_access_token(payload.username, extra={"role": user.role})
    refresh = create_refresh_token(payload.username)
    return TokenResponse(access_token=token, refresh_token=refresh)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", summary="Troca refresh token por novo access token", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest) -> TokenResponse:
    try:
        data = decode_token(payload.refresh_token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    username = data.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    async with session_scope() as session:
        result = await session.execute(select(UserAccount).where(UserAccount.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(username, extra={"role": user.role})
    refresh = create_refresh_token(username)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", summary="Logout (invalidate refresh token)")
async def logout() -> dict[str, str]:
    # Refresh tokens são stateless; delegar invalidação via blacklist/rotina futura
    return {"status": "ok"}


class MeResponse(BaseModel):
    username: str
    role: str


@router.get("/me", response_model=MeResponse)
async def me(user: UserAccount = Depends(get_current_user)) -> MeResponse:
    return MeResponse(username=user.username, role=user.role)
