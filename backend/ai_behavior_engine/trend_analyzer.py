def analyze_weekly_trend(core):
    daily = list(core["daily_spend"].values())

    if len(daily) < 14:
        return {"weekly_trend": "insufficient_data"}

    recent = sum(daily[-7:])
    previous = sum(daily[-14:-7])

    if recent > previous:
        trend = "worsening"
    elif recent < previous:
        trend = "improving"
    else:
        trend = "stable"

    return {"weekly_trend": trend}