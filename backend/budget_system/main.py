from fastapi import FastAPI
from budget_system.models import planned
from budget_system.db.database import engine, Base
from budget_system.routes import user, expense

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(user.router)
app.include_router(expense.router)