from fastapi import APIRouter
from ..models.schemas import RouteRequest
from ..services.routing_engine import get_routes, path_to_coords, path_avg_safety, path_confidence

router = APIRouter()

@router.post("/route")
def compute_route(req: RouteRequest):
    fast_path, safe_path = get_routes(
        req.origin_lat, req.origin_lon,
        req.dest_lat, req.dest_lon,
        req.hour, req.day
    )
    return {
        "fast_route": path_to_coords(fast_path),
        "safe_route": path_to_coords(safe_path),
        "fast_safety_score": round(path_avg_safety(fast_path) * 100),
        "safe_safety_score": round(path_avg_safety(safe_path) * 100),
        "fast_confidence": round(path_confidence(fast_path) * 100),
        "safe_confidence": round(path_confidence(safe_path) * 100)
    }