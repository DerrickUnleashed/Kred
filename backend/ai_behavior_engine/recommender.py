def generate_recommendations(ratio, categories, overspend, trend):
    insights = []
    actions = []

    if ratio > 0.5:
        insights.append("High impulsive spending detected")
        actions.append("Delay non-essential purchases")

    if overspend["frequency"] > 0.5:
        insights.append("Frequent overspending observed")
        actions.append("Stick to daily limits")

    for c in categories:
        if c["risk"] == "high":
            insights.append(f"High spending in {c['category']}")
            actions.append(f"Reduce spending in {c['category']}")

    if trend["weekly_trend"] == "worsening":
        insights.append("Spending trend is increasing")
        actions.append("Review recent expenses")

    return {
        "insights": insights,
        "actions": actions
    }