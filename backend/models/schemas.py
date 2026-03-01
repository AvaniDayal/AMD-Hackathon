from pydantic import BaseModel
from typing import Optional


class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    hour: Optional[int] = 22
    day: Optional[int] = 4


class IncidentReport(BaseModel):
    lat: float
    lon: float
    text: str
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None
    dest_lat: Optional[float] = None
    dest_lon: Optional[float] = None


class RouteResponse(BaseModel):
    fast_route: list
    safe_route: list
    fast_safety_score: float
    safe_safety_score: float
    fast_confidence: float
    safe_confidence: float