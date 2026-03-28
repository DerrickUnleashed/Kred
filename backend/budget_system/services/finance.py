from datetime import datetime, timezone
from budget_system.models.expense import Expense

def calculate_today_spent(db, user_id):
    today = datetime.now(timezone.utc).date()
    
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.created_at >= today
    ).all()

    return sum(e.amount for e in expenses)