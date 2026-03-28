def generate_action(remaining, risk, impulsive_ratio):
    if remaining <= 0:
        return "Stop spending for today"

    if risk == "high":
        return "Avoid non-essential spending today"

    if impulsive_ratio > 0.5:
        return "Focus on essential purchases only"

    return f"You can safely spend ₹{int(remaining)} today"