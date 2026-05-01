"""
AI Insights Router — generates real-time business intelligence
by comparing actual data across all ERP modules.
NO hardcoded messages. Everything is computed from database.

Includes:
- Actionable insights (cause + impact + recommended action)
- Executive summary (one-sentence business health statement)
- Business health score (0-100 composite gauge)
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
from models.hcm import Employee, Attendance
from models.procurement import InventoryItem
from models.ppm import Project

router = APIRouter(prefix="/api/insights", tags=["AI Insights"])
logger = logging.getLogger("erp.insights")

# ── Cache ────────────────────────────────────────────────────────────────────
_cache = {"data": None, "expires": 0}
CACHE_TTL = 60


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round((current - previous) / abs(previous) * 100, 1)


def _severity(pct: float) -> str:
    mag = abs(pct)
    if mag >= 20:
        return "high"
    if mag >= 10:
        return "medium"
    return "low"


def _compute_insights(db: Session) -> list[dict]:
    """Generate actionable insights from real cross-module data."""
    insights = []
    today = date.today()

    # ── 1. Revenue Trend ─────────────────────────────────────────────────
    try:
        last_7_start = today - timedelta(days=7)
        prev_7_start = today - timedelta(days=14)

        rev_last_7 = float(
            db.query(func.coalesce(func.sum(Revenue.amount), 0))
            .filter(Revenue.date >= last_7_start, Revenue.date < today)
            .scalar()
        )
        rev_prev_7 = float(
            db.query(func.coalesce(func.sum(Revenue.amount), 0))
            .filter(Revenue.date >= prev_7_start, Revenue.date < last_7_start)
            .scalar()
        )

        if rev_last_7 == 0 and rev_prev_7 == 0:
            cm, cy = today.month, today.year
            pm = cm - 1 if cm > 1 else 12
            py = cy if cm > 1 else cy - 1
            rev_last_7 = float(
                db.query(func.coalesce(func.sum(Revenue.amount), 0))
                .filter(func.extract("month", Revenue.date) == cm,
                        func.extract("year", Revenue.date) == cy).scalar()
            )
            rev_prev_7 = float(
                db.query(func.coalesce(func.sum(Revenue.amount), 0))
                .filter(func.extract("month", Revenue.date) == pm,
                        func.extract("year", Revenue.date) == py).scalar()
            )
            period = "this month vs last month"
        else:
            period = "last 7 days vs previous 7 days"

        if rev_prev_7 > 0 or rev_last_7 > 0:
            rev_change = _pct_change(rev_last_7, rev_prev_7)
            if abs(rev_change) >= 5:
                if rev_change < 0:
                    insights.append({
                        "title": "Revenue Decline",
                        "description": f"Revenue dropped {abs(rev_change)}% {period} — this reduces your profit margins and cash reserves. Focus on boosting sales or adjusting pricing.",
                        "severity": _severity(rev_change),
                        "module": "finance",
                    })
                else:
                    insights.append({
                        "title": "Revenue Growth",
                        "description": f"Revenue grew {abs(rev_change)}% {period} — good trajectory. Keep investing in the channels that are working.",
                        "severity": "low",
                        "module": "finance",
                    })
    except Exception as e:
        logger.warning(f"Insights: revenue analysis failed: {e}")

    # ── 2. Expense Growth ────────────────────────────────────────────────
    try:
        cm, cy = today.month, today.year
        pm = cm - 1 if cm > 1 else 12
        py = cy if cm > 1 else cy - 1

        exp_current = float(
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(func.extract("month", Expense.date) == cm,
                    func.extract("year", Expense.date) == cy).scalar()
        )
        exp_prev = float(
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(func.extract("month", Expense.date) == pm,
                    func.extract("year", Expense.date) == py).scalar()
        )

        if exp_prev > 0 or exp_current > 0:
            exp_change = _pct_change(exp_current, exp_prev)
            if abs(exp_change) >= 5:
                if exp_change > 0:
                    insights.append({
                        "title": f"Expense {'Surge' if exp_change > 15 else 'Increase'}",
                        "description": f"Expenses rose {abs(exp_change)}% vs last month — this eats into your margins. Audit your top cost categories and pause non-essential spending.",
                        "severity": _severity(exp_change),
                        "module": "finance",
                    })
                else:
                    insights.append({
                        "title": "Expense Reduction",
                        "description": f"Expenses dropped {abs(exp_change)}% vs last month — your cost discipline is paying off. Keep it up.",
                        "severity": "low",
                        "module": "finance",
                    })

        rev_current = float(
            db.query(func.coalesce(func.sum(Revenue.amount), 0))
            .filter(func.extract("month", Revenue.date) == cm,
                    func.extract("year", Revenue.date) == cy).scalar()
        )
        if exp_current > 0 and rev_current > 0 and exp_current > rev_current:
            ratio = round(exp_current / rev_current * 100, 1)
            insights.append({
                "title": "Spending Exceeds Income",
                "description": f"You're spending {ratio}% of your revenue — the business is operating at a loss. Cut costs immediately or accelerate sales.",
                "severity": "high",
                "module": "finance",
            })
    except Exception as e:
        logger.warning(f"Insights: expense analysis failed: {e}")

    # ── 3. Employee Attendance ───────────────────────────────────────────
    try:
        last_30 = today - timedelta(days=30)
        prev_30 = today - timedelta(days=60)

        def absence_rate(start, end):
            total = db.query(Attendance).filter(
                Attendance.date >= start, Attendance.date < end).count()
            absent = db.query(Attendance).filter(
                Attendance.date >= start, Attendance.date < end,
                Attendance.status == "absent").count()
            return (absent / total * 100) if total > 0 else 0

        rate_recent = absence_rate(last_30, today)
        rate_prev = absence_rate(prev_30, last_30)

        if rate_recent > 5:
            change = round(rate_recent - rate_prev, 1)
            sev = "high" if rate_recent > 15 else "medium" if rate_recent > 8 else "low"
            insights.append({
                "title": "Absenteeism Rising",
                "description": f"Absence rate is {round(rate_recent, 1)}% — this hurts team productivity. Look into workload, morale, or burnout and address root causes.",
                "severity": sev,
                "module": "hcm",
            })
    except Exception as e:
        logger.warning(f"Insights: attendance analysis failed: {e}")

    # ── 4. Inventory Stockout Risk ───────────────────────────────────────
    try:
        low_stock = (
            db.query(InventoryItem)
            .filter(InventoryItem.quantity <= InventoryItem.reorder_level)
            .all()
        )
        if low_stock:
            names = [f"{item.name}" for item in low_stock[:3]]
            insights.append({
                "title": "Low Inventory",
                "description": f"{len(low_stock)} item(s) below reorder level ({', '.join(names)}) — this could disrupt operations. Reorder within 2 days.",
                "severity": "high" if len(low_stock) >= 3 else "medium",
                "module": "procurement",
            })
    except Exception as e:
        logger.warning(f"Insights: inventory analysis failed: {e}")

    # ── 5. Delayed Projects ──────────────────────────────────────────────
    try:
        delayed = db.query(Project).filter(Project.status == "delayed").count()
        overbudget = (
            db.query(Project)
            .filter(Project.spent > Project.budget, Project.status != "completed")
            .count()
        )
        if delayed > 0:
            insights.append({
                "title": "Project Delays",
                "description": f"{delayed} project(s) past deadline — client satisfaction is at risk. Reassign resources or renegotiate timelines now.",
                "severity": "high" if delayed >= 3 else "medium",
                "module": "ppm",
            })
        if overbudget > 0:
            insights.append({
                "title": "Budget Overrun",
                "description": f"{overbudget} project(s) over budget — this erodes margins. Freeze scope changes and review costs immediately.",
                "severity": "high",
                "module": "ppm",
            })
    except Exception as e:
        logger.warning(f"Insights: project analysis failed: {e}")

    severity_order = {"high": 0, "medium": 1, "low": 2}
    insights.sort(key=lambda x: severity_order.get(x["severity"], 3))
    return insights


def _compute_health_score(db: Session, insights: list[dict]) -> dict:
    """Compute a 0-100 business health score from real metrics."""
    score = 100
    signals = []

    # Deduct for high/medium severity insights
    high_count = sum(1 for i in insights if i["severity"] == "high")
    med_count = sum(1 for i in insights if i["severity"] == "medium")
    score -= high_count * 15
    score -= med_count * 7

    # Revenue health
    try:
        today = date.today()
        cm, cy = today.month, today.year
        rev = float(
            db.query(func.coalesce(func.sum(Revenue.amount), 0))
            .filter(func.extract("month", Revenue.date) == cm,
                    func.extract("year", Revenue.date) == cy).scalar()
        )
        exp = float(
            db.query(func.coalesce(func.sum(Expense.amount), 0))
            .filter(func.extract("month", Expense.date) == cm,
                    func.extract("year", Expense.date) == cy).scalar()
        )
        if rev > 0 and exp > 0:
            margin = (rev - exp) / rev * 100
            if margin > 20:
                signals.append("Strong profit margins")
            elif margin > 0:
                signals.append("Positive but thin margins")
                score -= 5
            else:
                signals.append("Operating at a loss")
                score -= 15
    except Exception:
        pass

    # Project health
    try:
        total_proj = db.query(Project).filter(Project.status != "completed").count()
        delayed_proj = db.query(Project).filter(Project.status == "delayed").count()
        if total_proj > 0:
            delay_rate = delayed_proj / total_proj * 100
            if delay_rate > 40:
                signals.append("Most projects behind schedule")
                score -= 10
            elif delay_rate == 0:
                signals.append("All projects on track")
    except Exception:
        pass

    score = max(0, min(100, score))
    if score >= 75:
        status = "healthy"
    elif score >= 50:
        status = "caution"
    else:
        status = "critical"

    return {"score": score, "status": status, "signals": signals}


def _generate_executive_summary(insights: list[dict], health: dict) -> dict:
    """Generate structured executive summary: status, biggest risk, action."""
    high_count = sum(1 for i in insights if i["severity"] == "high")
    med_count = sum(1 for i in insights if i["severity"] == "medium")
    highs = [i for i in insights if i["severity"] == "high"]

    if high_count == 0 and med_count == 0:
        return {
            "status": "Stable",
            "risk": "No critical issues detected.",
            "action": "Continue monitoring. Operations are running smoothly.",
        }
    if high_count == 0:
        return {
            "status": "Stable",
            "risk": f"{med_count} area(s) need minor attention.",
            "action": "Review flagged insights and address before they escalate.",
        }
    top = highs[0]
    if high_count == 1:
        return {
            "status": "Warning",
            "risk": top["title"],
            "action": top["description"].split(" — ")[-1].split(".")[0] + "." if " — " in top["description"] else "Take immediate action.",
        }
    return {
        "status": "Critical" if high_count > 3 else "Warning",
        "risk": f"{high_count} critical issues: {', '.join(i['title'].lower() for i in highs[:3])}.",
        "action": "Prioritize these immediately to protect margins and operations.",
    }


@router.get("/summary")
def get_insights_summary(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Generate AI-powered business insights with actions, health score, and executive summary."""
    now = time.time()
    if _cache["data"] and now < _cache["expires"]:
        return _cache["data"]

    insights = _compute_insights(db)
    health = _compute_health_score(db, insights)
    executive_summary = _generate_executive_summary(insights, health)

    result = {
        "insights": insights,
        "health": health,
        "executive_summary": executive_summary,
        "generated_at": now,
    }
    _cache["data"] = result
    _cache["expires"] = now + CACHE_TTL
    return result
