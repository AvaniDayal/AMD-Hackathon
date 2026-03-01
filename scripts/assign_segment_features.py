import pickle
import json
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

with open("backend/data/safe_stops.json", "r") as f:
    safe_stops = json.load(f)

np.random.seed(42)
segment_features = {}

for u, v, data in G.edges(data=True):
    edge_id = f"{u}_{v}"
    
    # Get midpoint of edge for distance calculation
    u_lat = G.nodes[u]['y']
    u_lon = G.nodes[u]['x']
    v_lat = G.nodes[v]['y']
    v_lon = G.nodes[v]['x']
    mid_lat = (u_lat + v_lat) / 2
    mid_lon = (u_lon + v_lon) / 2
    
    # Lighting score based on road type
    highway = data.get('highway', 'path')
    if isinstance(highway, list):
        highway = highway[0]
    
    if highway in ['primary', 'secondary', 'tertiary']:
        lighting_score = np.random.uniform(0.7, 1.0)
    elif highway in ['residential', 'unclassified']:
        lighting_score = np.random.uniform(0.4, 0.75)
    else:
        lighting_score = np.random.uniform(0.1, 0.5)
    
    # Safe stop proximity (normalized 0-1, closer = higher)
    min_dist = min(
        haversine(mid_lat, mid_lon, s['lat'], s['lon'])
        for s in safe_stops
    )
    safe_stop_proximity = max(0, 1 - (min_dist / 500))
    
    segment_features[edge_id] = {
        "u": u,
        "v": v,
        "lighting_score": round(lighting_score, 3),
        "incident_density": 0.0,
        "safe_stop_proximity": round(safe_stop_proximity, 3),
        "incident_reports": [],
        "last_report_time": None
    }

with open("backend/data/segment_features.json", "w") as f:
    json.dump(segment_features, f, indent=2)

print(f"Features assigned to {len(segment_features)} segments.")