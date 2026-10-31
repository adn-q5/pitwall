import asyncio
from datetime import datetime, timedelta, timezone

from app.data.models import CarSample
from app.replay.engine import ReplayEngine


def make_samples(n=100):
    start = datetime(2025, 3, 16, 5, 0, tzinfo=timezone.utc)
    return [
        CarSample(driver_number=1, date=start + timedelta(seconds=i * 0.27), speed=i)
        for i in range(n)
    ]


def test_replay_emits_everything_in_order():
    engine = ReplayEngine(make_samples(), speed=50)  # 50x keeps the test fast
    engine.clock.play()
    got = []

    async def run():
        async for batch in engine.stream():
            got.extend(batch)

    asyncio.run(run())
    assert [s.speed for s in got] == list(range(100))


def test_paused_engine_does_not_advance():
    engine = ReplayEngine(make_samples(), speed=50)  # never played
    got = []

    async def run():
        async for batch in engine.stream():
            got.extend(batch)

    async def main():
        try:
            await asyncio.wait_for(run(), timeout=0.3)
        except asyncio.TimeoutError:
            pass

    asyncio.run(main())
    assert len(got) <= 1  # at most the very first sample, which sits at t0