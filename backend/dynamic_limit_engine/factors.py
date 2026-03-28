import math


def compute_behavior_factor(state):
    impulsive_ratio = state["impulsive_ratio"]
    streak = state["impulsive_streak"]
    volatility = state["spending_volatility"]

    streak_factor = min(streak / 5, 1)
    volatility_norm = volatility / (volatility + 1000) if volatility > 0 else 0

    penalty = 0.5 * impulsive_ratio + 0.3 * streak_factor + 0.2 * volatility_norm

    factor = 1 - penalty
    return max(0.5, min(factor, 1))


def compute_context_factor(state, current_limit):
    hours = state["hours_passed_today"]
    spent_today = state["spent_today"]

    # sigmoid time effect
    time_factor = 1 / (1 + math.exp(-(hours - 12) / 3))

    usage_ratio = spent_today / current_limit if current_limit > 0 else 0

    usage_penalty = max(0, usage_ratio - 0.7)

    penalty = 0.6 * time_factor + 0.4 * usage_penalty

    factor = 1 - penalty
    return max(0.6, min(factor, 1))


def compute_goal_factor(state, base_daily):
    savings_remaining = state["savings_target_remaining"]
    days_left = max(state["days_left_month"], 1)

    required_daily = savings_remaining / days_left

    pressure = required_daily / base_daily if base_daily > 0 else 0

    factor = 1 - min(pressure, 0.3)
    return max(0.7, min(factor, 1))