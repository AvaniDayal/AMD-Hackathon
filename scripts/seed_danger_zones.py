import json
import pickle
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

with open("backend/data/graph.pkl", "rb") as f:
    G = pickle.load(f)

with open("backend/data/segment_features.json", "r") as f:
    sf = json.load(f)

# DANGER ZONES — low lighting, high incident density
DANGER_ZONES = [
    # Lakeside Road — isolated, dark, near water
    {"lat": 19.1310, "lon": 72.9105, "radius": 250, "lighting": 0.15, "density": 0.75},
    # Back road behind H4/H5 hostels
    {"lat": 19.1295, "lon": 72.9125, "radius": 180, "lighting": 0.20, "density": 0.65},
    # Boundary wall area near Boathouse path
    {"lat": 19.1318, "lon": 72.9098, "radius": 200, "lighting": 0.18, "density": 0.70},
    # Isolated path near Staff Housing
    {"lat": 19.1290, "lon": 72.9140, "radius": 150, "lighting": 0.22, "density": 0.60},
]

# SAFE ZONES — high lighting, zero incident density
SAFE_ZONES = [
    # Main Gate Road — well lit, security, high traffic
    {"lat": 19.1334, "lon": 72.9133, "radius": 200, "lighting": 0.92, "density": 0.0},
    # Hostel Road — well lit, security posts
    {"lat": 19.1362, "lon": 72.9130, "radius": 200, "lighting": 0.88, "density": 0.0},
    # Infinite Corridor area — busiest part of campus
    {"lat": 19.1330, "lon": 72.9158, "radius": 180, "lighting": 0.90, "density": 0.0},
    # Gymkhana — open, well lit
    {"lat": 19.1345, "lon": 72.9118, "radius": 200, "lighting": 0.85, "density": 0.0},
    # IIT Hospital area — 24hr, well lit
    {"lat": 19.1320, "lon": 72.9108, "radius": 120, "lighting": 0.87, "density": 0.0},
]

danger_count = 0
safe_count = 0

for edge_id, feat in sf.items():
    u = feat.get("u")
    v = feat.get("v")
    if u is None or v is None:
        continue
    try:
        mid_lat = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
        mid_lon = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
    except:
        continue

    assigned = False

    # Check danger zones first
    for zone in DANGER_ZONES:
        dist = haversine(mid_lat, mid_lon, zone['lat'], zone['lon'])
        if dist <= zone['radius']:
            sf[edge_id]['lighting_score'] = round(
                max(0.05, zone['lighting'] + np.random.uniform(-0.05, 0.05)), 3
            )
            sf[edge_id]['incident_density'] = round(
                min(1.0, zone['density'] + np.random.uniform(-0.05, 0.05)), 3
            )
            danger_count += 1
            assigned = True
            break

    if not assigned:
        # Check safe zones
        for zone in SAFE_ZONES:
            dist = haversine(mid_lat, mid_lon, zone['lat'], zone['lon'])
            if dist <= zone['radius']:
                sf[edge_id]['lighting_score'] = round(
                    min(1.0, zone['lighting'] + np.random.uniform(-0.03, 0.03)), 3
                )
                sf[edge_id]['incident_density'] = 0.0
                safe_count += 1
                assigned = True
                break

with open("backend/data/segment_features.json", "w") as f:
    json.dump(sf, f, indent=2)

print(f"Danger segments updated: {danger_count}")
print(f"Safe segments updated: {safe_count}")
print(f"Neutral segments unchanged: {len(sf) - danger_count - safe_count}")