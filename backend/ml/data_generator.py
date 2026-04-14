"""
Synthetic data generator for training ML models.
Generates realistic-looking data that matches the ERP domain.
"""
import numpy as np
import pandas as pd


def generate_attrition_data(n: int = 500) -> pd.DataFrame:
    """
    Generate synthetic employee attrition dataset.

    Features: salary, tenure_years, performance_rating, department_encoded,
              overtime_hours, satisfaction_score, num_projects
    Target:   will_leave (0 or 1)
    """
    np.random.seed(42)
    salary = np.random.normal(65000, 20000, n).clip(30000, 150000)
    tenure = np.random.exponential(3, n).clip(0.5, 20)
    performance = np.random.uniform(1, 5, n)
    department = np.random.randint(0, 6, n)  # 0-5 encoded departments
    overtime = np.random.normal(5, 3, n).clip(0, 20)
    satisfaction = np.random.uniform(1, 5, n)
    num_projects = np.random.randint(1, 8, n)

    # Attrition logic: low salary + low satisfaction + high overtime = higher risk
    attrition_score = (
        (150000 - salary) / 150000 * 0.3
        + (5 - satisfaction) / 5 * 0.25
        + overtime / 20 * 0.2
        + (5 - performance) / 5 * 0.15
        + (1 / (tenure + 1)) * 0.1
    )
    noise = np.random.normal(0, 0.1, n)
    will_leave = (attrition_score + noise > 0.45).astype(int)

    return pd.DataFrame({
        "salary": salary.round(2),
        "tenure_years": tenure.round(2),
        "performance_rating": performance.round(2),
        "department_encoded": department,
        "overtime_hours": overtime.round(2),
        "satisfaction_score": satisfaction.round(2),
        "num_projects": num_projects,
        "will_leave": will_leave,
    })


def generate_revenue_data(n: int = 120) -> pd.DataFrame:
    """
    Generate synthetic monthly revenue dataset (10 years × 12 months).

    Features: month, prev_revenue, total_expenses, headcount, marketing_spend
    Target:   revenue
    """
    np.random.seed(42)
    months = np.tile(np.arange(1, 13), n // 12 + 1)[:n]
    base_revenue = 50000
    revenues = []
    prev_rev = base_revenue

    for i in range(n):
        seasonality = 1 + 0.15 * np.sin(2 * np.pi * months[i] / 12)
        growth = 1 + 0.005 * i  # gradual growth
        noise = np.random.normal(1, 0.05)
        rev = prev_rev * seasonality * growth * noise
        revenues.append(rev)
        prev_rev = rev

    revenues = np.array(revenues)
    expenses = revenues * np.random.uniform(0.4, 0.7, n)
    headcount = (np.linspace(10, 60, n) + np.random.normal(0, 2, n)).clip(5, 100).astype(int)
    marketing = revenues * np.random.uniform(0.05, 0.15, n)

    return pd.DataFrame({
        "month": months,
        "prev_revenue": np.roll(revenues, 1).round(2),
        "total_expenses": expenses.round(2),
        "headcount": headcount,
        "marketing_spend": marketing.round(2),
        "revenue": revenues.round(2),
    })


def generate_churn_data(n: int = 600) -> pd.DataFrame:
    """
    Generate synthetic customer churn dataset.

    Features: purchase_frequency, last_purchase_days, lifetime_value,
              support_tickets, avg_order_value, account_age_months
    Target:   will_churn (0 or 1)
    """
    np.random.seed(42)
    purchase_freq = np.random.poisson(5, n).clip(0, 30)
    last_purchase = np.random.exponential(30, n).clip(1, 365)
    ltv = np.random.lognormal(8, 1, n).clip(100, 100000)
    support_tickets = np.random.poisson(2, n)
    avg_order = ltv / (purchase_freq + 1)
    account_age = np.random.uniform(1, 60, n)

    # Churn logic: high last_purchase_days + low frequency + many tickets = churn
    churn_score = (
        last_purchase / 365 * 0.35
        + (30 - purchase_freq) / 30 * 0.25
        + support_tickets / 10 * 0.2
        + (60 - account_age) / 60 * 0.1
        + (100000 - ltv) / 100000 * 0.1
    )
    noise = np.random.normal(0, 0.08, n)
    will_churn = (churn_score + noise > 0.5).astype(int)

    return pd.DataFrame({
        "purchase_frequency": purchase_freq,
        "last_purchase_days": last_purchase.round(1),
        "lifetime_value": ltv.round(2),
        "support_tickets": support_tickets,
        "avg_order_value": avg_order.round(2),
        "account_age_months": account_age.round(1),
        "will_churn": will_churn,
    })


def generate_project_risk_data(n: int = 400) -> pd.DataFrame:
    """
    Generate synthetic project risk dataset.

    Features: budget_usage_pct, task_completion_pct, days_remaining,
              team_size, scope_changes, complexity_score
    Target:   risk_level (0=low, 1=medium, 2=high)
    """
    np.random.seed(42)
    budget_usage = np.random.uniform(0, 150, n)  # can exceed 100%
    task_completion = np.random.uniform(0, 100, n)
    days_remaining = np.random.exponential(30, n).clip(0, 180)
    team_size = np.random.randint(2, 20, n)
    scope_changes = np.random.poisson(2, n)
    complexity = np.random.uniform(1, 10, n)

    # Risk logic
    risk_score = (
        budget_usage / 150 * 0.25
        + (100 - task_completion) / 100 * 0.25
        + (1 / (days_remaining + 1)) * 30 * 0.2
        + scope_changes / 10 * 0.15
        + complexity / 10 * 0.15
    )
    risk_level = np.where(risk_score < 0.35, 0, np.where(risk_score < 0.6, 1, 2))

    return pd.DataFrame({
        "budget_usage_pct": budget_usage.round(2),
        "task_completion_pct": task_completion.round(2),
        "days_remaining": days_remaining.round(0).astype(int),
        "team_size": team_size,
        "scope_changes": scope_changes,
        "complexity_score": complexity.round(2),
        "risk_level": risk_level,
    })
