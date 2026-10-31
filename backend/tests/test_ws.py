from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app import main
from app.data.models import CarSample


def make_samples(n=100):
    start = datetime(2025, 3, 16, 5, 0, tzinfo=timezone.utc)
    return [
        CarSample(driver_number=1, date=start + timedelta(seconds=i * 0.27), speed=i)
        for i in range(n)
    ]


class FakeLap:
    lap_number = 1
    lap_duration = 27.0


def test_ws_streams_everything_then_done(monkeypatch):
    monkeypatch.setattr(main, "load_lap", lambda s, d, l: (FakeLap(), make_samples()))

    with TestClient(main.app) as c:
        with c.websocket_connect("/ws/replay?session=1&driver=1&speed=50") as ws:
            assert ws.receive_json()["type"] == "ready"
            count = 0
            while True:
                msg = ws.receive_json()
                if msg["type"] == "done":
                    break
                count += len(msg["data"])
            assert count == 100