from collections import Counter
from datetime import datetime


def impulsive_ratio(expenses):
    total = len(expenses)
    if total == 0:
        return 0

    impulsive = len([e for e in expenses if e.tag == "impulsive"])
    return round((impulsive / total) * 100, 2)


# 🔥 1. Impulsive streak
def impulsive_streak(expenses):
    streak = 0

    for e in reversed(expenses):
        if e.tag == "impulsive":
            streak += 1
        else:
            break

    return streak


# 🔥 2. Time-based insight
def impulsive_time_pattern(expenses):
    night_impulsive = 0
    total_impulsive = 0

    for e in expenses:
        if e.tag == "impulsive":
            total_impulsive += 1
            hour = e.created_at.hour

            if 18 <= hour <= 24:
                night_impulsive += 1

    if total_impulsive == 0:
        return None

    if night_impulsive / total_impulsive > 0.5:
        return "Most impulsive spending happens at night"

    return None


# 🔥 3. Category regret
def worst_category(expenses):
    category_map = {}

    for e in expenses:
        if e.tag == "impulsive":
            category_map[e.category] = category_map.get(e.category, 0) + 1

    if not category_map:
        return None

    return max(category_map, key=category_map.get)


# 🔥 4. Savings suggestion
def savings_suggestion(expenses):
    impulsive = [e.amount for e in expenses if e.tag == "impulsive"]

    if not impulsive:
        return None

    avg_impulse = sum(impulsive) / len(impulsive)

    monthly_saving = round(avg_impulse * 30, 2)

    return f"Reducing impulsive spending by ₹{int(avg_impulse)} daily can save ₹{int(monthly_saving)} monthly"