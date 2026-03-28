from .factors import (
    compute_behavior_factor,
    compute_context_factor,
    compute_goal_factor,
)


def compute_base_limit(state):
    monthly_income = state["monthly_income"]
    savings_ratio = state["savings_ratio"]

    usable = monthly_income * (1 - savings_ratio)
    return usable / 30


def compute_constraint_limit(state):
    monthly_remaining = state["remaining_month_budget"]
    days_left_month = max(state["days_left_month"], 1)

    weekly_remaining = state["weekly_remaining_budget"]
    days_left_week = max(state["days_left_week"], 1)

    category_remaining = state["category_remaining_budget"]

    monthly_constraint = monthly_remaining / days_left_month
    weekly_constraint = weekly_remaining / days_left_week

    return min(monthly_constraint, weekly_constraint, category_remaining)


def smooth_limit(prev, new):
    return 0.7 * prev + 0.3 * new


def apply_bounds(limit, base):
    min_limit = 0.6 * base
    max_limit = base

    return max(min(limit, max_limit), min_limit)


def generate_status(limit, base):
    ratio = limit / base if base > 0 else 0

    if ratio > 0.8:
        return "relaxed"
    elif ratio > 0.5:
        return "moderate"
    return "tight"


def generate_explanation(state, behavior, context, goal):
    explanation = {}

    if behavior < 0.7:
        explanation["behavior"] = "High impulsive spending detected"

    if context < 0.7:
        explanation["context"] = "Late-day or high usage spending risk"

    if goal < 0.85:
        explanation["goal"] = "Savings goal pressure is high"

    return explanation


def compute_dynamic_limit(state):
    base = compute_base_limit(state)
    constraint = compute_constraint_limit(state)

    behavior = compute_behavior_factor(state)
    goal = compute_goal_factor(state, base)

    temp_limit = base * behavior * goal

    context = compute_context_factor(state, temp_limit)

    adjusted = base * behavior * context * goal

    constrained = min(adjusted, constraint)

    prev = state.get("previous_dynamic_limit", base)
    smoothed = smooth_limit(prev, constrained)

    final_limit = apply_bounds(smoothed, base)

    safe_spend_now = max(final_limit - state["spent_today"], 0)

    status = generate_status(final_limit, base)

    explanation = generate_explanation(state, behavior, context, goal)

    return {
        "dynamic_limit": round(final_limit, 2),
        "safe_spend_now": round(safe_spend_now, 2),
        "status": status,
        "behavior_factor": round(behavior, 3),
        "context_factor": round(context, 3),
        "goal_factor": round(goal, 3),
        "explanation": explanation,
    }