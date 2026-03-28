from collections import defaultdict


def analyze_categories(core):
    expenses = core["expenses"]

    category_totals = defaultdict(float)

    for e in expenses:
        category_totals[e.category] += e.amount

    total = sum(category_totals.values())

    result = []

    for cat, amt in category_totals.items():
        percentage = amt / total if total else 0

        risk = "high" if percentage > 0.4 else "normal"

        result.append({
            "category": cat,
            "percentage": round(percentage, 2),
            "risk": risk
        })

    return result