from pydantic import BaseModel
from typing import Dict


class DynamicLimitResponse(BaseModel):
    dynamic_limit: float
    safe_spend_now: float
    status: str

    behavior_factor: float
    context_factor: float
    goal_factor: float

    explanation: Dict[str, str]