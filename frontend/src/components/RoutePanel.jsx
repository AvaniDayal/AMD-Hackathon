import { useMemo } from "react";

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const toRad = (x) => (x * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function routePassesThroughAlertZone(route, alertZones, radius = 160) {
  if (!route || !alertZones || alertZones.length === 0) return false;
  for (const coord of route) {
    for (const zone of alertZones) {
      if (haversine(coord[0], coord[1], zone.lat, zone.lon) <= radius) {
        return true;
      }
    }
  }
  return false;
}

function ConfidenceBar({ score }) {
  const label =
    score >= 70
      ? "✓ Well documented area"
      : score >= 30
      ? "~ Some community reports"
      : "○ New area — limited data";

  const color =
    score >= 70 ? "#4ade80" : score >= 30 ? "#facc15" : "#d1d5db";

  return (
    <div style={{ marginTop: 6 }}>
      <div style={{ background: "#e5e7eb", borderRadius: 4, height: 4, width: "100%" }}>
        <div
          style={{
            background: color,
            height: 4,
            borderRadius: 4,
            width: `${Math.max(score, 5)}%`,
            transition: "width 0.4s ease",
          }}
        />
      </div>
      <p style={{ fontSize: 10, color: "#6b7280", marginTop: 3 }}>{label}</p>
    </div>
  );
}

function RiskBadge({ score }) {
  const { label, bg, color } =
    score >= 70
      ? { label: "Low Risk", bg: "#dcfce7", color: "#15803d" }
      : score >= 50
      ? { label: "Moderate Risk", bg: "#fef9c3", color: "#854d0e" }
      : { label: "High Risk", bg: "#fee2e2", color: "#b91c1c" };

  return (
    <span
      style={{
        background: bg,
        color,
        fontSize: 10,
        fontWeight: 700,
        padding: "2px 7px",
        borderRadius: 20,
      }}
    >
      {label}
    </span>
  );
}

export default function RoutePanel({ data, alertZones = [], fastRoute = null }) {
  const fastRouteInDanger = useMemo(
    () => routePassesThroughAlertZone(fastRoute, alertZones),
    [fastRoute, alertZones]
  );

  if (!data) {
    return (
      <div
        style={{
          background: "white",
          borderRadius: 12,
          boxShadow: "0 2px 12px rgba(0,0,0,0.12)",
          padding: 14,
          width: 240,
          border: "1px solid #e5e7eb",
        }}
      >
        <p style={{ fontSize: 12, color: "#9ca3af", textAlign: "center" }}>
          Set origin &amp; destination to compare routes
        </p>
      </div>
    );
  }

  const {
    fast_safety_score: rawFastScore,
    safe_safety_score,
    fast_confidence,
    safe_confidence,
  } = data;

  // If fast route goes through danger zone, show penalised score
  const fast_safety_score = fastRouteInDanger
    ? Math.max(Math.round(rawFastScore * 0.55), 10)
    : rawFastScore;

  const scoreDiff = safe_safety_score - fast_safety_score;

  return (
    <div
      style={{
        background: "white",
        borderRadius: 12,
        boxShadow: "0 2px 12px rgba(0,0,0,0.15)",
        padding: 14,
        width: 248,
        border: "1px solid #e5e7eb",
      }}
    >
      <h2 style={{ fontSize: 13, fontWeight: 700, color: "#1f2937", marginBottom: 10 }}>
        Route Comparison
      </h2>

      {/* ── Fast Route ── */}
      <div
        style={{
          border: fastRouteInDanger ? "2px solid #dc2626" : "1px solid #fed7aa",
          borderRadius: 10,
          padding: 10,
          background: fastRouteInDanger ? "#fff1f2" : "#fff7ed",
          marginBottom: 10,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <span style={{ fontWeight: 700, fontSize: 12, color: "#c2410c" }}>⚡ Fast Route</span>
          <RiskBadge score={fast_safety_score} />
        </div>

        <p style={{ fontSize: 24, fontWeight: 800, color: "#ea580c", lineHeight: 1 }}>
          {fast_safety_score}
          <span style={{ fontSize: 12, fontWeight: 400, color: "#9ca3af" }}>/100</span>
        </p>

        <ConfidenceBar score={fast_confidence} />

        {/* Danger warning if route passes through alert zone */}
        {fastRouteInDanger && (
          <div
            style={{
              marginTop: 8,
              background: "#dc2626",
              color: "white",
              borderRadius: 6,
              padding: "5px 8px",
              fontSize: 10,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              gap: 5,
            }}
          >
            <span>🚨</span>
            <span>Passes through flagged zone — avoid this route</span>
          </div>
        )}
      </div>

      {/* ── Safe Route ── */}
      <div
        style={{
          border: "1px solid #bbf7d0",
          borderRadius: 10,
          padding: 10,
          background: "#f0fdf4",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <span style={{ fontWeight: 700, fontSize: 12, color: "#15803d" }}>🛡 Safe Route</span>
          <RiskBadge score={safe_safety_score} />
        </div>

        <p style={{ fontSize: 24, fontWeight: 800, color: "#16a34a", lineHeight: 1 }}>
          {safe_safety_score}
          <span style={{ fontSize: 12, fontWeight: 400, color: "#9ca3af" }}>/100</span>
        </p>

        <ConfidenceBar score={safe_confidence} />

        {fastRouteInDanger && (
          <div
            style={{
              marginTop: 8,
              background: "#16a34a",
              color: "white",
              borderRadius: 6,
              padding: "5px 8px",
              fontSize: 10,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              gap: 5,
            }}
          >
            <span>✓</span>
            <span>Recommended — avoids flagged areas</span>
          </div>
        )}
      </div>

      {/* Score difference */}
      <p
        style={{
          fontSize: 11,
          textAlign: "center",
          marginTop: 8,
          color: scoreDiff > 5 ? "#15803d" : "#9ca3af",
          fontWeight: scoreDiff > 5 ? 600 : 400,
        }}
      >
        {scoreDiff > 5
          ? `Safe route is ${scoreDiff} pts safer`
          : "Both routes have similar safety in this area"}
      </p>

      <p style={{ fontSize: 10, color: "#d1d5db", textAlign: "center", marginTop: 4 }}>
        Click a route on the map for details
      </p>
    </div>
  );
}