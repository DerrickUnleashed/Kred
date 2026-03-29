"""
engines/lifepath_regret_engine.py — LifePath Regret Engine
===========================================================
Quantifies the long-term financial and lifestyle cost of poor spending behaviour.

Enhancements over baseline:
  ─ Mathematical compounding calculations (FV of daily overspend)
  ─ Time-value-of-money approximation (opportunity cost at CAGR)
  ─ Inflation-adjusted loss projections
  ─ LLM narrative enrichment (ChatGroq / qwen3-32b)
  ─ Structured JSON output with regret_score, urgency_level, metaphor
"""

from __future__ import annotations

import math
import time
from typing import Any

from ..core.config import (
    GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    MAX_RETRIES, RETRY_DELAY_SECONDS,
    ANNUAL_INFLATION_RATE, ANNUAL_INVESTMENT_RETURN, OPPORTUNITY_COST_RATE,
)
from ..utils.logger import get_logger
from ..utils.json_parser import extract_json
from ..utils.prompt_builder import lifepath_regret_prompt

log = get_logger("kred.engine.lifepath_regret")


# ══════════════════════════════════════════════════════════════════════════════
#  LLM CLIENT
# ══════════════════════════════════════════════════════════════════════════════

def _build_groq_llm() -> Any:
    if not GROQ_API_KEY:
        log.warning("GROQ_API_KEY not set — LLM narrative disabled in LifePathRegretEngine.")
        return None
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        log.info("ChatGroq initialised in LifePathRegretEngine.")
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
#  FINANCIAL MATHEMATICS
# ══════════════════════════════════════════════════════════════════════════════

def future_value_of_annuity(
    daily_payment: float,
    annual_rate: float,
    years: int,
) -> float:
    """
    FV of a daily payment invested at a given annual rate.

    Uses the standard FV annuity formula adapted to daily periods:
        FV = PMT × [(1 + r)^n − 1] / r
    where:
        PMT = daily_payment
        r   = daily rate = annual_rate / 365
        n   = years × 365
    """
    if daily_payment <= 0 or annual_rate <= 0 or years <= 0:
        return 0.0
    daily_rate = annual_rate / 365
    n          = years * 365
    fv = daily_payment * ((math.pow(1 + daily_rate, n) - 1) / daily_rate)
    return round(fv, 2)


def inflation_adjusted_value(nominal: float, annual_inflation: float, years: int) -> float:
    """Returns the real value of a nominal amount after inflation erosion."""
    if years <= 0:
        return nominal
    return round(nominal / math.pow(1 + annual_inflation, years), 2)


