def extract_core_data(expenses):
    from collections import defaultdict

    expenses = sorted(expenses, key=lambda e: e.created_at)

    daily_spend = defaultdict(float)

    for e in expenses:
        date = e.created_at.date()
        daily_spend[date] += e.amount

    return {
        "daily_spend": dict(daily_spend),
        "expenses": expenses
    }