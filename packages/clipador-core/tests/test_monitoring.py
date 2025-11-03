from datetime import datetime, timedelta, timezone

from clipador_core.monitoring import (
    BurstConfig,
    Clip,
    get_time_minutes_ago,
    group_clips_by_burst,
    minimo_clipes_por_viewers,
    resolve_monitoring_parameters,
)


def make_clip(minutes_ago: float, clip_id: str, viewers: int = 0) -> Clip:
    created_at = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return Clip(id=clip_id, created_at=created_at, viewer_count=viewers)


def test_group_clips_by_burst_basic():
    clips = [
        make_clip(10, "a", viewers=150),
        make_clip(9.5, "b", viewers=150),
        make_clip(9, "c", viewers=150),
        make_clip(4, "d", viewers=10),
    ]

    config = BurstConfig(interval_seconds=120, min_clips=2)
    groups = group_clips_by_burst(clips, config)

    assert len(groups) == 1
    group = groups[0]
    assert {clip.id for clip in group.clips} == {"a", "b", "c"}
    assert group.start == min(c.created_at for c in group.clips)
    assert group.end == max(c.created_at for c in group.clips)


def test_clip_group_to_payload():
    clips = [
        make_clip(5, "a"),
        make_clip(4.5, "b"),
        make_clip(4, "c"),
    ]
    config = BurstConfig(interval_seconds=180, min_clips=2)
    group = group_clips_by_burst(clips, config)[0]

    payload = group.to_payload()
    assert payload["inicio_iso"].endswith("Z")
    assert payload["fim"].endswith("Z")
    assert len(payload["clipes"]) == 3
    assert payload["clipes"][0]["id"] == "a"


def test_group_clips_respects_min_strategy_function():
    config = BurstConfig(interval_seconds=180, min_clips=minimo_clipes_por_viewers)

    low_view_clips = [
        make_clip(5, "a", viewers=50),
        make_clip(4.5, "b", viewers=50),
        make_clip(4, "c", viewers=50),
    ]
    groups_low = group_clips_by_burst(low_view_clips, config)
    assert len(groups_low) == 1
    assert len(groups_low[0].clips) == 3

    high_view_clips = [
        make_clip(6, "h1", viewers=20000),
        make_clip(5.5, "h2", viewers=20000),
    ]
    groups_high = group_clips_by_burst(high_view_clips, config)
    assert groups_high == []


def test_clip_from_iso():
    clip = Clip.from_iso("abc", "2024-01-01T12:00:00.000Z", viewer_count=42)
    assert clip.id == "abc"
    assert clip.viewer_count == 42
    assert clip.created_at.tzinfo is not None
    assert clip.created_at.isoformat().startswith("2024-01-01T12:00:00")


def test_get_time_minutes_ago_format_and_offset():
    minutes = 3
    ts = get_time_minutes_ago(minutes)
    assert ts.endswith("Z")
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    delta_seconds = abs((datetime.now(timezone.utc) - parsed).total_seconds() - minutes * 60)
    assert delta_seconds < 5


def test_minimo_clipes_por_viewers_thresholds():
    assert minimo_clipes_por_viewers(0) == 1
    assert minimo_clipes_por_viewers(150) == 1
    assert minimo_clipes_por_viewers(500) == 2
    assert minimo_clipes_por_viewers(5000) == 3
    assert minimo_clipes_por_viewers(60000) == 4


def test_resolve_monitoring_parameters_with_presets_and_manual():
    presets = {
        "PADRAO": {"intervalo_segundos": 90, "min_clipes": 2},
        "AUTOMATICO": {"intervalo_segundos": 120, "min_clipes": minimo_clipes_por_viewers},
    }

    intervalo, minimo = resolve_monitoring_parameters(
        "PADRAO",
        presets,
        intervalo_manual="30",
        minimo_manual="5",
        fallback_intervalo=60,
        fallback_minimo=3,
    )
    assert intervalo == 90
    assert minimo == 2

    intervalo_auto, minimo_auto = resolve_monitoring_parameters(
        "AUTOMATICO",
        presets,
        intervalo_manual=None,
        minimo_manual=None,
        fallback_intervalo=60,
        fallback_minimo=3,
    )
    assert intervalo_auto == 120
    assert minimo_auto == 3

    intervalo_default, minimo_default = resolve_monitoring_parameters(
        "DESCONHECIDO",
        presets,
        intervalo_manual="invalid",
        minimo_manual="0",
        fallback_intervalo=75,
        fallback_minimo=4,
    )
    assert intervalo_default == 75
    assert minimo_default == 4
