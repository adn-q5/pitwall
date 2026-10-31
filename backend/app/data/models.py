from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")  # ignore fields we don't use


class Driver(_Base):
    driver_number: int
    name_acronym: str
    full_name: str
    team_name: Optional[str] = None
    team_colour: Optional[str] = None
    country_code: Optional[str] = None  # remember: it was None for Verstappen


class Lap(_Base):
    driver_number: int
    lap_number: int
    date_start: Optional[datetime] = None
    lap_duration: Optional[float] = None
    duration_sector_1: Optional[float] = None
    duration_sector_2: Optional[float] = None
    duration_sector_3: Optional[float] = None
    is_pit_out_lap: Optional[bool] = None


class Stint(_Base):
    driver_number: int
    stint_number: int
    lap_start: Optional[int] = None
    lap_end: Optional[int] = None
    compound: Optional[str] = None
    tyre_age_at_start: Optional[int] = None


class CarSample(_Base):
    driver_number: int
    date: datetime
    speed: Optional[int] = None
    throttle: Optional[int] = None
    brake: Optional[int] = None
    n_gear: Optional[int] = None
    rpm: Optional[int] = None
    drs: Optional[int] = None