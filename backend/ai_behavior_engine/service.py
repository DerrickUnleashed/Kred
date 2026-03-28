from budget_system.services.state import get_user_financial_state
from budget_system.services.insights import impulsive_ratio, impulsive_streak
from budget_system.services.prediction import spending_trend
from budget_system.models.expense import Expense

from .data_processor import extract_core_data
from .overspending_analyzer import analyze_overspending
from .category_analyzer import analyze_categories
from .trend_analyzer import analyze_weekly_trend
from .scoring import compute_behavior_score
from .recommender import generate_recommendations
from .simulator import run_simulation


def analyze_user_behavior(user_id, db):
    # 🔹 Fetch financial state
    state = get_user_financial_state(user_id, db)

    if not state:
        return {
            "error": "User financial state not found"
        }

    # 🔹 Fetch expenses separately (correct approach)
    expenses = db.query(Expense).filter(Expense.user_id == user_id).all()

    if not expenses:
        return {
            "risk_level": "low",
            "behavior_score": 100,
            "behavior_profile": "no_data",
            "message": "No expenses found for user",
            "patterns": {},
            "insights": [],
            "recommendations": [],
            "simulation": {}
        }

    # 🔹 Existing signals (reuse)
    ratio = impulsive_ratio(expenses)
    streak = impulsive_streak(expenses)
    raw_trend_signal = spending_trend(expenses)

    # 🔹 Safe access (avoid KeyError)
    volatility = state.get("spending_volatility", 0)

    # 🔹 Process data
    core = extract_core_data(expenses)

    # 🔹 Analysis layers
    overspend_data = analyze_overspending(core, state)
    category_data = analyze_categories(core)
    weekly_trend = analyze_weekly_trend(core)

    # 🔹 Fix trend consistency
    if weekly_trend.get("weekly_trend") == "insufficient_data":
        trend_signal = "Not enough data to determine trend"
    else:
        trend_signal = raw_trend_signal

    # 🔹 Scoring
    score_data = compute_behavior_score(
        ratio,
        volatility,
        overspend_data.get("frequency", 0),
        streak
    )

    # 🔹 Recommendations
    recommendations = generate_recommendations(
        ratio,
        category_data,
        overspend_data,
        weekly_trend
    )

    # 🔹 Simulation (chart + projection)
    simulation = run_simulation(core, ratio)

    # 🔹 Add contextual warning (important UX fix)
    if score_data["risk_level"] == "high":
        if "projection" in simulation:
            simulation["projection"]["warning"] = (
                "You are currently on a high-risk spending path. "
                "These projected savings require consistent behavior improvement."
            )

    # 🔹 Final Output
    return {
        "risk_level": score_data["risk_level"],
        "behavior_score": score_data["score"],
        "behavior_profile": score_data["profile"],

        "patterns": {
            "overspending": overspend_data,
            "categories": category_data,
            "trend": weekly_trend,
            "trend_signal": trend_signal
        },

        "insights": recommendations["insights"],
        "recommendations": recommendations["actions"],

        "simulation": simulation
    }