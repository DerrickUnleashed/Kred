def analyze_category(limit, spent):
    if limit == 0:
        return {"status": "no_budget"}

    usage = spent / limit

    if usage > 0.9:
        return {
            "status": "critical",
            "action": "Stop spending in this category"
        }
    elif usage > 0.7:
        return {
            "status": "warning",
            "action": "Reduce spending"
        }
    else:
        return {
            "status": "safe",
            "action": "Spending is under control"
        }