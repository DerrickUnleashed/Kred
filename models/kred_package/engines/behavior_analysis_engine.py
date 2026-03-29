"""
engines/behavior_analysis_engine.py — Behavior Analysis Engine
==============================================================
Wraps the original modular analysis pipeline (data_processor, overspending_analyzer,
category_analyzer, trend_analyzer, scoring, recommender, simulator) and enriches it
with a ChatGroq LLM layer for deeper behavioral insights and structured JSON output.

Original logic is 100% preserved. Only added:
  - LLM enrichment layer (ChatGroq / qwen3-32b)
  - Structured JSON output enforcement
  - Retry logic
  - Type hints throughout
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from ..core.config import (
    GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    MAX_RETRIES, RETRY_DELAY_SECONDS,
)
from ..utils.logger import get_logger
from ..utils.json_parser import extract_json
from ..utils.prompt_builder import behavior_analysis_prompt

log = get_logger("kred.engine.behavior_analysis")


# ══════════════════════════════════════════════════════════════════════════════
#  LLM CLIENT
# ══════════════════════════════════════════════════════════════════════════════

def _build_groq_llm() -> Any:
    if not GROQ_API_KEY:
        log.warning("GROQ_API_KEY not set — LLM enrichment disabled.")
        return None
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        log.info("ChatGroq initialised in BehaviorAnalysisEngine.")
        return llm
    except Exception as exc:
        log.error("ChatGroq init failed: %s", exc)
        return None


def _llm_call_with_retry(llm: Any, prompt: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
            log.warning("LLM attempt %d/%d failed: %s — retrying in %.1fs",
                        attempt, MAX_RETRIES, exc, wait)
            if attempt < MAX_RETRIES:
                time.sleep(wait)
    log.error("LLM failed after %d attempts.", MAX_RETRIES)
    return ""


# ══════════════════════════════════════════════════════════════════════════════
#  ORIGINAL ANALYSIS MODULES (preserved verbatim — only type hints added)
# ══════════════════════════════════════════════════════════════════════════════

def _extract_core_data(expenses: list[Any]) -> dict[str, Any]:
    """Preserved from data_processor.py — sorts expenses and builds daily_spend."""
    expenses = sorted(expenses, key=lambda e: e.created_at)
    daily_spend: dict = defaultdict(float)
    for e in expenses:
        date = e.created_at.date()
        daily_spend[date] += e.amount
    return {
        "daily_spend": dict(daily_spend),
        "expenses":    expenses,
    }


def _analyze_overspending(core: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    """Preserved from overspending_analyzer.py."""
    daily_spend  = core["daily_spend"]
    daily_limit  = state.get("daily_limit") or state.get("base_limit") or 0
    overspend_days = 0
    total_days   = len(daily_spend)
    deviations   = []

    for spend in daily_spend.values():
        deviation = spend - daily_limit
        deviations.append(deviation)
        if spend > daily_limit:
            overspend_days += 1

    frequency    = overspend_days / total_days if total_days else 0
    avg_deviation = sum(deviations) / total_days if total_days else 0

    return {"frequency": frequency, "avg_deviation": avg_deviation}


def _analyze_categories(core: dict[str, Any]) -> list[dict[str, Any]]:
    """Preserved from category_analyzer.py."""
    expenses = core["expenses"]
    category_totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        category_totals[e.category] += e.amount

    total  = sum(category_totals.values())
    result = []
    for cat, amt in category_totals.items():
        percentage = amt / total if total else 0
        risk       = "high" if percentage > 0.4 else "normal"
        result.append({"category": cat, "percentage": round(percentage, 2), "risk": risk})
    return result


def _analyze_weekly_trend(core: dict[str, Any]) -> dict[str, Any]:
    """Preserved from trend_analyzer.py."""
    daily = list(core["daily_spend"].values())
    if len(daily) < 14:
        return {"weekly_trend": "insufficient_data"}
    recent   = sum(daily[-7:])
    previous = sum(daily[-14:-7])
    if recent > previous:   trend = "worsening"
    elif recent < previous: trend = "improving"
    else:                   trend = "stable"
    return {"weekly_trend": trend}


def _normalize(value: float, max_val: float) -> float:
    """Preserved from scoring.py."""
    return min(value / max_val, 1) if max_val else 0


def _compute_behavior_score(
    ratio: float, volatility: float, overspend_freq: float, streak: int
) -> dict[str, Any]:
    """Preserved from scoring.py."""
    score = (
        0.4 * ratio +
        0.3 * _normalize(volatility, 1000) +
        0.2 * overspend_freq +
        0.1 * _normalize(streak, 10)
    )
    score     = max(0.0, min(score, 1.0))
    score_100 = int((1 - score) * 100)
    if score_100 > 75:   risk, profile = "low",      "disciplined"
    elif score_100 > 50: risk, profile = "moderate",  "balanced"
    else:                risk, profile = "high",       "impulsive"
    return {"score": score_100, "risk_level": risk, "profile": profile}


def _generate_recommendations(
    ratio: float,
    categories: list[dict[str, Any]],
    overspend: dict[str, Any],
    trend: dict[str, Any],
) -> dict[str, Any]:
    """Preserved from recommender.py."""
    insights: list[str] = []
    actions:  list[str] = []

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

    return {"insights": insights, "actions": actions}


def _moving_average(values: list[float], window: int = 3) -> list[float]:
    """Preserved from simulator.py."""
    if len(values) < window:
        return values
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        avg   = sum(values[start:i + 1]) / (i - start + 1)
        result.append(avg)
    return result


def _run_simulation(core: dict[str, Any], ratio: float) -> dict[str, Any]:
    """Preserved from simulator.py."""
    daily_items = sorted(core["daily_spend"].items())
    daily  = [v for _, v in daily_items]
    dates  = [str(d) for d, _ in daily_items]
    predicted = _moving_average(daily)

    chart = [
        {"date": dates[i], "actual": daily[i], "predicted": round(predicted[i], 2)}
        for i in range(len(daily))
    ]

    avg_daily = sum(daily) / len(daily) if daily else 0
    improvement_factor = 0.2
    current_5y_spend   = avg_daily * 365 * 5
    improved_5y_spend  = current_5y_spend * (1 - improvement_factor)
    potential_savings  = current_5y_spend - improved_5y_spend

    return {
        "chart": chart,
        "projection": {
            "current_spend_5y":  int(current_5y_spend),
            "improved_spend_5y": int(improved_5y_spend),
            "potential_savings": int(potential_savings),
            "note": "Savings achievable if recommendations are followed",
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE CLASS
# ══════════════════════════════════════════════════════════════════════════════

class BehaviorAnalysisEngine:
    """
    Executes the full behavior analysis pipeline and enriches rule-based
    outputs with LLM-generated insights via ChatGroq.
    """

    def __init__(self) -> None:
        self._llm = _build_groq_llm()
        log.info("BehaviorAnalysisEngine ready.")

    def run(
        self,
        *,
        expenses: list[Any],
        financial_state: dict[str, Any],
        user_id: int,
        future_self_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run full behavior analysis.

        Inputs come directly from the budget_system ORM / service layer.
        Replicates analyze_user_behavior() from service.py with LLM enrichment.
        """
        log.info("BehaviorAnalysisEngine.run() for user_id=%d", user_id)

        # ── Guard: no expenses ────────────────────────────────────────────────
        if not expenses:
            log.warning("No expenses found for user_id=%d", user_id)
            return {
                "risk_level":      "low",
                "behavior_score":  100,
                "behavior_profile": "no_data",
                "message":         "No expenses found for user",
                "patterns":        {},
                "insights":        [],
                "recommendations": [],
                "simulation":      {},
                "llm_enrichment":  {},
            }

        # ── Import reused signals from budget_system ──────────────────────────
        try:
            from budget_system.services.insights import impulsive_ratio, impulsive_streak
            from budget_system.services.prediction import spending_trend
            ratio  = impulsive_ratio(expenses)
            streak = impulsive_streak(expenses)
            raw_trend_signal = spending_trend(expenses)
        except ImportError:
            log.warning("budget_system not available — using default signal values.")
            ratio, streak, raw_trend_signal = 0.0, 0, "stable"

        volatility = financial_state.get("spending_volatility", 0)

        # ── Core processing ───────────────────────────────────────────────────
        core          = _extract_core_data(expenses)
        overspend_data = _analyze_overspending(core, financial_state)
        category_data  = _analyze_categories(core)
        weekly_trend   = _analyze_weekly_trend(core)

        trend_signal = (
            "Not enough data to determine trend"
            if weekly_trend.get("weekly_trend") == "insufficient_data"
            else raw_trend_signal
        )

        # ── Scoring ───────────────────────────────────────────────────────────
        score_data = _compute_behavior_score(
            ratio, volatility, overspend_data.get("frequency", 0), streak
        )

        # ── Rule-based recommendations ────────────────────────────────────────
        recommendations = _generate_recommendations(
            ratio, category_data, overspend_data, weekly_trend
        )

        # ── Simulation ────────────────────────────────────────────────────────
        simulation = _run_simulation(core, ratio)

        if score_data["risk_level"] == "high" and "projection" in simulation:
            simulation["projection"]["warning"] = (
                "You are currently on a high-risk spending path. "
                "These projected savings require consistent behavior improvement."
            )

        # ── LLM enrichment layer ──────────────────────────────────────────────
        llm_enrichment: dict[str, Any] = {}
        if self._llm:
            prompt = behavior_analysis_prompt(
                user_id=user_id,
                risk_level=score_data["risk_level"],
                behavior_score=score_data["score"],
                behavior_profile=score_data["profile"],
                overspending=overspend_data,
                categories=category_data,
                trend=weekly_trend,
                insights=recommendations["insights"],
                raw_recommendations=recommendations["actions"],
            )
            raw           = _llm_call_with_retry(self._llm, prompt)
            llm_enrichment = extract_json(raw, fallback={})
            log.debug("LLM enrichment keys: %s", list(llm_enrichment.keys()))
        else:
            log.warning("LLM not available — skipping behavior enrichment.")

        # ── Merge LLM insights with rule-based (LLM takes priority if present) ─
        final_insights       = llm_enrichment.get("enriched_insights", recommendations["insights"])
        final_recommendations = llm_enrichment.get("priority_actions",  recommendations["actions"])

        return {
            "risk_level":       score_data["risk_level"],
            "behavior_score":   score_data["score"],
            "behavior_profile": llm_enrichment.get("behavioral_archetype", score_data["profile"]),

            "patterns": {
                "overspending": overspend_data,
                "categories":   category_data,
                "trend":        weekly_trend,
                "trend_signal": trend_signal,
            },

            "insights":        final_insights,
            "recommendations": final_recommendations,

            "motivational_summary": llm_enrichment.get("motivational_summary", ""),
            "simulation":           simulation,
            "llm_enrichment":       llm_enrichment,
        }
