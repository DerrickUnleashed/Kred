def weekly_analysis(expenses):
    if not expenses:
        return None

    first_half = expenses[:len(expenses)//2]
    second_half = expenses[len(expenses)//2:]

    sum1 = sum(e.amount for e in first_half)
    sum2 = sum(e.amount for e in second_half)

    trend = "increasing" if sum2 > sum1 else "stable"

    top_category = max(
        set(e.category for e in expenses),
        key=lambda c: sum(e.amount for e in expenses if e.category == c)
    )

    risk = "high" if trend == "increasing" else "moderate"

    return {
        "weekly_trend": trend,
        "risk": risk,
        "top_category": top_category
    }