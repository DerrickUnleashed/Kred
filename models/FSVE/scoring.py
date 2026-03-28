from __future__ import annotations
import math


# ─── Input Processing ──────────────────────────────────────────────────────────

def process_inputs(raw: dict) -> dict:
    """Normalise all raw inputs into numeric [0–1] scales + keep originals."""
    p = dict(raw)  # copy

    # CGPA → [0,1]
    p["cgpa_norm"] = raw["cgpa"] / 10.0

    # College tier → [0,1]
    p["tier_norm"] = {"Tier 1 (Premier)": 1.0, "Tier 2": 0.6, "Tier 3": 0.3}[raw["college_tier"]]

    # Study hours → [0,1] (cap at 60)
    p["study_norm"] = min(raw["study_hours"] / 60.0, 1.0)

    # Skill level → [0,1]
    p["skill_norm"] = {"Beginner": 0.25, "Intermediate": 0.60, "Advanced": 0.90}[raw["skill_level"]]

    # Experience → [0,1]
    p["exp_norm"] = {"No": 0.0, "Yes (< 6 months)": 0.45, "Yes (6 months+)": 0.85}[raw["has_experience"]]

    # Consistency → [0,1]
    p["consistency_norm"] = {"Low": 0.2, "Medium": 0.55, "High": 0.9}[raw["consistency"]]

    # Savings → [0,1]
    p["savings_norm"] = {"Low": 0.2, "Medium": 0.55, "High": 0.9}[raw["savings_habit"]]

    # Financial discipline → [0,1]
    p["fin_disc_norm"] = {"Impulsive": 0.15, "Balanced": 0.55, "Disciplined": 0.95}[raw["fin_discipline"]]

    # Family income → [0,1]
    p["fam_income_norm"] = {"Low": 0.2, "Middle": 0.55, "High": 0.9}[raw["family_income"]]

    # Monthly spend relative proxy → inverse of excess (crude)
    # Higher spend with low income background = worse
    p["spend_risk"] = min(raw["monthly_spend"] / 30000.0, 1.0)

    # Lifestyle
    p["screen_norm"]  = {"Low (< 3 h)": 0.9, "Medium (3–6 h)": 0.55, "High (> 6 h)": 0.2}[raw["screen_time"]]
    p["health_norm"]  = {"Poor": 0.2, "Average": 0.55, "Good": 0.9}[raw["health_habits"]]
    p["sleep_norm"]   = {"Poor": 0.2, "Average": 0.55, "Good": 0.9}[raw["sleep_quality"]]

    # Location factor
    p["location_norm"] = {"Metro City": 0.85, "Tier-2 City": 0.6, "Small Town / Rural": 0.35}[raw["location"]]

    # Age-adjusted potential (younger = more runway)
    p["age_potential"] = max(0.0, (35 - raw["age"]) / 20.0)

    return p


# ─── Score Computation ─────────────────────────────────────────────────────────

def compute_scores(p: dict) -> dict:
    """
    Four domain scores (0–100) + weighted composite.

    Academic  (30%): CGPA, tier, study hours
    Financial (25%): savings, discipline, family bg, spend risk
    Career    (25%): skill, experience, consistency
    Lifestyle (20%): health, sleep, screen time
    """
    academic = (
        p["cgpa_norm"]   * 0.50 +
        p["tier_norm"]   * 0.30 +
        p["study_norm"]  * 0.20
    ) * 100

    financial = (
        p["savings_norm"]    * 0.30 +
        p["fin_disc_norm"]   * 0.35 +
        p["fam_income_norm"] * 0.20 +
        (1 - p["spend_risk"]) * 0.15
    ) * 100

    career = (
        p["skill_norm"]       * 0.40 +
        p["exp_norm"]         * 0.35 +
        p["consistency_norm"] * 0.25
    ) * 100

    lifestyle = (
        p["health_norm"] * 0.40 +
        p["sleep_norm"]  * 0.35 +
        p["screen_norm"] * 0.25
    ) * 100

    composite = (
        academic  * 0.30 +
        financial * 0.25 +
        career    * 0.25 +
        lifestyle * 0.20
    )

    return {
        "academic":  round(academic,  1),
        "financial": round(financial, 1),
        "career":    round(career,    1),
        "lifestyle": round(lifestyle, 1),
        "composite": round(composite, 1),
    }


