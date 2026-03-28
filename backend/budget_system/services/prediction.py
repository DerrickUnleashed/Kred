from datetime import datetime, timezone


# 🔥 1. Predict overspending today (BLENDED MODEL)
def predict_daily_overspend(user, expenses_today, all_expenses):
    if not expenses_today:
        return None

    total_spent = sum(e.amount for e in expenses_today)

    now = datetime.now(timezone.utc)
    hour = max(now.hour, 1)  # avoid division issues

    # 🔹 Today's projection
    today_projection = (total_spent / hour) * 24

    # 🔹 Historical daily averages (last 7 days)
    daily_totals = {}
    for e in all_expenses:
        day = e.created_at.date()
        daily_totals.setdefault(day, 0)
        daily_totals[day] += e.amount

    last_days = list(daily_totals.values())[-7:]
    historical_avg = sum(last_days) / len(last_days) if last_days else total_spent

    # 🔹 Blending factor (time-aware)
    alpha = min(hour / 12, 1)

    predicted_total = alpha * today_projection + (1 - alpha) * historical_avg

    if predicted_total > user.daily_limit:
        excess = int(predicted_total - user.daily_limit)
        return f"At this pace, you'll exceed today's limit by ₹{excess}"

    return None


# 🔥 2. Monthly burn rate prediction (FIXED + SMOOTHED)
def predict_monthly_runout(user, total_spent, expenses):
    if total_spent == 0:
        return None

    today = datetime.now(timezone.utc).date()
    first_day = today.replace(day=1)

    # 🔹 Days elapsed in current month
    days_elapsed = (today - first_day).days + 1

    # 🔹 Daily totals
    daily_totals = {}
    for e in expenses:
        day = e.created_at.date()
        daily_totals.setdefault(day, 0)
        daily_totals[day] += e.amount

    historical_avg = (
        sum(daily_totals.values()) / len(daily_totals)
        if daily_totals else 0
    )

    # 🔹 Smoothing factor
    k = 3

    daily_avg = (total_spent + k * historical_avg) / (days_elapsed + k)

    if daily_avg == 0:
        return None

    usable_income = user.daily_limit * 30

    days_left = usable_income / daily_avg

    if days_left < 30:
        return f"At this pace, you'll run out of money in {int(days_left)} days"

    return None


# 🔥 3. Spending acceleration (unchanged, already good)
def spending_trend(expenses):
    if len(expenses) < 2:
        return None

    first_half = expenses[:len(expenses)//2]
    second_half = expenses[len(expenses)//2:]

    sum1 = sum(e.amount for e in first_half)
    sum2 = sum(e.amount for e in second_half)

    if sum2 > sum1 * 1.2:
        return "Your spending is increasing over time"

    return None