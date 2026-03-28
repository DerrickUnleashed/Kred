from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime, timezone
from budget_system.db.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    amount = Column(Float)
    category = Column(String)
    tag = Column(String)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )