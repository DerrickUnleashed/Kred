def moving_average(values, window=3):
    if len(values) < window:
        return values

    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        avg = sum(values[start:i+1]) / (i - start + 1)
        result.append(avg)

    return result


def run_simulation(core, ratio):
    daily_items = sorted(core["daily_spend"].items())
    daily = [v for _, v in daily_items]
    dates = [str(d) for d, _ in daily_items]

    predicted = moving_average(daily)

    chart = []
    for i in range(len(daily)):
        chart.append({
            "date": dates[i],
            "actual": daily[i],
            "predicted": round(predicted[i], 2)
        })

    avg_daily = sum(daily) / len(daily) if daily else 0

    improvement = min(ratio, 0.3)

    avg_daily = sum(daily) / len(daily) if daily else 0

    # Scenario 1: Current behavior continues
    current_5y_spend = avg_daily * 365 * 5

    # Scenario 2: Improvement (only if user fixes behavior)
    improvement_factor = 0.2  # 20% reduction
    improved_5y_spend = current_5y_spend * (1 - improvement_factor)

    potential_savings = current_5y_spend - improved_5y_spend

    return {
        "chart": chart,
        "projection": {
            "current_spend_5y": int(current_5y_spend),
            "improved_spend_5y": int(improved_5y_spend),
            "potential_savings": int(potential_savings),
            "note": "Savings achievable if recommendations are followed"
        }
    }