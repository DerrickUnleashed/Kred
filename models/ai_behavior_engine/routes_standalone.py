"""
routes_standalone.py - Standalone API without budget_system dependency
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kred_package.core.pipeline import KredAIPipeline

router = APIRouter(prefix="/ai-behavior", tags=["AI Behavior"])

# Global pipeline instance
_pipeline: Optional[KredAIPipeline] = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = KredAIPipeline()
    return _pipeline


class UserProfileBody(BaseModel):
    """User profile input schema"""
    age: int = Field(21, ge=10, le=80)
    country: str = "India"
    edu_level: str = "Undergraduate"
    field: str = "Engineering / Technology"
    college_tier: str = "Tier 2"
    cgpa: float = Field(7.5, ge=0.0, le=10.0)
    study_hours: float = 20.0
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


class AnalyzeResponse(BaseModel):
    """Response schema"""
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_user(body: UserProfileBody):
    """Analyze user financial behavior and future projections"""
    try:
        pipeline = get_pipeline()
        
        user_profile = body.model_dump(exclude={"generate_images"})
        
        # Create mock financial state (no database needed)
        financial_state = {
            "daily_limit": body.monthly_spend / 30,
            "spending_volatility": 100,
            "base_limit": body.monthly_spend / 30
        }
        
        # Run the pipeline
        result = pipeline.run(
            user_profile=user_profile,
            expenses=[],  # Empty list since no DB
            financial_state=financial_state,
            user_id=999,
            generate_images=body.generate_images
        )
        
        # Extract and format results
        future_self = result.get("future_self", {})
        behavior = result.get("behavior_analysis", {})
        regret = result.get("lifepath_regret", {})
        
        return AnalyzeResponse(
            status="success",
            data={
                "future_self": {
                    "scores": future_self.get("scores", {}),
                    "composite_score": future_self.get("scores", {}).get("composite"),
                    "risk_level": future_self.get("scores", {}).get("risk"),
                    "simulation": future_self.get("simulation", {}),
                    "analysis": future_self.get("analysis", {})
                },
                "behavior_analysis": {
                    "risk_level": behavior.get("risk_level"),
                    "behavior_score": behavior.get("behavior_score"),
                    "behavior_profile": behavior.get("behavior_profile"),
                    "insights": behavior.get("insights", []),
                    "recommendations": behavior.get("recommendations", []),
                    "motivational_summary": behavior.get("motivational_summary", "")
                },
                "lifepath_regret": {
                    "regret_score": regret.get("regret_score"),
                    "urgency_level": regret.get("urgency_level"),
                    "five_year_regret": regret.get("five_year_regret"),
                    "ten_year_regret": regret.get("ten_year_regret"),
                    "compounded_loss_5y": regret.get("regret_financials", {}).get("compounded_loss_5y"),
                    "compounded_loss_10y": regret.get("regret_financials", {}).get("compounded_loss_10y"),
                    "redemption_path": regret.get("redemption_path")
                }
            }
        )
        
    except Exception as e:
        return AnalyzeResponse(
            status="error",
            error=str(e)
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "KRED AI Engine"}


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "API is working!", "available_engines": ["FutureSelf", "BehaviorAnalysis", "LifePathRegret"]}    