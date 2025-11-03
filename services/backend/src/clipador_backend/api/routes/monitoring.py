"""Rotas para presets e resolução de parâmetros de monitoramento."""

from fastapi import APIRouter, Depends

from clipador_core import minimo_clipes_por_viewers, resolve_monitoring_parameters

from ...security.dependencies import get_current_user
from ...models import UserAccount

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

_PRESETS = {
    "PADRAO": {
        "intervalo_segundos": 120,
        "min_clipes": 3,
    },
    "RAPIDO": {
        "intervalo_segundos": 60,
        "min_clipes": minimo_clipes_por_viewers,
    },
}


@router.get("/presets", summary="Presets disponíveis")
def list_presets(_user: UserAccount = Depends(get_current_user)) -> dict[str, object]:
    return {"data": _PRESETS}


@router.post("/resolve", summary="Resolve intervalo e mínimo para um modo")
def resolve_monitoring(body: dict[str, object], _user: UserAccount = Depends(get_current_user)) -> dict[str, object]:
    mode = body.get("modo", "PADRAO")
    intervalo, minimo = resolve_monitoring_parameters(
        mode,
        _PRESETS,
        intervalo_manual=body.get("intervalo_manual"),
        minimo_manual=body.get("minimo_manual"),
        fallback_intervalo=body.get("fallback_intervalo", 120),
        fallback_minimo=body.get("fallback_minimo", 3),
    )

    minimo_value = minimo
    if callable(minimo_value):
        minimo_value = minimo_value(body.get("viewers", 0) or 0)

    return {"data": {"intervalo_segundos": intervalo, "min_clipes": minimo_value}}
