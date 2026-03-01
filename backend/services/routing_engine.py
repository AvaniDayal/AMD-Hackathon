import pickle
import json
import numpy as np
import osmnx as ox
import networkx as nx
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from .confidence_calculator import calculate_confidence

G = None
segment_features = None
model = None
last_origin = None
last_dest = None
active_alert_zones = []  # persists across route changes until backend restart

FEATURES = [
    'lighting_score', 'incident_density', 'safe_stop_proximity',
    'time_sin', 'time_cos', 'day_sin', 'day_cos'
]


def load_data():
    global G, segment_features
    with open("backend/data/graph.pkl", "rb") as f:
        G = pickle.load(f)
    with open("backend/data/segment_features.json", "r") as f:
        segment_features = json.load(f)
    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")


def load_model():
    global model
    with open("ml/saved_models/safety_rf_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("Model loaded in routing engine.")


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def precompute_costs(hour, day):
    time_sin = np.sin(2 * np.pi * hour / 24)
    time_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * day / 7)
    day_cos = np.cos(2 * np.pi * day / 7)

    rows = []
    edge_keys = []

    for u, v, data in G.edges(data=True):
        edge_id = f"{u}_{v}"
        feat = segment_features.get(edge_id, {})
        rows.append({
            'lighting_score': feat.get('lighting_score', 0.5),
            'incident_density': feat.get('incident_density', 0.0),
            'safe_stop_proximity': feat.get('safe_stop_proximity', 0.3),
            'time_sin': time_sin,
            'time_cos': time_cos,
            'day_sin': day_sin,
            'day_cos': day_cos
        })
        edge_keys.append((u, v))

    df = pd.DataFrame(rows, columns=FEATURES)
    probs = model.predict_proba(df)[:, 1]
    probs = np.maximum(probs, 0.01)

    for (u, v), prob in zip(edge_keys, probs):
        G[u][v][0]['safety_prob'] = float(prob)
        G[u][v][0]['safety_cost'] = float(-np.log(prob))

    # Re-apply all active alert zone penalties after fresh scoring
    if active_alert_zones:
        for (alat, alon) in active_alert_zones:
            for u, v, data in G.edges(data=True):
                dist = haversine(G.nodes[u]['y'], G.nodes[u]['x'], alat, alon)
                if dist <= 200:
                    G[u][v][0]['safety_cost'] = 999.0

    print(f"Precomputed {len(edge_keys)} edges. Active alert zones: {len(active_alert_zones)}")


def get_routes(origin_lat, origin_lon, dest_lat, dest_lon, hour=22, day=4):
    global last_origin, last_dest

    last_origin = (origin_lat, origin_lon)
    last_dest = (dest_lat, dest_lon)

    precompute_costs(hour, day)

    origin_node = ox.distance.nearest_nodes(G, origin_lon, origin_lat)
    dest_node = ox.distance.nearest_nodes(G, dest_lon, dest_lat)

    fast_path = nx.shortest_path(G, origin_node, dest_node, weight='length')
    safe_path = nx.shortest_path(G, origin_node, dest_node, weight='safety_cost')

    return fast_path, safe_path


def path_to_coords(path):
    return [[G.nodes[n]['y'], G.nodes[n]['x']] for n in path]


def path_avg_safety(path):
    scores = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        scores.append(G[u][v][0].get('safety_prob', 0.5))
    return round(sum(scores) / len(scores), 3) if scores else 0.5


def path_confidence(path):
    with open("backend/data/segment_features.json", "r") as f:
        sf = json.load(f)
    total_reports = 0
    last_time = None
    for i in range(len(path) - 1):
        edge_id = f"{path[i]}_{path[i + 1]}"
        feat = sf.get(edge_id, {})
        total_reports += len(feat.get("incident_reports", []))
        t = feat.get("last_report_time")
        if t:
            last_time = t
    return calculate_confidence(total_reports, last_time)


def reroute_avoiding_zone(alert_lat, alert_lon, avoid_radius=200,
                           origin=None, dest=None):
    global last_origin, last_dest, active_alert_zones

    # Update stored coordinates if provided by caller
    if origin:
        last_origin = origin
    if dest:
        last_dest = dest

    if last_origin is None or last_dest is None:
        print("Reroute skipped: no origin/dest stored.")
        return None

    # Add new zone and persist
    active_alert_zones.append((alert_lat, alert_lon))

    # Get dest node — never block edges adjacent to destination
    dest_node = ox.distance.nearest_nodes(G, last_dest[1], last_dest[0])
    dest_neighbors = set(G.predecessors(dest_node)) | set(G.successors(dest_node))

    # Apply all zone penalties
    for (alat, alon) in active_alert_zones:
        for u, v, data in G.edges(data=True):
            # Never block the final approach edges to destination
            if u == dest_node or v == dest_node:
                continue
            if u in dest_neighbors or v in dest_neighbors:
                continue
            dist = haversine(G.nodes[u]['y'], G.nodes[u]['x'], alat, alon)
            if dist <= avoid_radius:
                G[u][v][0]['safety_cost'] = 999.0

    origin_node = ox.distance.nearest_nodes(G, last_origin[1], last_origin[0])

    try:
        new_path = nx.shortest_path(G, origin_node, dest_node, weight='safety_cost')
        print(f"Reroute successful: {len(new_path)} nodes.")
        return path_to_coords(new_path)
    except Exception as e:
        print(f"Reroute failed: {e}")
        return None