# ─── Behavior Analysis ────────────────────────────────────────────────────────

def analyze_behavior(scores: dict) -> dict:
    c = scores["composite"]

    risk_level = "Low" if c > 75 else ("Moderate" if c >= 50 else "High")
    profile    = "Disciplined" if c > 75 else ("Balanced" if c >= 50 else "At Risk")

    # Trend based on whether career + academic are both strong or not
    academic_ok = scores["academic"]  >= 65
    career_ok   = scores["career"]    >= 60
    fin_ok      = scores["financial"] >= 55

    improving_signals = sum([academic_ok, career_ok, fin_ok])
    trend = "Improving" if improving_signals >= 3 else ("Stable" if improving_signals == 2 else "Declining")

    # Weakest domain
    domain_map = {
        "Academic":  scores["academic"],
        "Financial": scores["financial"],
        "Career":    scores["career"],
        "Lifestyle": scores["lifestyle"],
    }
    weakest = min(domain_map, key=domain_map.get)
    strongest = max(domain_map, key=domain_map.get)

    return {
        "risk_level":  risk_level,
        "profile":     profile,
        "trend":       trend,
        "weakest":     weakest,
        "strongest":   strongest,
        "composite":   scores["composite"],
    }


# ─── Future Simulation ────────────────────────────────────────────────────────

def simulate_future(p: dict, scores: dict, behavior: dict) -> dict:
    """
    Project scores and outcomes at 5, 10, and 25 year horizons.
    Simple compound growth / decay model based on behavioral trajectory.
    """
    c   = scores["composite"] / 100.0
    age = p["age"]

    def _project(base_score: float, years: int, trend: str, boost: float = 0.0) -> float:
        rate = {
            "Improving": 0.025,
            "Stable":    0.005,
            "Declining": -0.020,
        }[trend]
        raw = base_score * ((1 + rate + boost) ** years)
        return min(100.0, max(0.0, round(raw, 1)))

    trend = behavior["trend"]

    results = {}
    for years, label in [(5, "5_year"), (10, "10_year"), (25, "25_year")]:
        proj_academic  = _project(scores["academic"],  years, trend, 0.01 * p["study_norm"])
        proj_financial = _project(scores["financial"], years, trend, 0.01 * p["fin_disc_norm"])
        proj_career    = _project(scores["career"],    years, trend, 0.015 * p["consistency_norm"])
        proj_lifestyle = _project(scores["lifestyle"], years, trend)
        proj_composite = round(
            proj_academic * 0.30 + proj_financial * 0.25 +
            proj_career   * 0.25 + proj_lifestyle * 0.20, 1
        )
        future_age = age + years

        # Qualitative outcomes
        career_stability = _label(proj_career, ["Unstable", "Emerging", "Stable", "Strong", "Elite"])
        fin_condition    = _label(proj_financial, ["Struggling", "Tight", "Moderate", "Comfortable", "Wealthy"])
        lifestyle_qual   = _label(proj_lifestyle, ["Poor", "Below Average", "Average", "Good", "Excellent"])

        # Estimated income band (very rough — illustrative)
        base_income = {
            "Engineering / Technology": 6,
            "Science": 5, "Commerce / Business": 5,
            "Arts / Humanities": 3, "Medicine / Healthcare": 7,
            "Law": 5, "Other": 4,
        }.get(p["field_of_study"], 4)

        skill_mult = p["skill_norm"] * 1.5 + 0.5
        tier_mult  = p["tier_norm"]
        years_mult = (1.08 ** years)  # 8% annual growth proxy
        score_mult = proj_composite / 65.0
        income_lpa = round(base_income * skill_mult * (0.5 + tier_mult * 0.5) * years_mult * score_mult, 1)

        results[label] = {
            "years":            years,
            "future_age":       future_age,
            "academic":         proj_academic,
            "financial":        proj_financial,
            "career":           proj_career,
            "lifestyle":        proj_lifestyle,
            "composite":        proj_composite,
            "career_stability": career_stability,
            "fin_condition":    fin_condition,
            "lifestyle_qual":   lifestyle_qual,
            "income_lpa":       income_lpa,
        }

    return results


def _label(score: float, labels: list[str]) -> str:
    idx = min(int(score / 20), len(labels) - 1)
    return labels[idx]
