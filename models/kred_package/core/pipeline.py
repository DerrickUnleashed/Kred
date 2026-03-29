"""
core/pipeline.py — Master pipeline orchestrator.

Enforces execution order:
  FutureSelf → BehaviorAnalysis → LifePathRegret

Each engine receives the outputs of the previous stages, enabling
context-aware chaining. All errors are caught and logged; the pipeline
never raises to the caller — it returns a structured result dict.
"""

from __future__ import annotations

import time
from typing import Any

from ..utils.logger import pipeline_log as log
from ..engines.future_self_engine import FutureSelfEngine
from ..engines.behavior_analysis_engine import BehaviorAnalysisEngine
from ..engines.lifepath_regret_engine import LifePathRegretEngine


class KredAIPipeline:
    """
    Orchestrates all three AI engines in sequence.

    Usage:
        pipeline = KredAIPipeline()
        result   = pipeline.run(user_profile=..., expenses=..., financial_state=...)
    """

    def __init__(self) -> None:
        self.future_self_engine      = FutureSelfEngine()
        self.behavior_engine         = BehaviorAnalysisEngine()
        self.lifepath_regret_engine  = LifePathRegretEngine()
        log.info("KredAIPipeline initialised — all three engines loaded.")

    # ──────────────────────────────────────────────────────────────────────────
    def run(
        self,
        *,
        user_profile: dict[str, Any],
        expenses: list[Any],
        financial_state: dict[str, Any],
        user_id: int = 0,
        generate_images: bool = True,
    ) -> dict[str, Any]:
        """
        Execute the full pipeline.

        Args:
            user_profile:    Dict matching the FutureSelf user schema.
            expenses:        List of Expense ORM objects (or dicts).
            financial_state: Financial state dict from budget_system.
            user_id:         Integer user ID.
            generate_images: Whether to call FLUX for image generation.

        Returns:
            Structured dict with keys:
              future_self, behavior_analysis, lifepath_regret, meta
        """
        t_start = time.perf_counter()
        result: dict[str, Any] = {
            "future_self": {},
            "behavior_analysis": {},
            "lifepath_regret": {},
            "meta": {"pipeline_status": "started", "elapsed_ms": 0},
        }

        # ── Stage 1: Future Self Engine ───────────────────────────────────────
        log.info("Pipeline Stage 1 → FutureSelfEngine")
        try:
            future_self_result = self.future_self_engine.run(
                user_profile=user_profile,
                generate_images=generate_images,
            )
            result["future_self"] = future_self_result
            log.info("Stage 1 complete — composite score: %s",
                     future_self_result.get("scores", {}).get("composite", "N/A"))
        except Exception as exc:
            log.error("Stage 1 FutureSelfEngine failed: %s", exc, exc_info=True)
            result["future_self"] = {"error": str(exc)}

        # ── Stage 2: Behavior Analysis Engine ────────────────────────────────
        log.info("Pipeline Stage 2 → BehaviorAnalysisEngine")
        try:
            behavior_result = self.behavior_engine.run(
                expenses=expenses,
                financial_state=financial_state,
                user_id=user_id,
                # Pass future_self context for richer recommendations
                future_self_context=result.get("future_self", {}),
            )
            result["behavior_analysis"] = behavior_result
            log.info("Stage 2 complete — risk: %s | score: %s",
                     behavior_result.get("risk_level", "N/A"),
                     behavior_result.get("behavior_score", "N/A"))
        except Exception as exc:
            log.error("Stage 2 BehaviorAnalysisEngine failed: %s", exc, exc_info=True)
            result["behavior_analysis"] = {"error": str(exc)}

        # ── Stage 3: LifePath Regret Engine ───────────────────────────────────
        log.info("Pipeline Stage 3 → LifePathRegretEngine")
        try:
            regret_result = self.lifepath_regret_engine.run(
                user_id=user_id,
                behavior_analysis=result.get("behavior_analysis", {}),
                financial_state=financial_state,
                future_self_simulation=result.get("future_self", {}).get("simulation", {}),
            )
            result["lifepath_regret"] = regret_result
            log.info("Stage 3 complete — regret score: %s | urgency: %s",
                     regret_result.get("regret_score", "N/A"),
                     regret_result.get("urgency_level", "N/A"))
        except Exception as exc:
            log.error("Stage 3 LifePathRegretEngine failed: %s", exc, exc_info=True)
            result["lifepath_regret"] = {"error": str(exc)}

        # ── Meta ──────────────────────────────────────────────────────────────
        elapsed = round((time.perf_counter() - t_start) * 1000, 1)
        result["meta"] = {
            "pipeline_status": "complete",
            "elapsed_ms": elapsed,
            "user_id": user_id,
            "stages_completed": sum([
                "error" not in result["future_self"],
                "error" not in result["behavior_analysis"],
                "error" not in result["lifepath_regret"],
            ]),
        }
        log.info("Pipeline complete in %.1f ms", elapsed)
        return result
