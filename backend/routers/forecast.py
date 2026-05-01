"""
Forecast Router — ML-powered revenue predictions for the next 30 days.
Uses the existing trained revenue model + historical data.
"""
import time
import logging
from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth.dependencies import get_current_user
from models.finance import Revenue, Expense
from models.hcm import Employee

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])
logger = logging.getLogger("erp.forecast")

_cache = {"data": None, "expires": 0}
CACHE_TTL = 120


@router.get("/revenue")
def forecast_revenue(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Forecast daily revenue for the next 30 days using ML + historical trends."""
    now = time.time()
    if _cache["data"] and now < _cache["expires"]:
        return _cache["data"]

    today = date.today()

    # ── Get historical daily revenue (last 60 days) ──────────────────────
    past_start = today - timedelta(days=60)
    hist_rows = (
        db.query(Revenue.date, func.sum(Revenue.amount).label("total"))
        .filter(Revenue.date >= past_start, Revenue.date <= today)
        .group_by(Revenue.date)
        .order_by(Revenue.date)
        .all()
    )

    # Build date->amount map for past data
    hist_map = {r.date: float(r.total) for r in hist_rows}

    # Fill gaps: last 30 days of actual data
    past_dates = []
    past_values = []
    for i in range(30, 0, -1):
        d = today - timedelta(days=i)
        past_dates.append(d.isoformat())
        past_values.append(hist_map.get(d, 0))

    # ── Generate forecast (next 30 days) ─────────────────────────────────
    # Try ML model first, fall back to trend extrapolation
    forecast_dates = []
    forecast_values = []

    try:
        from ml.predict import _load_model
        bundle = _load_model("revenue_model")
        model = bundle["model"]
        scaler = bundle["scaler"]

        # Get context values for prediction
        total_expenses = float(
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(func.extract("month", Expense.date) == today.month,
                    func.extract("year", Expense.date) == today.year)
            .scalar()
        )
        headcount = db.query(Employee).filter(Employee.is_active == True).count()
        avg_daily = sum(past_values[-14:]) / max(1, sum(1 for v in past_values[-14:] if v > 0))

        import numpy as np
        import pandas as pd

        for i in range(1, 31):
            d = today + timedelta(days=i)
            month = d.month
            features = pd.DataFrame([[month, avg_daily, total_expenses / 30,
                                      headcount, total_expenses * 0.15]],
                                    columns=["month", "prev_revenue", "total_expenses",
                                             "headcount", "marketing_spend"])
            scaled = scaler.transform(features)
            pred = float(model.predict(scaled)[0])
            # Daily = monthly prediction / 30, with slight variance
            daily_pred = max(0, pred / 30 * (0.9 + 0.2 * (i % 7) / 7))
            forecast_dates.append(d.isoformat())
            forecast_values.append(round(daily_pred, 2))
            avg_daily = daily_pred  # feed forward

    except Exception as e:
        logger.warning(f"Forecast: ML prediction failed, using trend: {e}")
        # Fallback: simple moving average trend
        recent_avg = sum(past_values[-7:]) / max(1, sum(1 for v in past_values[-7:] if v > 0)) if any(past_values[-7:]) else 0
        for i in range(1, 31):
            d = today + timedelta(days=i)
            # Add slight growth trend + weekday variance
            growth = 1 + (0.002 * i)
            weekday_factor = 0.7 if d.weekday() >= 5 else 1.0
            pred = round(recent_avg * growth * weekday_factor, 2)
            forecast_dates.append(d.isoformat())
            forecast_values.append(pred)

    result = {
        "past": {"dates": past_dates, "values": past_values},
        "forecast": {"dates": forecast_dates, "values": forecast_values},
        "model": "ml" if forecast_values and forecast_values[0] > 0 else "trend",
    }

    _cache["data"] = result
    _cache["expires"] = now + CACHE_TTL
    return result
