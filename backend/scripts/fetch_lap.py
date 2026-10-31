from datetime import timedelta

from app.data import f1_data
from app.data.openf1_client import OpenF1Client

client = OpenF1Client()
SESSION = 9693  # Australia 2025, from your earlier output

drivers = f1_data.get_drivers(client, SESSION)
print(f"{len(drivers)} drivers")

d = drivers[0]
laps = f1_data.get_laps(client, SESSION, d.driver_number)
timed = [l for l in laps if l.lap_duration and l.date_start]
best = min(timed, key=lambda l: l.lap_duration)
print(f"{d.full_name}: {len(laps)} laps, fastest = lap {best.lap_number} ({best.lap_duration:.3f}s)")

end = best.date_start + timedelta(seconds=best.lap_duration)
samples = f1_data.get_car_data(client, SESSION, d.driver_number, best.date_start, end)
top = max(s.speed for s in samples if s.speed is not None)
print(f"{len(samples)} telemetry samples, top speed {top} km/h")