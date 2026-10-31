# PitWall

Real-time Formula 1 telemetry replay dashboard. A FastAPI backend streams a real race lap over WebSockets, and a React frontend draws speed, throttle and brake live, with play, pause, speed and seek controls.

![PitWall dashboard](docs/dashboard.png)

## Why this project

Live F1 telemetry is paid, but historical data is free. So PitWall replays a past session through its own streaming server, as if it were live. If a live source is plugged in later, only the data layer changes.

## Features

- Replay engine with a virtual clock: play, pause, 1x / 4x / 10x speed, and seek
- WebSocket streaming of telemetry (speed, throttle, brake, gear, RPM) to the browser
- Live charts that draw left to right as the lap progresses
- Cached, rate-limited API client with retries and exponential backoff
- Typed data models (Pydantic) that handle missing values
- Automated tests for the cache, the replay engine and the WebSocket endpoint

## Architecture

```
OpenF1 API --> API client (retries, throttling) --> SQLite cache
                                                      |
                        Replay engine (virtual clock) <
                                      |
                        FastAPI WebSocket  --->  React dashboard
```

## Tech stack

- **Backend:** Python, FastAPI, WebSockets, Pydantic, httpx, SQLite, pytest
- **Frontend:** React, Vite, Recharts
- **Data:** OpenF1 (historical F1 data)

## Run it locally

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open the URL that Vite prints (usually http://localhost:5173).

Run the tests:

```bash
cd backend
pytest
```

## Roadmap

- [ ] Race and driver pickers
- [ ] Track map drawn from GPS coordinates
- [ ] Tyre degradation analysis
- [ ] AI race engineer (LLM with tool calling over the telemetry)
- [ ] Deployment

## Data and disclaimer

Telemetry comes from the community-run [OpenF1](https://openf1.org) API. This is an independent educational project. It is not affiliated with or endorsed by Formula 1 or the FIA.
