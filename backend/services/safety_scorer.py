import pickle
import numpy as np
import pandas as pd

model = None

FEATURES = [
    'lighting_score', 'incident_density', 'safe_stop_proximity',
    'time_sin', 'time_cos', 'day_sin', 'day_cos'
]

def load_model():
    global model
    with open("ml/saved_models/safety_rf_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("Safety model loaded.")

def score_segment(lighting, incident_density, safe_stop_proximity, hour, day):
    time_sin = np.sin(2 * np.pi * hour / 24)
    time_cos = np.cos(2 * np.pi * hour / 24)
    day_sin = np.sin(2 * np.pi * day / 7)
    day_cos = np.cos(2 * np.pi * day / 7)

    df = pd.DataFrame([[
        lighting, incident_density, safe_stop_proximity,
        time_sin, time_cos, day_sin, day_cos
    ]], columns=FEATURES)

    prob = model.predict_proba(df)[0][1]
    return max(prob, 0.01)