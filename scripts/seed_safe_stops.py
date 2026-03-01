import json
import os

# Real approximate coordinates of safe locations on/near IIT Bombay
safe_stops = [
    {"id": 1, "name": "IIT Bombay Main Gate Security", "lat": 19.1334, "lon": 72.9133},
    {"id": 2, "name": "Hostel Area Security Post", "lat": 19.1350, "lon": 72.9150},
    {"id": 3, "name": "Hospital/Medical Centre IIT", "lat": 19.1320, "lon": 72.9140},
    {"id": 4, "name": "24hr Convenience Store", "lat": 19.1360, "lon": 72.9120},
    {"id": 5, "name": "Library Security Desk", "lat": 19.1340, "lon": 72.9160}
]

with open("backend/data/safe_stops.json", "w") as f:
    json.dump(safe_stops, f, indent=2)

print(f"Seeded {len(safe_stops)} safe stops.")