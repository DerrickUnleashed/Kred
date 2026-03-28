from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from budget_system.db.database import get_db
from budget_system.models.expense import Expense
from budget_system.models.user import User
from budget_system.services.finance import calculate_today_spent
from budget_system.services.insights import (
    impulsive_ratio,
    impulsive_streak,
    impulsive_time_pattern,
    worst_category,
    savings_suggestion
)
from budget_system.services.prediction import (
    predict_daily_overspend,
    predict_monthly_runout,
    spending_trend
)
from datetime import datetime, timezone
from datetime import date
from budget_system.models.planned import PlannedExpense
from budget_system.services.adaptive import calculate_adaptive_limit
router = APIRouter()


# 🔹 1. Add Expense (buttons / manual)
@router.post("/expense")
def add_expense(user_id: int, amount: float, category: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    spent = calculate_today_spent(db, user_id)
    remaining = round(user.daily_limit - spent, 2)

    return {
        "expense_id": expense.id,
        "remaining_today": remaining
    }


# 🔹 2. Add Expense via TEXT (voice + typing)
@router.post("/expense/text")
def add_expense_text(user_id: int, input_text: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    words = input_text.lower().split()

    amount = None
    category = "other"

    # Extract amount
    for w in words:
        if w.replace(".", "", 1).isdigit():
            amount = float(w)

    # Category detection
    if any(word in words for word in ["coffee", "food", "lunch", "dinner"]):
        category = "food"
    elif any(word in words for word in ["uber", "bus", "auto", "taxi"]):
        category = "transport"
    elif any(word in words for word in ["movie", "shopping", "amazon"]):
        category = "entertainment"

    if amount is None:
        raise HTTPException(status_code=400, detail="Amount not found")

    expense = Expense(
        user_id=user_id,
        amount=amount,
        category=category
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    spent = calculate_today_spent(db, user_id)
    remaining = round(user.daily_limit - spent, 2)

    return {
        "expense_id": expense.id,
        "category": category,
        "amount": amount,
        "remaining_today": remaining
    }


# 🔹 3. Swipe (ESSENTIAL vs IMPULSIVE)
@router.post("/expense/swipe")
def swipe(expense_id: int, tag: str, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if tag not in ["essential", "impulsive"]:
        raise HTTPException(status_code=400, detail="Invalid tag")

    expense.tag = tag
    db.commit()

    return {
        "message": "updated",
        "tag": tag
    }


# 🔹 4. Dashboard
@router.get("/dashboard/{user_id}")
def dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔥 NEW: adaptive limit
    adaptive_limit = calculate_adaptive_limit(user, db, PlannedExpense)

    spent = calculate_today_spent(db, user_id)
    remaining = round(adaptive_limit - spent, 2)

    return {
        "base_daily_limit": user.daily_limit,
        "adaptive_daily_limit": adaptive_limit,
        "spent_today": spent,
        "remaining": remaining
    }


# 🔹 5. Insights (UPGRADED 🔥)
@router.get("/insights/{user_id}")
def insights(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    expenses = db.query(Expense).filter(
        Expense.user_id == user_id
    ).order_by(Expense.created_at).all()

    ratio = impulsive_ratio(expenses)
    streak = impulsive_streak(expenses)
    time_pattern = impulsive_time_pattern(expenses)
    category = worst_category(expenses)
    saving_tip = savings_suggestion(expenses)

    insights_list = []

    # Base insight
    insights_list.append(f"{ratio}% of your spending is impulsive")

    if streak >= 2:
        insights_list.append(f"You've made {streak} impulsive spends in a row")

    if time_pattern:
        insights_list.append(time_pattern)

    if category:
        insights_list.append(f"{category.capitalize()} has the highest impulsive spending")

    if saving_tip:
        insights_list.append(saving_tip)

    # 🔮 PREDICTIONS

    # Today's expenses
    today = datetime.now(timezone.utc).date()
    today_expenses = [e for e in expenses if e.created_at.date() == today]

    pred1 = predict_daily_overspend(user, today_expenses)
    if pred1:
        insights_list.append(pred1)

    total_spent = sum(e.amount for e in expenses)
    pred2 = predict_monthly_runout(user, total_spent)
    if pred2:
        insights_list.append(pred2)

    pred3 = spending_trend(expenses)
    if pred3:
        insights_list.append(pred3)

    return {
        "insights": insights_list
    }
    
@router.post("/planned")
def add_planned_expense(user_id: int, amount: float, planned_date: date, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    planned = PlannedExpense(
        user_id=user_id,
        amount=amount,
        date=planned_date
    )

    db.add(planned)
    db.commit()

    # 🔥 Recalculate adaptive limit
    new_limit = calculate_adaptive_limit(user, db, PlannedExpense)

    return {
        "message": "Planned expense added",
        "new_daily_limit": new_limit
    }