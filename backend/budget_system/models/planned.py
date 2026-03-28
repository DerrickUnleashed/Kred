from sqlalchemy import Column, Integer, Float, Date
from budget_system.db.database import Base

class PlannedExpense(Base):
    __tablename__ = "planned_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    amount = Column(Float)
    date = Column(Date)