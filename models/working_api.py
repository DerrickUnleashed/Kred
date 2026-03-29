# working_api.py - Working API based on successful test
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from kred_package.core.pipeline import KredAIPipeline

app = FastAPI(title="KRED AI Engine API", version="1.0.0")

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline instance (singleton)
_pipeline: Optional[KredAIPipeline] = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        print("Initializing KRED Pipeline...")
        _pipeline = KredAIPipeline()
    return _pipeline

# Request/Response Models
class UserProfileRequest(BaseModel):
    age: int = Field(21, ge=18, le=80)
    country: str = "India"
    edu_level: str = "Undergraduate"
    field: str = "Engineering / Technology"
    college_tier: str = "Tier 2"
    cgpa: float = Field(7.5, ge=0, le=10)
    study_hours: float = 20.0
    target_career: str = ""
    skill: str = "Intermediate"
    experience: bool = False
    consistency: str = "Medium"
    monthly_spend: float = Field(10000, ge=0)
    savings: str = "Medium"
    family_bg: str = "Middle"
    discipline: str = "Balanced"
    screen_time: str = "Medium (4-6 hrs)"
    health: str = "Average"
    sleep: str = "Average"
    generate_images: bool = False

class AnalysisResponse(BaseModel):
    status: str
    composite_score: float
    risk_level: str
    behavior_score: int
    behavior_profile: str
    regret_score: int
    urgency_level: str
    details: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {
        "message": "KRED AI Engine API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "Analyze user financial behavior",
            "GET /health": "Health check",
            "GET /status": "Pipeline status"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "KRED AI Engine"}

@app.get("/status")
async def pipeline_status():
    """Check if pipeline is initialized"""
    pipeline = get_pipeline()
    return {
        "pipeline_initialized": pipeline is not None,
        "status": "ready" if pipeline else "not_initialized"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_user(request: UserProfileRequest):
    """
    Analyze user's financial behavior and get future projections
    
    Returns:
        - composite_score: Overall financial health score (0-100)
        - risk_level: Risk assessment (low/moderate/high)
        - behavior_score: Spending behavior score (0-100)
        - regret_score: Future regret prediction (0-100)
        - urgency_level: How urgently changes are needed
    """
    try:
        pipeline = get_pipeline()
        
        # Convert request to user profile dict
        user_profile = request.model_dump(exclude={"generate_images"})
        
        # Create mock financial state (since we don't have expenses data)
        financial_state = {
            "daily_limit": request.monthly_spend / 30,
            "spending_volatility": 100,
            "base_limit": request.monthly_spend / 30
        }
        
        print(f"📊 Analyzing user: Age {request.age}, CGPA {request.cgpa}, Spend ₹{request.monthly_spend}")
        
        # Run the pipeline (same as successful test)
        result = pipeline.run(
            user_profile=user_profile,
            expenses=[],  # Empty list - no transaction data
            financial_state=financial_state,
            user_id=999,
            generate_images=request.generate_images
        )
        
        # Extract results
        future_self = result.get("future_self", {})
        behavior = result.get("behavior_analysis", {})
        regret = result.get("lifepath_regret", {})
        
        scores = future_self.get("scores", {})
        
        response = AnalysisResponse(
            status="success",
            composite_score=scores.get("composite", 0),
            risk_level=behavior.get("risk_level", "unknown"),
            behavior_score=behavior.get("behavior_score", 0),
            behavior_profile=behavior.get("behavior_profile", "unknown"),
            regret_score=regret.get("regret_score", 0),
            urgency_level=regret.get("urgency_level", "Low"),
            details={
                "future_scores": {
                    "academic": scores.get("academic"),
                    "financial": scores.get("financial"),
                    "career": scores.get("career"),
                    "lifestyle": scores.get("lifestyle")
                },
                "insights": behavior.get("insights", [])[:3],  # Top 3 insights
                "recommendations": behavior.get("recommendations", [])[:3],  # Top 3 recommendations
                "five_year_regret": regret.get("five_year_regret", ""),
                "redemption_path": regret.get("redemption_path", "")
            }
        )
        
        print(f"✅ Analysis complete: Score={response.composite_score}, Risk={response.risk_level}")
        return response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting KRED AI Engine API...")
    print("📍 Server will run at: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
