def normalize(value, max_val):
    return min(value / max_val, 1)


def compute_behavior_score(ratio, volatility, overspend_freq, streak):
    score = (
        0.4 * ratio +
        0.3 * normalize(volatility, 1000) +
        0.2 * overspend_freq +
        0.1 * normalize(streak, 10)
    )

    score = max(0, min(score, 1))  # clamp 0–1
    score_100 = int((1 - score) * 100)
    if score_100 > 75:
        risk = "low"
        profile = "disciplined"
    elif score_100 > 50:
        risk = "moderate"
        profile = "balanced"
    else:
        risk = "high"
        profile = "impulsive"

    return {
        "score": score_100,
        "risk_level": risk,
        "profile": profile
    }