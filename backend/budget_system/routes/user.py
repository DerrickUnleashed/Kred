from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from budget_system.db.database import get_db
from budget_system.models.user import User
from budget_system.services.budget import generate_daily_limit

router = APIRouter()

@router.post("/setup")
def setup_user(income: float, db: Session = Depends(get_db)):
    daily_limit = generate_daily_limit(income)

    user = User(monthly_income=income, daily_limit=daily_limit)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "daily_limit": user.daily_limit
    }