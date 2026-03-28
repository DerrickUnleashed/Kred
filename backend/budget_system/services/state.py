from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import statistics
import calendar

from budget_system.models.user import User
from budget_system.models.expense import Expense
from budget_system.models.planned import PlannedExpense

from budget_system.services.insights import impulsive_ratio, impulsive_streak
from budget_system.services.prediction import (
    predict_daily_overspend,
    predict_monthly_runout
)


def get_user_financial_state(user_id: int, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {}

    now = datetime.now(timezone.utc)
    today = now.date()

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id
    ).order_by(Expense.created_at).all()

    # Today
    today_expenses = [e for e in expenses if e.created_at.date() == today]
    spent_today = sum(e.amount for e in today_expenses)

    # Last 7 days
    week_ago = today - timedelta(days=7)
    week_expenses = [e for e in expenses if e.created_at.date() >= week_ago]
    spent_this_week = sum(e.amount for e in week_expenses)

    # Month total
    first_day_month = today.replace(day=1)
    month_expenses = [e for e in expenses if e.created_at.date() >= first_day_month]
    total_spent_month = sum(e.amount for e in month_expenses)

    monthly_income = getattr(user, "monthly_income", user.daily_limit * 30)
    savings_ratio = getattr(user, "savings_ratio", 0.2)

    usable_budget = monthly_income * (1 - savings_ratio)

    remaining_month_budget = max(usable_budget - total_spent_month, 0)

    weekly_budget = (usable_budget / 30) * 7
    weekly_remaining_budget = max(weekly_budget - spent_this_week, 0)

    category_remaining_budget = remaining_month_budget

    hours_passed_today = now.hour + now.minute / 60

    days_passed_month = (today - first_day_month).days + 1

    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_left_month = max(days_in_month - days_passed_month, 0)

    days_left_week = max(7 - today.weekday(), 1)

    imp_ratio = impulsive_ratio(expenses)
    imp_streak = impulsive_streak(expenses)

    amounts = [e.amount for e in expenses]
    spending_volatility = (
        statistics.stdev(amounts) if len(amounts) > 1 else 0
    )

    daily_prediction = predict_daily_overspend(user, today_expenses, expenses)

    if isinstance(daily_prediction, dict):
        predicted_daily_total = daily_prediction.get("predicted_total", spent_today)
        overspending_risk = daily_prediction.get("risk", False)
    else:
        predicted_daily_total = spent_today
        overspending_risk = daily_prediction is not None

    monthly_prediction = predict_monthly_runout(user, total_spent_month, expenses)

    if total_spent_month > 0 and days_passed_month > 0:
        daily_avg = total_spent_month / days_passed_month
        monthly_runout_days = (
            usable_budget / daily_avg if daily_avg > 0 else days_in_month
        )
    else:
        monthly_runout_days = days_in_month

    savings_target = monthly_income * savings_ratio

    actual_saved = monthly_income - total_spent_month

    savings_target_remaining = max(
        savings_target - actual_saved,
        0
    )
    previous_dynamic_limit = getattr(user, "daily_limit", 0)

    return {
        "monthly_income": monthly_income,
        "savings_ratio": savings_ratio,

        "spent_today": spent_today,
        "spent_this_week": spent_this_week,
        "total_spent_month": total_spent_month,

        "remaining_month_budget": remaining_month_budget,
        "weekly_remaining_budget": weekly_remaining_budget,
        "category_remaining_budget": category_remaining_budget,

        "hours_passed_today": hours_passed_today,
        "days_passed_month": days_passed_month,
        "days_left_month": days_left_month,
        "days_left_week": days_left_week,

        "impulsive_ratio": imp_ratio,
        "impulsive_streak": imp_streak,
        "spending_volatility": spending_volatility,

        "predicted_daily_total": predicted_daily_total,
        "overspending_risk": overspending_risk,
        "monthly_runout_days": monthly_runout_days,

        "savings_target_remaining": savings_target_remaining,

        "previous_dynamic_limit": previous_dynamic_limit
    }