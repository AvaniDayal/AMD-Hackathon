import { useState } from "react";
import React from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Circle,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getRoutes } from "../services/api";
import RoutePanel from "./RoutePanel";
import IncidentForm from "./IncidentForm";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const IIT_BOMBAY_CENTER = [19.1334, 72.9133];

const originIcon = L.divIcon({
  html: `<div style="background:#2563eb;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>`,
  className: "",
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const destIcon = L.divIcon({
  html: `<div style="background:#16a34a;width:14px;height:14px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4)"></div>`,
  className: "",
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

const incidentIcon = L.divIcon({
  html: `<div style="font-size:18px;line-height:1">⚠️</div>`,
  className: "",
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

function MapClickHandler({ onMapClick, mode }) {
  useMapEvents({
    click(e) {
      if (mode) onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function Map() {
  const [routes, setRoutes] = useState(null);
  const [routeData, setRouteData] = useState(null);
  const [alertZones, setAlertZones] = useState([]);
  const [incidentMarkers, setIncidentMarkers] = useState([]);
  const [origin, setOrigin] = useState(null);
  const [dest, setDest] = useState(null);
  const [clickMode, setClickMode] = useState(null);
  const [incidentLocation, setIncidentLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [safeRouteOverride, setSafeRouteOverride] = useState(null);
  const [routeInfo, setRouteInfo] = useState(null);

  // Fetch routes and update all route state
  const fetchRoutes = async (orig, dst) => {
    setLoading(true);
    //setSafeRouteOverride(null);
    try {
      const res = await getRoutes({
        origin_lat: orig.lat,
        origin_lon: orig.lon,
        dest_lat: dst.lat,
        dest_lon: dst.lon,
        hour: 22,
        day: 4,
      });
      setRoutes(res.data);
      setRouteData(res.data);
    } catch (err) {
      console.error("Route error:", err);
    }
    setLoading(false);
  };

  const handleMapClick = (lat, lon) => {
    if (clickMode === "origin") {
      const newOrigin = { lat, lon };
      setOrigin(newOrigin);
      setClickMode(null);
      if (dest) fetchRoutes(newOrigin, dest);
    } else if (clickMode === "dest") {
      const newDest = { lat, lon };
      setDest(newDest);
      setClickMode(null);
      if (origin) fetchRoutes(origin, newDest);
    } else if (clickMode === "incident") {
      setIncidentLocation({ lat, lon });
      setClickMode(null);
    }
  };

  const handleAlert = (lat, lon) => {
    setAlertZones((prev) => [...prev, { lat, lon, id: Date.now() }]);
  };

  const handleReroute = (newRoute) => {
    if (newRoute && newRoute.length > 0) {
      setSafeRouteOverride(newRoute);
    }
  };

  // Called after incident submitted — adds marker AND refreshes scores
  const handleIncidentSubmitted = (lat, lon) => {
    setIncidentMarkers((prev) => [...prev, { lat, lon, id: Date.now() }]);
    setIncidentLocation(null);
    // Re-fetch routes to update safety scores with new incident data
    // if (origin && dest) {
    //   setTimeout(() => fetchRoutes(origin, dest), 800);
    // }
  };

  return (
    <div style={{ position: "fixed", inset: 0, overflow: "hidden" }}>

      {/* ── Full screen map ── */}
      <MapContainer
        center={IIT_BOMBAY_CENTER}
        zoom={15}
        style={{
          position: "absolute",
          inset: 0,
          cursor: clickMode ? "crosshair" : "grab",
        }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="© OpenStreetMap contributors"
        />
        <MapClickHandler onMapClick={handleMapClick} mode={clickMode} />

        {routes && (
          <>
            <Polyline
              positions={routes.fast_route}
              color="#f97316"
              weight={6}
              opacity={0.85}
              eventHandlers={{
                click: () =>
                  setRouteInfo({
                    title: "⚡ Fast Route",
                    body: "Shortest path by distance. May include poorly-lit segments and isolated stretches. Higher risk after dark.",
                  }),
              }}
            />
            <Polyline
              positions={safeRouteOverride || routes.safe_route}
              color="#16a34a"
              weight={6}
              opacity={0.9}
              eventHandlers={{
                click: () =>
                  setRouteInfo({
                    title: "🛡 Safe Route",
                    body: "Optimised for safety. Prioritises well-lit roads, security post proximity, and low incident history.",
                  }),
              }}
            />
          </>
        )}

        {origin && (
          <Marker position={[origin.lat, origin.lon]} icon={originIcon}>
            <Popup><b className="text-blue-700">📍 Origin</b></Popup>
          </Marker>
        )}
        {dest && (
          <Marker position={[dest.lat, dest.lon]} icon={destIcon}>
            <Popup><b className="text-green-700">🏁 Destination</b></Popup>
          </Marker>
        )}

        {incidentMarkers.map((m) => (
          <React.Fragment key={m.id}>
            <Circle
              center={[m.lat, m.lon]}
              radius={150}
              color="#dc2626"
              fillColor="#dc2626"
              fillOpacity={0.2}
              weight={2}
            />
            <Marker position={[m.lat, m.lon]} icon={incidentIcon}>
              <Popup><b className="text-orange-700">⚠️ Incident reported here</b></Popup>
            </Marker>
          </React.Fragment>
        ))}
      </MapContainer>

      {/* ── Top-left controls — fixed height, never overflows ── */}
      <div style={{
        position: "fixed",
        top: 12,
        left: 12,
        zIndex: 1000,
        width: 220,
        display: "flex",
        flexDirection: "column",
        gap: 6,
      }}>
        {/* Click mode banner */}
        {clickMode && (
          <div style={{
            background: "#2563eb",
            color: "white",
            padding: "6px 10px",
            borderRadius: 8,
            fontSize: 11,
            fontWeight: 700,
            textAlign: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
          }}>
            {clickMode === "origin"   && "📍 Click map to set Origin"}
            {clickMode === "dest"     && "🏁 Click map to set Destination"}
            {clickMode === "incident" && "⚠️ Click map to mark Incident"}
          </div>
        )}

        {/* Origin / Dest buttons */}
        <div style={{ display: "flex", gap: 6 }}>
          <button
            onClick={() => setClickMode("origin")}
            style={{
              flex: 1,
              padding: "7px 4px",
              borderRadius: 8,
              fontSize: 11,
              fontWeight: 700,
              cursor: "pointer",
              border: "2px solid #2563eb",
              background: clickMode === "origin" ? "#2563eb" : "white",
              color: clickMode === "origin" ? "white" : "#1d4ed8",
              boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
            }}
          >
            📍 Set Origin
          </button>
          <button
            onClick={() => setClickMode("dest")}
            style={{
              flex: 1,
              padding: "7px 4px",
              borderRadius: 8,
              fontSize: 11,
              fontWeight: 700,
              cursor: "pointer",
              border: "2px solid #16a34a",
              background: clickMode === "dest" ? "#16a34a" : "white",
              color: clickMode === "dest" ? "white" : "#15803d",
              boxShadow: "0 1px 4px rgba(0,0,0,0.15)",
            }}
          >
            🏁 Set Dest
          </button>
        </div>

        {/* Coordinate chips — only show if set */}
        {origin && (
          <div style={{
            background: "white",
            fontSize: 10,
            padding: "4px 8px",
            borderRadius: 6,
            borderLeft: "4px solid #2563eb",
            boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
            color: "#1d4ed8",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}>
            From: {origin.lat.toFixed(4)}, {origin.lon.toFixed(4)}
          </div>
        )}
        {dest && (
          <div style={{
            background: "white",
            fontSize: 10,
            padding: "4px 8px",
            borderRadius: 6,
            borderLeft: "4px solid #16a34a",
            boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
            color: "#15803d",
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}>
            To: {dest.lat.toFixed(4)}, {dest.lon.toFixed(4)}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{
            background: "white",
            fontSize: 11,
            padding: "6px 10px",
            borderRadius: 8,
            color: "#ea580c",
            fontWeight: 600,
            textAlign: "center",
            boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
          }}>
            ⏳ Computing routes...
          </div>
        )}
      </div>

      {/* ── Alert banner — top center ── */}
      {alertZones.length > 0 && (
        <div style={{
          position: "fixed",
          top: 12,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1000,
          background: "#dc2626",
          color: "white",
          padding: "10px 18px",
          borderRadius: 12,
          boxShadow: "0 4px 16px rgba(0,0,0,0.3)",
          display: "flex",
          alignItems: "center",
          gap: 10,
          maxWidth: 360,
        }}>
          <span style={{ fontSize: 18 }}>🔴</span>
          <div>
            <p style={{ fontWeight: 700, fontSize: 13, lineHeight: 1.3 }}>
              Safety Alert — {alertZones.length} zone{alertZones.length > 1 ? "s" : ""} flagged
            </p>
            <p style={{ fontSize: 11, opacity: 0.9 }}>
              Safe route updated to avoid flagged areas
            </p>
          </div>
          <button
            onClick={() => setAlertZones([])}
            style={{
              marginLeft: 6,
              background: "none",
              border: "none",
              color: "white",
              fontSize: 18,
              cursor: "pointer",
              opacity: 0.8,
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>
      )}

      {/* ── Route panel — top right ── */}
      <div style={{
        position: "fixed",
        top: 12,
        right: 12,
        zIndex: 1000,
      }}>
        <RoutePanel data={routeData} alertZones={alertZones} fastRoute={routes?.fast_route} />
      </div>

      {/* ── Route info popup — bottom center ── */}
      {routeInfo && (
        <div style={{
          position: "fixed",
          bottom: 180,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1000,
          background: "#111827",
          color: "white",
          padding: "12px 20px",
          borderRadius: 12,
          boxShadow: "0 4px 16px rgba(0,0,0,0.4)",
          fontSize: 13,
          maxWidth: 300,
          textAlign: "center",
        }}>
          <p style={{ fontWeight: 700, marginBottom: 4 }}>{routeInfo.title}</p>
          <p style={{ fontSize: 11, opacity: 0.8 }}>{routeInfo.body}</p>
          <button
            onClick={() => setRouteInfo(null)}
            style={{
              marginTop: 8,
              fontSize: 11,
              background: "none",
              border: "none",
              color: "white",
              opacity: 0.7,
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ── Incident form — bottom left ── */}
      <div style={{
        position: "fixed",
        bottom: 12,
        left: 12,
        zIndex: 1000,
      }}>
        <IncidentForm
          incidentLocation={incidentLocation}
          onRequestLocationPick={() => setClickMode("incident")}
          onAlert={handleAlert}
          onReroute={handleReroute}
          onSubmitted={handleIncidentSubmitted}
          origin={origin}
          dest={dest}
        />
      </div>
    </div>
  );
}