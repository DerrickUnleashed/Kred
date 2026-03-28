def compute_budget_health(remaining_ratio, impulsive_ratio, adherence_score):
    w1, w2, w3 = 0.4, 0.3, 0.3

    health = (
        w1 * remaining_ratio +
        w2 * (1 - impulsive_ratio) +
        w3 * adherence_score
    ) * 100

    return round(health, 2)