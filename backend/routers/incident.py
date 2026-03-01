from fastapi import APIRouter
from ..models.schemas import IncidentReport
from ..services.nlp_classifier import classify_incident
from ..services.convergence_detector import check_convergence
from ..services import routing_engine
from ..services.routing_engine import reroute_avoiding_zone
import json
import osmnx as ox
from datetime import datetime

router = APIRouter()


@router.post("/incident")
def report_incident(report: IncidentReport):
    G = routing_engine.G
    segment_features = routing_engine.segment_features

    if G is None:
        return {"error": "Graph not loaded"}

    # Always sync origin/dest from frontend so rerouting works even after restart
    origin = None
    dest = None
    if report.origin_lat is not None and report.dest_lat is not None:
        origin = (report.origin_lat, report.origin_lon)
        dest = (report.dest_lat, report.dest_lon)
        routing_engine.last_origin = origin
        routing_engine.last_dest = dest

    # Classify incident text
    classification = classify_incident(report.text)

    # Find nearest graph edge to incident location
    nearest_node = ox.distance.nearest_nodes(G, report.lon, report.lat)
    neighbors = list(G.neighbors(nearest_node))
    nearest_edge_id = f"{nearest_node}_{neighbors[0]}" if neighbors else None

    now = datetime.utcnow().isoformat()

    # Update segment features for affected edge
    if nearest_edge_id and nearest_edge_id in segment_features:
        segment_features[nearest_edge_id]["incident_density"] = min(
            segment_features[nearest_edge_id]["incident_density"] + 0.1, 1.0
        )
        segment_features[nearest_edge_id]["incident_reports"].append({
            "lat": report.lat,
            "lon": report.lon,
            "timestamp": now,
            "category": classification["category"],
            "severity": classification["severity"]
        })
        segment_features[nearest_edge_id]["last_report_time"] = now

    # Persist updated features to disk
    with open("backend/data/segment_features.json", "w") as f:
        json.dump(segment_features, f, indent=2)

    # Collect all real reports for convergence check
    all_reports = []
    for edge_data in segment_features.values():
        for r in edge_data.get("incident_reports", []):
            # Only include reports with valid coordinates
            if r.get("lat", 0) != 0 and r.get("lon", 0) != 0:
                all_reports.append(r)

    alert, alert_lat, alert_lon = check_convergence(all_reports)

    # Compute rerouted safe path if alert triggered
    new_safe_route = None
    if alert and alert_lat is not None:
        new_safe_route = reroute_avoiding_zone(
            alert_lat, alert_lon,
            avoid_radius=200,
            origin=origin,
            dest=dest
        )

    return {
        "classification": classification,
        "alert": alert,
        "alert_lat": alert_lat,
        "alert_lon": alert_lon,
        "new_safe_route": new_safe_route
    }