"""
ai_behavior_engine/routes_v2.py — Upgraded FastAPI routes
==========================================================
Fixed version - works without budget_system dependency
"""

from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kred_package.core.pipeline import KredAIPipeline

router = APIRouter(prefix="/ai-behavior", tags=["AI Behavior"])

# Global pipeline instance
_pipeline: Optional[KredAIPipeline] = None

def get_pipeline() -> KredAIPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = KredAIPipeline()
    return _pipeline


# ── Request Models ─────────────────────────────────────────────────────────────
class UserProfileBody(BaseModel):
    age: int = Field(21, ge=10, le=80)
    country: str = "India"
    edu_level: str = "Undergraduate"
    field: str = "Engineering / Technology"
    college_tier: str = "Tier 2"
    cgpa: float = Field(7.5, ge=0.0, le=10.0)
    study_hours: float = Field(20.0, ge=0.0)
    target_career: str = ""
    skill: str = "Intermediate"
    experience: bool = False
    consistency: str = "Medium"
    monthly_spend: float = 10000.0
    savings: str = "Medium"
    family_bg: str = "Middle"
    discipline: str = "Balanced"
    screen_time: str = "Medium (4-6 hrs)"
    health: str = "Average"
    sleep: str = "Average"
    generate_images: bool = False


# ── Response Models ────────────────────────────────────────────────────────────
class AnalysisResponse(BaseModel):
    status: str
    composite_score: float
    risk_level: str
    behavior_score: int
    behavior_profile: str
    regret_score: int
    urgency_level: str
    details: Optional[dict] = None


# ── API Endpoints ──────────────────────────────────────────────────────────────
@router.get("/health")
def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "KRED AI Engine"}


@router.get("/status")
def pipeline_status() -> dict[str, Any]:
    """Check pipeline status"""
    pipeline = get_pipeline()
    return {
        "pipeline_initialized": pipeline is not None,
        "status": "ready" if pipeline else "not_initialized"
    }


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_user(body: UserProfileBody) -> dict[str, Any]:
    """
    Full pipeline analysis: FutureSelf + BehaviorAnalysis + LifePathRegret.
    No database required - uses provided user profile.
    """
    try:
        pipeline = get_pipeline()
        
        # Convert to dict
        user_profile = body.model_dump(exclude={"generate_images"})
        
        # Create financial state from user data
        financial_state = {
            "daily_limit": body.monthly_spend / 30,
            "spending_volatility": 100,
            "base_limit": body.monthly_spend / 30
        }
        
        # Run pipeline
        result = pipeline.run(
            user_profile=user_profile,
            expenses=[],  # No transaction data
            financial_state=financial_state,
            user_id=999,
            generate_images=body.generate_images
        )
        
        # Extract results
        future_self = result.get("future_self", {})
        behavior = result.get("behavior_analysis", {})
        regret = result.get("lifepath_regret", {})
        scores = future_self.get("scores", {})
        
        return {
            "status": "success",
            "composite_score": scores.get("composite", 0),
            "risk_level": behavior.get("risk_level", "unknown"),
            "behavior_score": behavior.get("behavior_score", 0),
            "behavior_profile": behavior.get("behavior_profile", "unknown"),
            "regret_score": regret.get("regret_score", 0),
            "urgency_level": regret.get("urgency_level", "Low"),
            "details": {
                "future_scores": {
                    "academic": scores.get("academic"),
                    "financial": scores.get("financial"),
                    "career": scores.get("career"),
                    "lifestyle": scores.get("lifestyle")
                },
                "insights": behavior.get("insights", [])[:5],
                "recommendations": behavior.get("recommendations", [])[:5],
                "redemption_path": regret.get("redemption_path", "")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Original endpoint (commented out - requires database) ──────────────────────
# @router.get("/{user_id}")
# def get_behavior_analysis(user_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
#     """
#     Original behavior analysis endpoint — requires budget_system database.
#     Use POST /analyze instead for standalone mode.
#     """
#     return analyze_user_behavior_v2(
#         user_id=user_id,
#         db=db,
#         user_profile=None,
#         generate_images=False,
#     )


# ── For backward compatibility with original route ─────────────────────────────
@router.get("/{user_id}")
def get_behavior_analysis_fallback(user_id: int) -> dict[str, Any]:
    """
    Fallback endpoint when database is not available.
    Returns analysis with default profile.
    """
    return {
        "message": "Database not available. Use POST /analyze with user profile.",
        "suggestion": {
            "endpoint": "POST /ai-behavior/analyze",
            "example_body": {
                "age": 21,
                "cgpa": 7.5,
                "monthly_spend": 18000,
                "skill": "Intermediate"
            }
        }
    }