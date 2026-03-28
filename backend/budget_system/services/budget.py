def generate_daily_limit(income: float):
    savings_ratio = 0.2
    usable_income = income * (1 - savings_ratio)
    return round(usable_income / 30, 2)