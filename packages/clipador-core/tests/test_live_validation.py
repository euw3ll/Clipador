import asyncio

from clipador_core.live_validation import is_real_live_clip


class FakeTwitchClient:
    def __init__(self, *, stream=None, vod=None):
        self._stream = stream
        self._vod = vod
        self.calls = {"stream": 0, "vod": 0}

    async def get_stream_info(self, user_id: str):  # pragma: no cover - simple proxy
        self.calls["stream"] += 1
        return self._stream

    async def get_vod_by_id(self, vod_id: str):
        self.calls["vod"] += 1
        return self._vod


def test_is_real_live_clip_true_when_stream_matches():
    stream = {"started_at": "2024-01-01T12:00:00.000Z"}
    vod = {"type": "archive", "created_at": "2024-01-01T12:01:00.000Z"}
    client = FakeTwitchClient(stream=stream, vod=vod)

    clip = {
        "id": "123",
        "created_at": "2024-01-01T12:02:00.000Z",
        "video_id": "987",
    }

    assert asyncio.run(is_real_live_clip(clip, twitch_client=client, user_id="999")) is True
    assert client.calls["stream"] == 1
    assert client.calls["vod"] == 1


def test_is_real_live_clip_false_when_stream_missing():
    client = FakeTwitchClient(stream=None)
    clip = {"created_at": "2024-01-01T12:02:00.000Z"}

    assert asyncio.run(is_real_live_clip(clip, twitch_client=client, user_id="999")) is False


def test_is_real_live_clip_false_when_vod_not_archive():
    stream = {"started_at": "2024-01-01T12:00:00.000Z"}
    vod = {"type": "highlight", "created_at": "2024-01-01T12:01:00.000Z"}
    client = FakeTwitchClient(stream=stream, vod=vod)
    clip = {
        "id": "123",
        "created_at": "2024-01-01T12:02:00.000Z",
        "video_id": "987",
    }

    assert asyncio.run(is_real_live_clip(clip, twitch_client=client, user_id="999")) is False
