from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def check_convergence(incidents, radius_m=150, window_minutes=10):
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=window_minutes)
    
    recent = []
    for inc in incidents:
        try:
            ts = datetime.fromisoformat(inc['timestamp'])
            if ts > cutoff:
                recent.append(inc)
        except:
            continue
    
    for i, base in enumerate(recent):
        cluster = [base]
        for j, other in enumerate(recent):
            if i != j:
                dist = haversine(
                    base['lat'], base['lon'],
                    other['lat'], other['lon']
                )
                if dist <= radius_m:
                    cluster.append(other)
        
        if len(cluster) >= 1:
            avg_lat = sum(c['lat'] for c in cluster) / len(cluster)
            avg_lon = sum(c['lon'] for c in cluster) / len(cluster)
            return True, avg_lat, avg_lon
    
    return False, None, None