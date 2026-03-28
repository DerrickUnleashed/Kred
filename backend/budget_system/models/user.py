from sqlalchemy import Column, Integer, Float
from budget_system.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    monthly_income = Column(Float)
    daily_limit = Column(Float)