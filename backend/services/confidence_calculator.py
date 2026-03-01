import numpy as np
from datetime import datetime

MAX_REPORTS = 50

def calculate_confidence(total_reports, last_report_time=None):
    if total_reports == 0:
        return 0.1
    
    density_factor = (
        np.log(1 + total_reports) /
        np.log(1 + MAX_REPORTS)
    )
    
    if last_report_time:
        last = datetime.fromisoformat(last_report_time)
        hours_ago = (datetime.utcnow() - last).total_seconds() / 3600
        recency_factor = np.exp(-hours_ago / 48)
    else:
        recency_factor = 0.5
    
    confidence = density_factor * recency_factor
    return round(min(confidence, 1.0), 3)

def confidence_label(score):
    if score >= 0.7:
        return "High Data Confidence"
    elif score >= 0.4:
        return "Moderate Data Confidence"
    else:
        return "Low Data — Use Caution"