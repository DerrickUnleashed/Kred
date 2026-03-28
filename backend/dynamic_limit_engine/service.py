from sqlalchemy.orm import Session

from budget_system.services.state import get_user_financial_state
from .engine import compute_dynamic_limit


def get_dynamic_limit(user_id: int, db: Session):
    state = get_user_financial_state(user_id, db)

    if not state:
        return {"error": "User not found"}

    return compute_dynamic_limit(state)