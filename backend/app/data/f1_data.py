from datetime import datetime

from app.data.models import CarSample, Driver, Lap, Stint
from app.data.openf1_client import OpenF1Client


def get_drivers(client: OpenF1Client, session_key: int) -> list[Driver]:
    rows = client.get("drivers", session_key=session_key)
    return [Driver(**r) for r in rows]


def get_laps(client: OpenF1Client, session_key: int, driver_number: int) -> list[Lap]:
    rows = client.get("laps", session_key=session_key, driver_number=driver_number)
    return [Lap(**r) for r in rows]


def get_stints(client: OpenF1Client, session_key: int, driver_number: int) -> list[Stint]:
    rows = client.get("stints", session_key=session_key, driver_number=driver_number)
    return [Stint(**r) for r in rows]


def get_car_data(
    client: OpenF1Client,
    session_key: int,
    driver_number: int,
    start: datetime,
    end: datetime,
) -> list[CarSample]:
    """Telemetry in a time window. Never fetch a whole race at once."""
    rows = client.get(
        "car_data",
        session_key=session_key,
        driver_number=driver_number,
        **{"date>": start.isoformat(), "date<": end.isoformat()},
    )
    return [CarSample(**r) for r in rows]