def compute_regret_financials(
    *,
    avg_daily_spend: float,
    daily_limit: float,
    overspend_frequency: float,
) -> dict[str, float]:
    """
    Compute all financial regret metrics using compounding mathematics.

    Logic:
      1. Estimate daily overspend = (avg_daily_spend - daily_limit) × overspend_frequency
         (zero-floored — we don't credit underspending here)
      2. Project what that daily overspend would compound to if invested at ANNUAL_INVESTMENT_RETURN
      3. Compute opportunity cost = what was lost by spending vs investing
      4. Apply inflation adjustment to real-value losses

    Returns:
        Dict of pre-computed financial quantities for injection into the LLM prompt.
    """
    daily_excess = max(0.0, (avg_daily_spend - daily_limit) * overspend_frequency)
    log.debug("Daily excess spend (frequency-weighted): ₹%.2f", daily_excess)

    # Compounded loss — what the excess would have grown to if invested
    cl_5y  = future_value_of_annuity(daily_excess, ANNUAL_INVESTMENT_RETURN, 5)
    cl_10y = future_value_of_annuity(daily_excess, ANNUAL_INVESTMENT_RETURN, 10)

    # Inflation-adjusted real loss
    cl_5y_real  = inflation_adjusted_value(cl_5y,  ANNUAL_INFLATION_RATE, 5)
    cl_10y_real = inflation_adjusted_value(cl_10y, ANNUAL_INFLATION_RATE, 10)

    # Opportunity cost — using a conservative rate
    oc_5y  = future_value_of_annuity(daily_excess, OPPORTUNITY_COST_RATE, 5)
    oc_10y = future_value_of_annuity(daily_excess, OPPORTUNITY_COST_RATE, 10)

    return {
        "daily_excess_spend":    daily_excess,
        "compounded_loss_5y":    cl_5y,
        "compounded_loss_10y":   cl_10y,
        "real_loss_5y":          cl_5y_real,
        "real_loss_10y":         cl_10y_real,
        "opportunity_cost_5y":   oc_5y,
        "opportunity_cost_10y":  oc_10y,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE CLASS
# ══════════════════════════════════════════════════════════════════════════════

class LifePathRegretEngine:
    """
    Quantifies the emotional and financial regret of current spending patterns
    using compounding mathematics + LLM-powered narrative.
    """

    def __init__(self) -> None:
        self._llm = _build_groq_llm()
        log.info("LifePathRegretEngine ready.")

    def run(
        self,
        *,
        user_id: int,
        behavior_analysis: dict[str, Any],
        financial_state: dict[str, Any],
        future_self_simulation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Run the LifePath Regret Engine.

        Args:
            user_id:               Integer user ID.
            behavior_analysis:     Output dict from BehaviorAnalysisEngine.run()
            financial_state:       Financial state from budget_system.
            future_self_simulation: Optional simulation dict from FutureSelfEngine.

        Returns:
            {
              "regret_financials":  { daily_excess_spend, compounded_loss_5y, ... },
              "regret_score":       int (0-100),
              "five_year_regret":   str,
              "ten_year_regret":    str,
              "missed_milestones":  list[str],
              "redemption_path":    str,
              "trajectory_metaphor": str,
              "urgency_level":      str,
              "llm_raw":            str (debug)
            }
        """
        log.info("LifePathRegretEngine.run() for user_id=%d", user_id)

        # ── Extract inputs from upstream stages ───────────────────────────────
        patterns         = behavior_analysis.get("patterns", {})
        overspending     = patterns.get("overspending", {})
        risk_profile     = behavior_analysis.get("risk_level", "unknown")
        behavior_profile = behavior_analysis.get("behavior_profile", "unknown")

        simulation       = behavior_analysis.get("simulation", {})
        projection       = simulation.get("projection", {})
        avg_daily_spend  = (projection.get("current_spend_5y", 0) / (365 * 5)
                            if projection.get("current_spend_5y") else 0.0)
        daily_limit      = (financial_state.get("daily_limit")
                            or financial_state.get("base_limit") or 0.0)
        overspend_freq   = overspending.get("frequency", 0.0)

        log.debug("avg_daily_spend=%.2f daily_limit=%.2f overspend_freq=%.3f",
                  avg_daily_spend, daily_limit, overspend_freq)

        # ── Mathematical compounding ───────────────────────────────────────────
        regret_financials = compute_regret_financials(
            avg_daily_spend=avg_daily_spend,
            daily_limit=daily_limit,
            overspend_frequency=overspend_freq,
        )
        log.debug("Regret financials: %s", regret_financials)

        # ── LLM narrative ─────────────────────────────────────────────────────
        llm_result: dict[str, Any] = {}
        llm_raw = ""
        if self._llm:
            prompt = lifepath_regret_prompt(
                user_id=user_id,
                avg_daily_spend=avg_daily_spend,
                daily_limit=daily_limit,
                overspend_frequency=overspend_freq,
                compounded_loss_5y=regret_financials["compounded_loss_5y"],
                compounded_loss_10y=regret_financials["compounded_loss_10y"],
                opportunity_cost_5y=regret_financials["opportunity_cost_5y"],
                opportunity_cost_10y=regret_financials["opportunity_cost_10y"],
                risk_profile=risk_profile,
                behavior_profile=behavior_profile,
            )
            llm_raw    = _llm_call_with_retry(self._llm, prompt)
            llm_result = extract_json(llm_raw, fallback={})
            log.debug("LLM regret keys: %s", list(llm_result.keys()))
        else:
            log.warning("LLM unavailable — LifePathRegret returning math-only output.")

        # ── Compute rule-based regret score as fallback ────────────────────────
        rule_regret_score = _rule_based_regret_score(
            overspend_freq=overspend_freq,
            risk_profile=risk_profile,
            compounded_loss_5y=regret_financials["compounded_loss_5y"],
        )

        return {
            "regret_financials": regret_financials,

            # LLM fields (with rule-based fallbacks)
            "regret_score":        llm_result.get("regret_score",        rule_regret_score),
            "five_year_regret":    llm_result.get("five_year_regret",    _default_5y_regret(regret_financials)),
            "ten_year_regret":     llm_result.get("ten_year_regret",     _default_10y_regret(regret_financials)),
            "missed_milestones":   llm_result.get("missed_milestones",   _default_milestones(risk_profile)),
            "redemption_path":     llm_result.get("redemption_path",     "Track spending daily → cut 20% of top category → invest the difference."),
            "trajectory_metaphor": llm_result.get("trajectory_metaphor", "A ship sailing with a slow leak — barely noticeable today, fatal at open sea."),
            "urgency_level":       llm_result.get("urgency_level",       _rule_urgency(risk_profile, overspend_freq)),
            "llm_raw":             llm_raw,  # debug field
        }


# ══════════════════════════════════════════════════════════════════════════════
#  RULE-BASED FALLBACKS (used when LLM is unavailable)
# ══════════════════════════════════════════════════════════════════════════════

def _rule_based_regret_score(
    overspend_freq: float,
    risk_profile: str,
    compounded_loss_5y: float,
) -> int:
    """Heuristic regret score when LLM is offline."""
    base = int(overspend_freq * 60)
    if risk_profile == "high":    base += 30
    elif risk_profile == "moderate": base += 15
    if compounded_loss_5y > 500_000: base += 10
    return min(base, 100)


def _rule_urgency(risk_profile: str, overspend_freq: float) -> str:
    if risk_profile == "high" or overspend_freq > 0.6:  return "Critical"
    if risk_profile == "moderate" or overspend_freq > 0.3: return "High"
    if overspend_freq > 0.1: return "Moderate"
    return "Low"


def _default_5y_regret(financials: dict[str, float]) -> str:
    loss = financials.get("compounded_loss_5y", 0)
    return (
        f"In 5 years, the compounding effect of daily overspending amounts to "
        f"₹{loss:,.0f} in lost investment growth — enough to cover a year of EMIs or "
        f"fund an emergency corpus. The absence of this buffer will be felt during "
        f"any financial shock."
    )


def _default_10y_regret(financials: dict[str, float]) -> str:
    loss = financials.get("compounded_loss_10y", 0)
    return (
        f"Over 10 years, the compounding shortfall reaches ₹{loss:,.0f}. "
        f"This gap represents the difference between owning and renting, between "
        f"retiring comfortably and continuing to work out of necessity."
    )


def _default_milestones(risk_profile: str) -> list[str]:
    if risk_profile == "high":
        return [
            "Emergency fund (6 months expenses)",
            "Down payment on first home",
            "Children's education fund",
        ]
    return [
        "Investment portfolio milestone",
        "Debt-free status",
        "Retirement corpus target",
    ]
