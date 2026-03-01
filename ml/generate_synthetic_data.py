import numpy as np
import pandas as pd
import os

os.makedirs("ml/data", exist_ok=True)
np.random.seed(42)
n = 5000

lighting = np.random.uniform(0, 1, n)
incident_density = np.random.uniform(0, 1, n)
safe_stop_proximity = np.random.uniform(0, 1, n)

hours = np.random.uniform(0, 24, n)
time_sin = np.sin(2 * np.pi * hours / 24)
time_cos = np.cos(2 * np.pi * hours / 24)

days = np.random.randint(0, 7, n)
day_sin = np.sin(2 * np.pi * days / 7)
day_cos = np.cos(2 * np.pi * days / 7)

# Deterministic safety rule
base = (
    lighting * 0.4 +
    (1 - incident_density) * 0.35 +
    safe_stop_proximity * 0.25
)

# Add realistic noise
noise = np.random.normal(0, 0.08, n)
final_score = base + noise
labels = (final_score > 0.55).astype(int)

# 8% label flip for realism
flip_mask = np.random.random(n) < 0.08
labels[flip_mask] = 1 - labels[flip_mask]

df = pd.DataFrame({
    'lighting_score': lighting,
    'incident_density': incident_density,
    'safe_stop_proximity': safe_stop_proximity,
    'time_sin': time_sin,
    'time_cos': time_cos,
    'day_sin': day_sin,
    'day_cos': day_cos,
    'safety_label': labels
})

train = df.sample(frac=0.8, random_state=42)
val = df.drop(train.index)

train.to_csv("ml/data/synthetic_segments.csv", index=False)
val.to_csv("ml/data/validation_split.csv", index=False)

print(f"Generated {n} rows. Train: {len(train)}, Val: {len(val)}")
print(f"Safe labels: {labels.sum()}, Unsafe: {n - labels.sum()}")