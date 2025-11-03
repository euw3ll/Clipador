"""Domínio compartilhado do Clipador."""

from .live_validation import is_real_live_clip  # noqa: F401
from .monitoring import (  # noqa: F401
    BurstConfig,
    Clip,
    ClipGroup,
    get_time_minutes_ago,
    group_clips_by_burst,
    minimo_clipes_por_viewers,
    resolve_monitoring_parameters,
)

__all__ = [
    "BurstConfig",
    "Clip",
    "ClipGroup",
    "group_clips_by_burst",
    "get_time_minutes_ago",
    "minimo_clipes_por_viewers",
    "resolve_monitoring_parameters",
    "is_real_live_clip",
]
