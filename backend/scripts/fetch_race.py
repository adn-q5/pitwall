import time
from app.data.openf1_client import OpenF1Client

client = OpenF1Client()

start = time.perf_counter()
sessions = client.get("sessions", year=2025, session_name="Race")
elapsed = time.perf_counter() - start

print(f"{len(sessions)} races in {elapsed:.3f}s")