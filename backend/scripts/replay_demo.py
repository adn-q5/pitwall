import asyncio
from datetime import timedelta

from app.data import f1_data
from app.data.openf1_client import OpenF1Client
from app.replay.engine import ReplayEngine

SESSION = 9693  # Australia 2025
SPEED = 4       # 4x: an 83 s lap plays in about 21 s

# Fetch first (sync), then replay (async)
client = OpenF1Client()
driver = f1_data.get_drivers(client, SESSION)[0]
laps = f1_data.get_laps(client, SESSION, driver.driver_number)
timed = [l for l in laps if l.lap_duration and l.date_start]
best = min(timed, key=lambda l: l.lap_duration)
end = best.date_start + timedelta(seconds=best.lap_duration)
samples = f1_data.get_car_data(client, SESSION, driver.driver_number, best.date_start, end)


async def main():
    engine = ReplayEngine(samples, speed=SPEED)
    engine.clock.play()
    async for batch in engine.stream():
        s = batch[-1]
        speed = s.speed or 0
        print(f"{s.date:%H:%M:%S}  {speed:>3} km/h  {'█' * (speed // 8)}")


asyncio.run(main())