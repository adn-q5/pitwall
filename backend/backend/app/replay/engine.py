import asyncio
import bisect
import time
from datetime import datetime, timedelta

from app.data.models import CarSample


class ReplayClock:
    """Maps real time to race time. Supports play, pause, speed and seek."""

    def __init__(self, start: datetime, speed: float = 1.0):
        self._virtual = start      # race time at the last checkpoint
        self._speed = speed
        self._anchor = None        # monotonic time of last checkpoint; None = paused
        self.seek_count = 0        # lets the engine notice jumps

    def now(self) -> datetime:
        if self._anchor is None:
            return self._virtual
        elapsed = time.monotonic() - self._anchor
        return self._virtual + timedelta(seconds=elapsed * self._speed)

    @property
    def playing(self) -> bool:
        return self._anchor is not None

    def play(self):
        if self._anchor is None:
            self._anchor = time.monotonic()

    def pause(self):
        self._virtual = self.now()
        self._anchor = None

    def set_speed(self, speed: float):
        self._virtual = self.now()          # checkpoint BEFORE changing speed
        if self._anchor is not None:
            self._anchor = time.monotonic()
        self._speed = speed

    def seek(self, to: datetime):
        self._virtual = to
        if self._anchor is not None:
            self._anchor = time.monotonic()
        self.seek_count += 1


class ReplayEngine:
    """Streams telemetry samples in batches as the virtual clock advances."""

    def __init__(self, samples: list[CarSample], speed: float = 1.0, tick: float = 0.05):
        if not samples:
            raise ValueError("No samples to replay")
        self.samples = sorted(samples, key=lambda s: s.date)
        self._times = [s.date for s in self.samples]
        self.clock = ReplayClock(self._times[0], speed)
        self.tick = tick

    async def stream(self):
        """Yield lists of samples whose timestamp has been reached."""
        cursor = 0
        seen_seek = self.clock.seek_count
        while cursor < len(self.samples):
            now = self.clock.now()
            target = bisect.bisect_right(self._times, now)  # samples with date <= now

            if self.clock.seek_count != seen_seek:          # user jumped: don't flood
                seen_seek = self.clock.seek_count
                cursor = target
            elif target > cursor:
                yield self.samples[cursor:target]
                cursor = target

            await asyncio.sleep(self.tick)