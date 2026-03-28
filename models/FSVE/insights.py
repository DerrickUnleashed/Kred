from __future__ import annotations


def build_insights_and_recommendations(
    processed: dict,
    scores: dict,
    behavior: dict,
    simulation: dict,
    llm_output: dict,
) -> dict:
    """
    Consolidate rule-based + LLM-based insights into a single structured dict
    used by the UI recommendation panel.
    """
    ins_json = llm_output.get("insights_json", {})

    # ── Rule-based fallback insights ──────────────────────────────────────────
    academic_risk = ins_json.get("academic_risk") or _academic_risk(processed, scores)
    fin_risk      = ins_json.get("financial_risk") or _financial_risk(processed, scores)
    career_sig    = ins_json.get("career_signal")  or _career_signal(processed, scores)
    ls_warn       = ins_json.get("lifestyle_warning") or _lifestyle_warning(processed, scores)

    recs = ins_json.get("recommendations") or _fallback_recommendations(processed, scores, behavior)

    # ── Priority actions ──────────────────────────────────────────────────────
    improvement_priority = ins_json.get("improvement_priority") or behavior["weakest"]

    return {
        "academic_risk":   academic_risk,
        "financial_risk":  fin_risk,
        "career_signal":   career_sig,
        "lifestyle_warning": ls_warn,
        "top_strength":    ins_json.get("top_strength", behavior["strongest"] + " habits"),
        "top_threat":      ins_json.get("top_threat",   behavior["weakest"]  + " deficit"),
        "improvement_priority": improvement_priority,
        "recommendations": recs,
    }


# ─── Rule-based Fallbacks ─────────────────────────────────────────────────────

def _academic_risk(p: dict, s: dict) -> str:
    score = s["academic"]
    if score >= 75:
        return "Academic foundation is strong — maintain consistency to sustain this advantage."
    elif score >= 50:
        return f"CGPA of {p['cgpa']} combined with {p['study_hours']} study hours/week signals inconsistency risk."
    else:
        return f"Critical academic risk: {p['cgpa']} CGPA from a {p['college_tier']} institution limits early opportunities."


def _financial_risk(p: dict, s: dict) -> str:
    score = s["financial"]
    if score >= 75:
        return "Disciplined financial behavior is your long-term moat — protect this habit."
    elif score >= 50:
        return f"{p['fin_discipline']} financial discipline with {p['savings_habit']} savings creates volatility risk."
    else:
        return f"High financial fragility: impulsive spending + low savings compounds wealth loss over time."


def _career_signal(p: dict, s: dict) -> str:
    score = s["career"]
    exp   = p["has_experience"]
    skill = p["skill_level"]
    if score >= 70:
        return f"{skill} skill level with {exp} is a strong early-career signal for {p['target_career']}."
    elif score >= 45:
        return f"Career trajectory for {p['target_career']} is nascent — skill gaps need targeted bridging."
    else:
        return f"Stagnation risk: Beginner-level skills with no experience severely limits entry into {p['target_career']}."


def _lifestyle_warning(p: dict, s: dict) -> str:
    score = s["lifestyle"]
    if score >= 70:
        return "Healthy lifestyle habits are compounding positively — energy and focus will sustain performance."
    elif score >= 45:
        return f"Mixed habits: {p['health_habits']} health + {p['sleep_quality']} sleep creates cognitive overhead."
    else:
        return f"Critical: poor health + poor sleep + high screen time is a silent performance tax accelerating burnout."


def _fallback_recommendations(p: dict, s: dict, b: dict) -> list:
    recs = [
        {
            "area":   "Academic",
            "action": f"Increase weekly study hours to at least 35 with spaced repetition. Target CGPA ≥ 8.",
            "impact": "High" if s["academic"] < 65 else "Medium",
        },
        {
            "area":   "Financial",
            "action": "Automate ₹500–₹2000/month into a liquid mutual fund before spending anything.",
            "impact": "High" if s["financial"] < 60 else "Medium",
        },
        {
            "area":   "Career",
            "action": f"Commit to one domain project or open-source contribution to build a {p['target_career']} portfolio.",
            "impact": "High",
        },
        {
            "area":   "Lifestyle",
            "action": "Fix your sleep window to 10:30 PM–6:30 AM. No screens 45 minutes before bed.",
            "impact": "High" if s["lifestyle"] < 60 else "Medium",
        },
        {
            "area":   "Mindset",
            "action": "Track one measurable daily habit using a simple journal for 30 days.",
            "impact": "Medium",
        },
    ]
    return recs
