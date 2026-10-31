import httpx

BASE = "https://api.openf1.org/v1"

def get(endpoint: str, **params):
    r = httpx.get(f"{BASE}/{endpoint}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# 1) Which races happened in 2025?
sessions = get("sessions", year=2025, session_name="Race")
print(f"{len(sessions)} race sessions found\n")
for s in sessions:
    print(s["session_key"], s["country_name"], s["date_start"][:10])

# 2) Pick one and look at its drivers
session_key = sessions[0]["session_key"]
drivers = get("drivers", session_key=session_key)
print("\nFirst driver object (look at the fields!):")
print(drivers[0])