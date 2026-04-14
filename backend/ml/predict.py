"""
ML Prediction Service — loads saved models and exposes prediction functions.
Also provides a FastAPI router for prediction endpoints.
"""
import os
import joblib
import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from config import ML_MODELS_DIR

router = APIRouter(prefix="/api/ml", tags=["ML Predictions"])


# ─── Model Cache ─────────────────────────────────────────────────────────────
_model_cache: dict = {}


def _load_model(name: str):
    """Load a model from disk, with caching."""
    if name not in _model_cache:
        path = os.path.join(ML_MODELS_DIR, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model '{name}' not found at {path}. Run training first.")
        _model_cache[name] = joblib.load(path)
    return _model_cache[name]


def reload_models():
    """Clear cache and reload all models."""
    _model_cache.clear()
    for name in ["attrition_model", "revenue_model", "churn_model", "project_risk_model"]:
        try:
            _load_model(name)
        except FileNotFoundError:
            pass


# ─── Request / Response Schemas ──────────────────────────────────────────────
class AttritionInput(BaseModel):
    salary: float = Field(..., gt=0, description="Annual salary")
    tenure_years: float = Field(..., ge=0)
    performance_rating: float = Field(..., ge=1, le=5)
    department_encoded: int = Field(..., ge=0, le=5)
    overtime_hours: float = Field(..., ge=0)
    satisfaction_score: float = Field(..., ge=1, le=5)
    num_projects: int = Field(..., ge=1)


class RevenueInput(BaseModel):
    month: int = Field(..., ge=1, le=12)
    prev_revenue: float = Field(..., gt=0)
    total_expenses: float = Field(..., ge=0)
    headcount: int = Field(..., ge=1)
    marketing_spend: float = Field(..., ge=0)


class ChurnInput(BaseModel):
    purchase_frequency: int = Field(..., ge=0)
    last_purchase_days: float = Field(..., ge=0)
    lifetime_value: float = Field(..., ge=0)
    support_tickets: int = Field(..., ge=0)
    avg_order_value: float = Field(..., ge=0)
    account_age_months: float = Field(..., ge=0)


class ProjectRiskInput(BaseModel):
    budget_usage_pct: float = Field(..., ge=0)
    task_completion_pct: float = Field(..., ge=0, le=100)
    days_remaining: int = Field(..., ge=0)
    team_size: int = Field(..., ge=1)
    scope_changes: int = Field(..., ge=0)
    complexity_score: float = Field(..., ge=1, le=10)


class PredictionResponse(BaseModel):
    prediction: str
    confidence: Optional[float] = None
    details: Optional[dict] = None


# ─── Prediction Functions ────────────────────────────────────────────────────
def predict_attrition(data: AttritionInput) -> dict:
    bundle = _load_model("attrition_model")
    features = np.array([[
        data.salary, data.tenure_years, data.performance_rating,
        data.department_encoded, data.overtime_hours,
        data.satisfaction_score, data.num_projects,
    ]])
    scaled = bundle["scaler"].transform(features)
    prediction = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    return {
        "prediction": "High Risk" if prediction == 1 else "Low Risk",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {
            "stay_probability": round(float(proba[0]) * 100, 1),
            "leave_probability": round(float(proba[1]) * 100, 1),
        },
    }


def predict_revenue(data: RevenueInput) -> dict:
    bundle = _load_model("revenue_model")
    features = np.array([[
        data.month, data.prev_revenue, data.total_expenses,
        data.headcount, data.marketing_spend,
    ]])
    scaled = bundle["scaler"].transform(features)
    prediction = bundle["model"].predict(scaled)[0]
    return {
        "prediction": f"${prediction:,.2f}",
        "confidence": None,
        "details": {
            "forecasted_revenue": round(float(prediction), 2),
            "input_prev_revenue": data.prev_revenue,
            "growth_pct": round((prediction - data.prev_revenue) / data.prev_revenue * 100, 1)
            if data.prev_revenue > 0 else 0,
        },
    }


def predict_churn(data: ChurnInput) -> dict:
    bundle = _load_model("churn_model")
    features = np.array([[
        data.purchase_frequency, data.last_purchase_days,
        data.lifetime_value, data.support_tickets,
        data.avg_order_value, data.account_age_months,
    ]])
    scaled = bundle["scaler"].transform(features)
    prediction = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    return {
        "prediction": "Will Churn" if prediction == 1 else "Will Retain",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {
            "retain_probability": round(float(proba[0]) * 100, 1),
            "churn_probability": round(float(proba[1]) * 100, 1),
        },
    }


def predict_project_risk(data: ProjectRiskInput) -> dict:
    bundle = _load_model("project_risk_model")
    features = np.array([[
        data.budget_usage_pct, data.task_completion_pct,
        data.days_remaining, data.team_size,
        data.scope_changes, data.complexity_score,
    ]])
    scaled = bundle["scaler"].transform(features)
    prediction = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    risk_labels = ["Low", "Medium", "High"]
    return {
        "prediction": f"{risk_labels[prediction]} Risk",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {
            "low_risk_pct": round(float(proba[0]) * 100, 1),
            "medium_risk_pct": round(float(proba[1]) * 100, 1),
            "high_risk_pct": round(float(proba[2]) * 100, 1),
        },
    }


# ─── API Endpoints ───────────────────────────────────────────────────────────
@router.post("/predict/attrition", response_model=PredictionResponse)
def api_predict_attrition(data: AttritionInput):
    """Predict employee attrition risk."""
    try:
        return predict_attrition(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict/revenue", response_model=PredictionResponse)
def api_predict_revenue(data: RevenueInput):
    """Forecast next month's revenue."""
    try:
        return predict_revenue(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict/churn", response_model=PredictionResponse)
def api_predict_churn(data: ChurnInput):
    """Predict customer churn risk."""
    try:
        return predict_churn(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/predict/project-risk", response_model=PredictionResponse)
def api_predict_project_risk(data: ProjectRiskInput):
    """Assess project risk level."""
    try:
        return predict_project_risk(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/train")
def api_train_models():
    """Retrain all ML models (admin endpoint)."""
    try:
        from ml.train import train_all
        results = train_all()
        reload_models()
        return {"status": "success", "metrics": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
