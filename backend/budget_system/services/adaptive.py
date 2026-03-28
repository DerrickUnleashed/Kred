from datetime import datetime, timedelta


def calculate_adaptive_limit(user, db, PlannedExpense):
    today = datetime.now().date()
    end_of_week = today + timedelta(days=(6 - today.weekday()))

    # Get planned expenses for remaining week
    planned = db.query(PlannedExpense).filter(
        PlannedExpense.user_id == user.id,
        PlannedExpense.date >= today,
        PlannedExpense.date <= end_of_week
    ).all()

    reserved = sum(p.amount for p in planned)

    # Remaining usable weekly money
    weekly_budget = user.daily_limit * 7
    remaining_budget = weekly_budget - reserved

    days_left = (end_of_week - today).days + 1

    if days_left <= 0:
        return user.daily_limit

    adaptive_limit = remaining_budget / days_left

    return round(adaptive_limit, 2)