"""Rotinas de monitoramento e agrupamento de clipes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable, Mapping, Tuple, Union

MinClipsStrategy = Union[int, Callable[[int], int]]


def _datetime_to_iso(dt: datetime) -> str:
    """Converte datetime UTC para string ISO com sufixo Z."""

    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@dataclass(slots=True)
class Clip:
    """Representa um clipe coletado de plataformas externas."""

    id: str
    created_at: datetime
    viewer_count: int = 0
    video_id: str | None = None
    streamer_name: str | None = None
    streamer_external_id: str | None = None

    @classmethod
    def from_iso(cls, clip_id: str, created_at_iso: str, **kwargs) -> "Clip":
        """Cria um clipe a partir de um timestamp ISO8601 (sufixo `Z` suportado)."""

        return cls(
            id=clip_id,
            created_at=datetime.fromisoformat(created_at_iso.replace("Z", "+00:00")),
            **kwargs,
        )


@dataclass(slots=True)
class ClipGroup:
    """Agrupamento (burst) de clipes em um intervalo de tempo."""

    clips: list[Clip]
    start: datetime
    end: datetime

    def to_payload(self) -> dict[str, object]:
        """Serializa o agrupamento em formato compatível com o legado."""

        start_iso = _datetime_to_iso(self.start)
        end_iso = _datetime_to_iso(self.end)

        return {
            "inicio": start_iso,
            "inicio_iso": start_iso,
            "fim": end_iso,
            "clipes": [
                {
                    "id": clip.id,
                    "created_at": _datetime_to_iso(clip.created_at),
                    "viewer_count": clip.viewer_count,
                    "video_id": clip.video_id,
                    "streamer_name": clip.streamer_name,
                    "streamer_external_id": clip.streamer_external_id,
                }
            for clip in self.clips
        ],
        }


@dataclass(slots=True)
class BurstConfig:
    """Configuração para agrupamento de clipes."""

    interval_seconds: int
    min_clips: MinClipsStrategy

    def threshold_for(self, viewers: int) -> int:
        value = self.min_clips
        return value(viewers) if callable(value) else value


def group_clips_by_burst(clips: Iterable[Clip], config: BurstConfig) -> list[ClipGroup]:
    """Agrupa clipes pela proximidade temporal, respeitando o limiar configurado."""

    sorted_clips = sorted(clips, key=lambda clip: clip.created_at)
    if not sorted_clips:
        return []

    groups: list[ClipGroup] = []
    usados: set[str] = set()

    for index, base_clip in enumerate(sorted_clips):
        if base_clip.id in usados:
            continue

        grupo = [base_clip]
        usados_temp = {base_clip.id}
        base_time = base_clip.created_at

        for outro_clip in sorted_clips[index + 1 :]:
            if outro_clip.id in usados or outro_clip.id in usados_temp:
                continue

            delta = (outro_clip.created_at - base_time).total_seconds()
            if delta <= config.interval_seconds:
                grupo.append(outro_clip)
                usados_temp.add(outro_clip.id)
            else:
                break

        threshold = config.threshold_for(base_clip.viewer_count)
        if len(grupo) >= threshold:
            groups.append(
                ClipGroup(
                    clips=list(grupo),
                    start=grupo[0].created_at,
                    end=grupo[-1].created_at,
                )
            )
            usados.update(usados_temp)

    return groups


def get_time_minutes_ago(minutes: int = 5) -> str:
    """Retorna um timestamp ISO8601 UTC `minutes` minutos atrás."""

    dt = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def minimo_clipes_por_viewers(viewers: int) -> int:
    """Define limiar padrão de clipes por audiência, inspirado na lógica original."""

    if viewers <= 0:
        return 1
    if viewers < 200:
        return 1
    if viewers < 1000:
        return 2
    if viewers < 10000:
        return 3
    if viewers < 50000:
        return 3
    return 4


def _sanitize_interval(value: object, fallback: int) -> int:
    try:
        inteiro = int(value)
    except (TypeError, ValueError):
        inteiro = fallback
    if inteiro <= 0:
        return fallback
    return inteiro


def _sanitize_minimum(value: object, fallback: int) -> int:
    try:
        inteiro = int(value)
    except (TypeError, ValueError):
        inteiro = fallback
    if inteiro < 1:
        return fallback
    return inteiro


def resolve_monitoring_parameters(
    mode: str,
    presets: Mapping[str, Mapping[str, object]],
    *,
    intervalo_manual: object | None = None,
    minimo_manual: object | None = None,
    fallback_intervalo: int = 60,
    fallback_minimo: int = 3,
) -> Tuple[int, MinClipsStrategy]:
    """Resolve intervalo e mínimo de clipes considerando presets e overrides."""

    intervalo = _sanitize_interval(intervalo_manual, fallback_intervalo)
    criterio: MinClipsStrategy = minimo_manual if minimo_manual is not None else fallback_minimo

    preset = presets.get(mode)
    if preset:
        intervalo = _sanitize_interval(
            preset.get("intervalo_segundos", intervalo), fallback_intervalo
        )
        if mode != "AUTOMATICO":
            criterio = preset.get("min_clipes", criterio)

    if callable(criterio):
        return intervalo, criterio

    return intervalo, _sanitize_minimum(criterio, fallback_minimo)
