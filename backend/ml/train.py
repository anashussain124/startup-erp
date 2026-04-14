"""
ML Training Pipeline — trains and saves all 4 models.

Models:
  1. Random Forest     → Employee attrition prediction
  2. Linear Regression → Revenue forecasting
  3. Decision Tree     → Customer churn prediction
  4. Gradient Boosted  → Project risk classification

Run this script to (re)train all models:
    python -m ml.train
"""
import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, r2_score, classification_report
from sklearn.preprocessing import StandardScaler

from ml.data_generator import (
    generate_attrition_data,
    generate_revenue_data,
    generate_churn_data,
    generate_project_risk_data,
)
from config import ML_MODELS_DIR


def ensure_models_dir():
    os.makedirs(ML_MODELS_DIR, exist_ok=True)


def train_attrition_model():
    """Train Random Forest for employee attrition prediction."""
    print("=" * 60)
    print("Training: Employee Attrition (Random Forest)")
    print("=" * 60)
    df = generate_attrition_data(500)
    X = df.drop("will_leave", axis=1)
    y = df["will_leave"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Stay", "Leave"]))

    # Save model + scaler
    joblib.dump({"model": model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(ML_MODELS_DIR, "attrition_model.pkl"))
    print("Saved: attrition_model.pkl\n")
    return acc


def train_revenue_model():
    """Train Linear Regression for revenue forecasting."""
    print("=" * 60)
    print("Training: Revenue Forecasting (Linear Regression)")
    print("=" * 60)
    df = generate_revenue_data(120)
    # Drop first row (prev_revenue is rolled)
    df = df.iloc[1:].reset_index(drop=True)
    X = df.drop("revenue", axis=1)
    y = df["revenue"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    print(f"R² Score: {r2:.4f}")
    print(f"Avg Prediction: ${np.mean(y_pred):,.2f}")
    print(f"Avg Actual:     ${np.mean(y_test):,.2f}\n")

    joblib.dump({"model": model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(ML_MODELS_DIR, "revenue_model.pkl"))
    print("Saved: revenue_model.pkl\n")
    return r2


def train_churn_model():
    """Train Decision Tree for customer churn prediction."""
    print("=" * 60)
    print("Training: Customer Churn (Decision Tree)")
    print("=" * 60)
    df = generate_churn_data(600)
    X = df.drop("will_churn", axis=1)
    y = df["will_churn"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = DecisionTreeClassifier(max_depth=8, min_samples_split=10, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Retain", "Churn"]))

    joblib.dump({"model": model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(ML_MODELS_DIR, "churn_model.pkl"))
    print("Saved: churn_model.pkl\n")
    return acc


def train_project_risk_model():
    """Train Gradient Boosting Classifier for project risk assessment."""
    print("=" * 60)
    print("Training: Project Risk (Gradient Boosting)")
    print("=" * 60)
    df = generate_project_risk_data(400)
    X = df.drop("risk_level", axis=1)
    y = df["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred, target_names=["Low", "Medium", "High"]))

    joblib.dump({"model": model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(ML_MODELS_DIR, "project_risk_model.pkl"))
    print("Saved: project_risk_model.pkl\n")
    return acc


def train_all():
    """Train all models and save to disk."""
    ensure_models_dir()
    print("\n🚀 Starting ML Training Pipeline\n")
    results = {
        "attrition": train_attrition_model(),
        "revenue": train_revenue_model(),
        "churn": train_churn_model(),
        "project_risk": train_project_risk_model(),
    }
    print("✅ All models trained and saved!")
    print(f"   Models directory: {ML_MODELS_DIR}")
    return results


if __name__ == "__main__":
    train_all()
