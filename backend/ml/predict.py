"""
ML Prediction Service — loads saved models and exposes prediction functions.
Thread-safe lazy loading with locking to prevent cold-start failures.
Includes explainable AI: human-readable factors for each prediction.
"""
import os
import threading
import logging
import joblib
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from config import ML_MODELS_DIR
from auth.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/ml", tags=["ML Predictions"])
logger = logging.getLogger("erp.ml")

# ─── Thread-safe Model Cache ────────────────────────────────────────────────
_model_cache: dict = {}
_model_lock = threading.Lock()


def _load_model(name: str):
    """Load a model from disk with thread-safe locking."""
    if name in _model_cache:
        return _model_cache[name]
    with _model_lock:
        # Double-check after acquiring lock
        if name in _model_cache:
            return _model_cache[name]
        path = os.path.join(ML_MODELS_DIR, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model '{name}' not found. Run training first.")
        try:
            bundle = joblib.load(path)
            _model_cache[name] = bundle
            logger.info(f"[ML] Loaded model: {name}")
            return bundle
        except Exception as e:
            logger.error(f"[ML] Failed to load {name}: {e}")
            raise


def preload_models():
    """Pre-load all models at startup. Called from lifespan."""
    names = ["attrition_model", "revenue_model", "churn_model", "project_risk_model"]
    loaded = 0
    for name in names:
        try:
            _load_model(name)
            loaded += 1
        except Exception as e:
            logger.warning(f"[ML] Skipped {name}: {e}")
    logger.info(f"[ML] Pre-loaded {loaded}/{len(names)} models")


def reload_models():
    """Clear cache and reload all models."""
    with _model_lock:
        _model_cache.clear()
    preload_models()


# ─── Explainability Helpers ──────────────────────────────────────────────────
def _get_feature_factors(model_bundle, feature_names: list, feature_values: list, top_n: int = 3) -> list[str]:
    """Extract top contributing factors from a trained model."""
    model = model_bundle["model"]
    factors = []
    try:
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            for idx in indices:
                name = feature_names[idx].replace("_", " ").title()
                val = round(feature_values[idx], 1) if isinstance(feature_values[idx], float) else feature_values[idx]
                imp = round(importances[idx] * 100, 1)
                factors.append(f"{name}: {val} (impact: {imp}%)")
        elif hasattr(model, "coef_"):
            coefs = np.abs(model.coef_.flatten())
            indices = np.argsort(coefs)[::-1][:top_n]
            for idx in indices:
                name = feature_names[idx].replace("_", " ").title()
                val = round(feature_values[idx], 1) if isinstance(feature_values[idx], float) else feature_values[idx]
                factors.append(f"{name}: {val}")
    except Exception:
        pass
    if not factors:
        for name, val in zip(feature_names[:top_n], feature_values[:top_n]):
            readable = name.replace("_", " ").title()
            val = round(val, 1) if isinstance(val, float) else val
            factors.append(f"{readable}: {val}")
    return factors


# ─── Request / Response Schemas ──────────────────────────────────────────────
class AttritionInput(BaseModel):
    salary: float = Field(..., gt=0)
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
    factors: Optional[list[str]] = None


# ─── Prediction Functions ────────────────────────────────────────────────────
def predict_attrition(data: AttritionInput) -> dict:
    bundle = _load_model("attrition_model")
    names = ["salary", "tenure_years", "performance_rating", "department_encoded",
             "overtime_hours", "satisfaction_score", "num_projects"]
    vals = [data.salary, data.tenure_years, data.performance_rating,
            data.department_encoded, data.overtime_hours, data.satisfaction_score, data.num_projects]
    features = np.array([vals])
    scaled = bundle["scaler"].transform(features)
    pred = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    return {
        "prediction": "High Risk" if pred == 1 else "Low Risk",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {"stay_probability": round(float(proba[0]) * 100, 1), "leave_probability": round(float(proba[1]) * 100, 1)},
        "factors": _get_feature_factors(bundle, names, vals),
    }

def predict_revenue(data: RevenueInput) -> dict:
    bundle = _load_model("revenue_model")
    names = ["month", "prev_revenue", "total_expenses", "headcount", "marketing_spend"]
    vals = [data.month, data.prev_revenue, data.total_expenses, data.headcount, data.marketing_spend]
    features = np.array([vals])
    scaled = bundle["scaler"].transform(features)
    pred = bundle["model"].predict(scaled)[0]
    return {
        "prediction": f"${pred:,.2f}",
        "confidence": None,
        "details": {"forecasted_revenue": round(float(pred), 2), "input_prev_revenue": data.prev_revenue,
                     "growth_pct": round((pred - data.prev_revenue) / data.prev_revenue * 100, 1) if data.prev_revenue > 0 else 0},
        "factors": _get_feature_factors(bundle, names, vals),
    }

def predict_churn(data: ChurnInput) -> dict:
    bundle = _load_model("churn_model")
    names = ["purchase_frequency", "last_purchase_days", "lifetime_value", "support_tickets", "avg_order_value", "account_age_months"]
    vals = [data.purchase_frequency, data.last_purchase_days, data.lifetime_value, data.support_tickets, data.avg_order_value, data.account_age_months]
    features = np.array([vals])
    scaled = bundle["scaler"].transform(features)
    pred = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    return {
        "prediction": "Will Churn" if pred == 1 else "Will Retain",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {"retain_probability": round(float(proba[0]) * 100, 1), "churn_probability": round(float(proba[1]) * 100, 1)},
        "factors": _get_feature_factors(bundle, names, vals),
    }

def predict_project_risk(data: ProjectRiskInput) -> dict:
    bundle = _load_model("project_risk_model")
    names = ["budget_usage_pct", "task_completion_pct", "days_remaining", "team_size", "scope_changes", "complexity_score"]
    vals = [data.budget_usage_pct, data.task_completion_pct, data.days_remaining, data.team_size, data.scope_changes, data.complexity_score]
    features = np.array([vals])
    scaled = bundle["scaler"].transform(features)
    pred = bundle["model"].predict(scaled)[0]
    proba = bundle["model"].predict_proba(scaled)[0]
    risk_labels = ["Low", "Medium", "High"]
    return {
        "prediction": f"{risk_labels[pred]} Risk",
        "confidence": round(float(max(proba)) * 100, 1),
        "details": {"low_risk_pct": round(float(proba[0]) * 100, 1), "medium_risk_pct": round(float(proba[1]) * 100, 1), "high_risk_pct": round(float(proba[2]) * 100, 1)},
        "factors": _get_feature_factors(bundle, names, vals),
    }


# ─── API Endpoints ───────────────────────────────────────────────────────────
@router.post("/predict/attrition", response_model=PredictionResponse)
def api_predict_attrition(data: AttritionInput, user=Depends(get_current_user)):
    try:
        return predict_attrition(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/predict/revenue", response_model=PredictionResponse)
def api_predict_revenue(data: RevenueInput, user=Depends(get_current_user)):
    try:
        return predict_revenue(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/predict/churn", response_model=PredictionResponse)
def api_predict_churn(data: ChurnInput, user=Depends(get_current_user)):
    try:
        return predict_churn(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/predict/project-risk", response_model=PredictionResponse)
def api_predict_project_risk(data: ProjectRiskInput, user=Depends(get_current_user)):
    try:
        return predict_project_risk(data)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.post("/train")
def api_train_models(user=Depends(require_role("admin"))):
    try:
        from ml.train import train_all
        results = train_all()
        reload_models()
        return {"status": "success", "metrics": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
