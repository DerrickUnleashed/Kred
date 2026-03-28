from datetime import datetime, timezone


# 🔥 1. Predict overspending today
def predict_daily_overspend(user, expenses_today):
    if not expenses_today:
        return None

    total_spent = sum(e.amount for e in expenses_today)

    now = datetime.now(timezone.utc)
    hour = now.hour

    # Avoid divide by zero
    if hour == 0:
        return None

    # Estimate full-day spending
    predicted_total = (total_spent / hour) * 24

    if predicted_total > user.daily_limit:
        return f"At this pace, you'll exceed today's limit by ₹{int(predicted_total - user.daily_limit)}"

    return None


# 🔥 2. Monthly burn rate prediction
def predict_monthly_runout(user, total_spent):
    if total_spent == 0:
        return None

    daily_avg = total_spent / 30  # simple estimate

    if daily_avg == 0:
        return None

    usable_income = user.daily_limit * 30

    days_left = usable_income / daily_avg

    if days_left < 30:
        return f"At this pace, you'll run out of money in {int(days_left)} days"

    return None


# 🔥 3. Spending acceleration
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