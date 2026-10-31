import asyncio
import threading
from datetime import timedelta
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from app.data import f1_data
from app.data.openf1_client import OpenF1Client
from app.replay.engine import ReplayEngine

app = FastAPI(title="PitWall")
client = OpenF1Client()
_fetch_lock = threading.Lock()  # one shared client/SQLite connection: fetch one at a time

STATIC = Path(__file__).parent / "static"
MAX_SPEED = 50.0


def load_lap(session_key: int, driver_number: int, lap_number: int | None):
    """Blocking: runs in a worker thread. Returns (lap, samples)."""
    with _fetch_lock:
        laps = f1_data.get_laps(client, session_key, driver_number)
        timed = [l for l in laps if l.lap_duration and l.date_start]
        if not timed:
            raise ValueError("No timed laps for this driver")
        if lap_number is None:
            lap = min(timed, key=lambda l: l.lap_duration)
        else:
            matches = [l for l in timed if l.lap_number == lap_number]
            if not matches:
                raise ValueError(f"Lap {lap_number} not found")
            lap = matches[0]
        end = lap.date_start + timedelta(seconds=lap.lap_duration)
        samples = f1_data.get_car_data(client, session_key, driver_number, lap.date_start, end)
    if not samples:
        raise ValueError("No telemetry for this lap")
    return lap, samples


def to_payload(s, t0):
    return {
        "t": round((s.date - t0).total_seconds(), 3),  # seconds since lap start
        "speed": s.speed,
        "throttle": s.throttle,
        "brake": s.brake,
        "gear": s.n_gear,
        "rpm": s.rpm,
        "drs": s.drs,
    }


@app.get("/")
def test_page():
    return FileResponse(STATIC / "test.html")


@app.websocket("/ws/replay")
async def replay_ws(
    ws: WebSocket,
    session: int,
    driver: int,
    lap: int | None = None,
    speed: float = 1.0,
):
    await ws.accept()
    speed = min(max(speed, 0.1), MAX_SPEED)

    try:
        lap_info, samples = await asyncio.to_thread(load_lap, session, driver, lap)
    except Exception as e:
        await ws.send_json({"type": "error", "message": str(e)})
        await ws.close()
        return

    engine = ReplayEngine(samples, speed=speed)
    t0 = engine.samples[0].date
    await ws.send_json({
        "type": "ready",
        "lap_number": lap_info.lap_number,
        "lap_duration": lap_info.lap_duration,
        "samples": len(samples),
    })
    engine.clock.play()

    async def sender():
        try:
            async for batch in engine.stream():
                await ws.send_json({"type": "samples", "data": [to_payload(s, t0) for s in batch]})
            await ws.send_json({"type": "done"})
        except (WebSocketDisconnect, RuntimeError):
            pass  # client left

    async def receiver():
        try:
            while True:
                msg = await ws.receive_json()
                action = msg.get("action")
                try:
                    if action == "play":
                        engine.clock.play()
                    elif action == "pause":
                        engine.clock.pause()
                    elif action == "speed":
                        engine.clock.set_speed(min(max(float(msg["value"]), 0.1), MAX_SPEED))
                    elif action == "seek":
                        offset = max(float(msg["value"]), 0.0)
                        engine.clock.seek(t0 + timedelta(seconds=offset))
                except (KeyError, TypeError, ValueError):
                    await ws.send_json({"type": "error", "message": f"Bad command: {msg}"})
        except (WebSocketDisconnect, RuntimeError):
            pass

    tasks = [asyncio.create_task(sender()), asyncio.create_task(receiver())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            t.cancel()