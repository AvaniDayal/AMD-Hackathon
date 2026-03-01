from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import route, incident
from .services.routing_engine import load_data, load_model as load_routing_model
from .services.safety_scorer import load_model
import json
import os

app = FastAPI(title="SafeCompanion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clear_session_reports():
    """Clear incident reports from previous session on startup.
    Keeps segment features (lighting, density seeding) but wipes
    old reports so convergence detection starts fresh each session."""
    path = "backend/data/segment_features.json"
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        sf = json.load(f)
    for edge_id in sf:
        sf[edge_id]["incident_reports"] = []
        sf[edge_id]["last_report_time"] = None
        # Reset incident density back to seeded value (not accumulated)
        # Keep lighting_score and safe_stop_proximity unchanged
    with open(path, "w") as f:
        json.dump(sf, f, indent=2)
    print("Session reports cleared. Segment features retained.")


@app.on_event("startup")
def startup():
    clear_session_reports()
    load_model()
    load_routing_model()
    load_data()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(route.router)
app.include_router(incident.router)