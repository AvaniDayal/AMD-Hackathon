import json

with open("backend/data/segment_features.json", "r") as f:
    sf = json.load(f)

cleaned = 0
for edge_id, feat in sf.items():
    real_reports = [
        r for r in feat.get("incident_reports", [])
        if r.get("lat", 0) != 0 and r.get("lon", 0) != 0
    ]
    if len(real_reports) != len(feat.get("incident_reports", [])):
        cleaned += len(feat.get("incident_reports", [])) - len(real_reports)
        sf[edge_id]["incident_reports"] = real_reports
        if not real_reports:
            sf[edge_id]["last_report_time"] = None

with open("backend/data/segment_features.json", "w") as f:
    json.dump(sf, f, indent=2)

print(f"Removed {cleaned} fake seeded reports.")