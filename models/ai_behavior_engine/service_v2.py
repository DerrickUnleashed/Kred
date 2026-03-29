"""
ai_behavior_engine/service_v2.py — Upgraded service layer
==========================================================
Bridges the FastAPI route layer to the new KredAIPipeline.
Preserves the original service.py return contract 100% while
enriching it with LLM insights, regret analysis, and structured output.
"""

from __future__ import annotations

from typing import Any

from ..utils.logger import get_logger
from ..core.pipeline import KredAIPipeline

log = get_logger("kred.service_v2")

# Module-level singleton — pipeline is expensive to initialise
_pipeline: KredAIPipeline | None = None


def _get_pipeline() -> KredAIPipeline:
    global _pipeline
    if _pipeline is None:
        log.info("Initialising KredAIPipeline singleton.")
        _pipeline = KredAIPipeline()
    return _pipeline


def analyze_user_behavior_v2(
    user_id: int,
    db: Any,
    user_profile: dict[str, Any] | None = None,
    generate_images: bool = False,
) -> dict[str, Any]:
    """
    Upgraded drop-in replacement for the original analyze_user_behavior().

    Args:
        user_id:        Integer user ID (used for DB queries).
        db:             SQLAlchemy Session.
        user_profile:   Optional dict for FutureSelf engine (if None, skips FS stage).
        generate_images: Whether to call FLUX for image generation.

    Returns:
        Structured dict preserving original contract + enriched fields.
    """
    log.info("analyze_user_behavior_v2 called for user_id=%d", user_id)

    # ── Fetch data (preserving original patterns) ─────────────────────────────
    try:
        from budget_system.services.state import get_user_financial_state
        from budget_system.models.expense import Expense

        financial_state = get_user_financial_state(user_id, db)
        if not financial_state:
            log.warning("No financial state found for user_id=%d", user_id)
            return {"error": "User financial state not found"}

        expenses = db.query(Expense).filter(Expense.user_id == user_id).all()
    except ImportError as exc:
        log.error("budget_system import failed: %s", exc)
        return {"error": f"budget_system unavailable: {exc}"}

    if not expenses:
        return {
            "risk_level":       "low",
            "behavior_score":   100,
            "behavior_profile": "no_data",
            "message":          "No expenses found for user",
            "patterns":         {},
            "insights":         [],
            "recommendations":  [],
            "simulation":       {},
            "lifepath_regret":  {},
            "future_self":      {},
        }

    # ── Run pipeline ──────────────────────────────────────────────────────────
    pipeline = _get_pipeline()
    result   = pipeline.run(
        user_profile=user_profile or {},
        expenses=expenses,
        financial_state=financial_state,
        user_id=user_id,
        generate_images=generate_images and bool(user_profile),
    )

    behavior  = result.get("behavior_analysis", {})
    future    = result.get("future_self", {})
    regret    = result.get("lifepath_regret", {})

    # ── Return original contract + enriched fields ────────────────────────────
    return {
        # ── Original contract (unchanged) ─────────────────────────────────────
        "risk_level":       behavior.get("risk_level", "unknown"),
        "behavior_score":   behavior.get("behavior_score", 0),
        "behavior_profile": behavior.get("behavior_profile", "unknown"),
        "patterns":         behavior.get("patterns", {}),
        "insights":         behavior.get("insights", []),
        "recommendations":  behavior.get("recommendations", []),
        "simulation":       behavior.get("simulation", {}),

        # ── Enriched fields (new) ─────────────────────────────────────────────
        "motivational_summary": behavior.get("motivational_summary", ""),
        "lifepath_regret":      regret,
        "future_self":          {
            "scores":     future.get("scores", {}),
            "simulation": future.get("simulation", {}),
            "scenarios":  future.get("scenarios", {}),
            "analysis":   future.get("analysis", {}),
        },

        # ── Pipeline meta ─────────────────────────────────────────────────────
        "meta": result.get("meta", {}),
    }
