import time
from urllib.parse import urlencode

import httpx

from app.data.cache import Cache

BASE_URL = "https://api.openf1.org/v1"
MIN_INTERVAL = 0.4  # seconds between calls, stays under the rate limit


class OpenF1Error(Exception):
    pass


class OpenF1Client:
    def __init__(self, cache=None, timeout=30.0, max_retries=4):
        self._http = httpx.Client(base_url=BASE_URL, timeout=timeout)
        self._cache = cache or Cache()
        self._max_retries = max_retries
        self._last_call = 0.0

    def _throttle(self):
        wait = MIN_INTERVAL - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def get(self, endpoint, ttl=None, **params):
        """GET an endpoint. Cached forever by default (historical data doesn't change)."""
        key = f"{endpoint}?{urlencode(sorted(params.items()))}"
        cached = self._cache.get(key, ttl=ttl)
        if cached is not None:
            return cached

        last_error = None
        for attempt in range(self._max_retries):
            self._throttle()
            try:
                r = self._http.get(f"/{endpoint}", params=params)
            except (httpx.TimeoutException, httpx.TransportError) as e:
                last_error = e                      # network hiccup: retry
            else:
                if r.status_code == 429 or r.status_code >= 500:
                    last_error = OpenF1Error(f"HTTP {r.status_code}")  # retry
                elif r.status_code >= 400:
                    raise OpenF1Error(f"HTTP {r.status_code}: {r.text[:200]}")  # our bug, don't retry
                else:
                    data = r.json()
                    self._cache.set(key, data)
                    return data
            time.sleep(2 ** attempt)                # backoff: 1s, 2s, 4s, 8s

        raise OpenF1Error(f"Failed after {self._max_retries} attempts") from last_error