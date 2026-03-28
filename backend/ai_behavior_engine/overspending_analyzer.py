def analyze_overspending(core, state):
    daily_spend = core["daily_spend"]
    daily_limit = state.get("daily_limit") or state.get("base_limit") or 0
    overspend_days = 0
    total_days = len(daily_spend)
    deviations = []

    for spend in daily_spend.values():
        deviation = spend - daily_limit
        deviations.append(deviation)

        if spend > daily_limit:
            overspend_days += 1

    frequency = overspend_days / total_days if total_days else 0
    avg_deviation = sum(deviations) / total_days if total_days else 0

    return {
        "frequency": frequency,
        "avg_deviation": avg_deviation
    }