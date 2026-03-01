"""
Evaluate Model for SafeCompanion
Evaluates trained ML models performance
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


def load_model(model_path):
    """Load a saved model"""
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        print(f"Model not found: {model_path}")
        return None


def evaluate_safety_model():
    """Evaluate safety scoring model"""
    print("=" * 50)
    print("Evaluating Safety Model")
    print("=" * 50)
    
    # Load model and scaler
    model = load_model('ml/saved_models/safety_model.pkl')
    scaler = load_model('ml/saved_models/safety_scaler.pkl')
    
    if model is None or scaler is None:
        print("Please run train_model.py first")
        return
    
    # Load test data
    try:
        df = pd.read_csv('ml/data/routes.csv')
    except FileNotFoundError:
        print("No test data found")
        return
    
    # Prepare features
    X = df[['latitude', 'longitude', 'distance_m']].copy()
    y_true = df['safety_score']
    
    # Scale and predict
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    
    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    
    print(f"Mean Absolute Error: {mae:.4f}")
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"Root Mean Squared Error: {rmse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        print("\nFeature Importances:")
        features = ['latitude', 'longitude', 'distance_m']
        for feat, imp in zip(features, model.feature_importances_):
            print(f"  {feat}: {imp:.4f}")


def evaluate_incident_classifier():
    """Evaluate incident classifier"""
    print("\n" + "=" * 50)
    print("Evaluating Incident Classifier")
    print("=" * 50)
    
    # Load model
    model = load_model('ml/saved_models/incident_classifier.pkl')
    
    if model is None:
        print("Please run train_model.py first")
        return
    
    # Load test data
    try:
        df = pd.read_csv('ml/data/incidents.csv')
    except FileNotFoundError:
        print("No test data found")
        return
    
    # Prepare data
    severity_map = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
    df['severity_encoded'] = df['severity'].map(severity_map)
    
    X = df[['latitude', 'longitude']]
    y_true = df['severity_encoded']
    
    # Predict
    y_pred = model.predict(X)
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, 
                                target_names=['low', 'medium', 'high', 'critical']))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))


def main():
    """Main evaluation function"""
    print("SafeCompanion Model Evaluation")
    print("=" * 50)
    
    evaluate_safety_model()
    evaluate_incident_classifier()
    
    print("\n" + "=" * 50)
    print("Evaluation complete!")


if __name__ == "__main__":
    main()
