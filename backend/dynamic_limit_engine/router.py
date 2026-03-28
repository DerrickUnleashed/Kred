from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from budget_system.db.database import get_db
from .service import get_dynamic_limit

router = APIRouter(prefix="/dynamic-limit", tags=["Dynamic Limit"])


@router.get("/{user_id}")
def fetch_dynamic_limit(user_id: int, db: Session = Depends(get_db)):
    return get_dynamic_limit(user_id, db)