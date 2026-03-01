import pandas as pd
import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    confusion_matrix, classification_report, ConfusionMatrixDisplay
)

os.makedirs("ml/saved_models", exist_ok=True)

FEATURES = [
    'lighting_score', 'incident_density', 'safe_stop_proximity',
    'time_sin', 'time_cos', 'day_sin', 'day_cos'
]

train = pd.read_csv("ml/data/synthetic_segments.csv")
val = pd.read_csv("ml/data/validation_split.csv")

X_train, y_train = train[FEATURES], train['safety_label']
X_val, y_val = val[FEATURES], val['safety_label']

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    n_jobs=-1,  # Use all CPU cores — important for AMD benchmark
    random_state=42
)

print("Training model...")
model.fit(X_train, y_train)

cv_scores = cross_val_score(model, X_train, y_train, cv=5)
print(f"CV Accuracy: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")

y_pred = model.predict(X_val)
print("\nClassification Report:")
print(classification_report(y_val, y_pred))

# Save confusion matrix
cm = confusion_matrix(y_val, y_pred)
disp = ConfusionMatrixDisplay(cm, display_labels=["Unsafe", "Safe"])
disp.plot(cmap='Blues')
plt.title("SafeCompanion Model — Confusion Matrix")
plt.tight_layout()
plt.savefig("ml/saved_models/confusion_matrix.png", dpi=150)
plt.close()
print("Confusion matrix saved.")

# Save feature importance
importances = pd.Series(model.feature_importances_, index=FEATURES)
importances.sort_values().plot(kind='barh', color='steelblue')
plt.title("SafeCompanion — Feature Importance")
plt.xlabel("Importance Score")
plt.tight_layout()
plt.savefig("ml/saved_models/feature_importance.png", dpi=150)
plt.close()
print("Feature importance chart saved.")

# Save model
with open("ml/saved_models/safety_rf_model.pkl", "wb") as f:
    pickle.dump(model, f)
print("Model saved to ml/saved_models/safety_rf_model.pkl")