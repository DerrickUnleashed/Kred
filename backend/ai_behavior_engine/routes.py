from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.budget_system.db.database import get_db
from .service import analyze_user_behavior

router = APIRouter(prefix="/ai-behavior", tags=["AI Behavior"])


@router.get("/{user_id}")
def get_behavior_analysis(user_id: int, db: Session = Depends(get_db)):
    result = analyze_user_behavior(user_id, db)
    return result