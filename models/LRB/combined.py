import os
import json
import math
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

st.set_page_config(
    page_title="Student Life Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e6e1;
    font-family: 'DM Mono', monospace;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0d1117 0%, #0a0a0f 60%);
}

[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid #1e1e2e;
}

[data-testid="stSidebar"] * { color: #c9c7c0 !important; }

h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f5c842 0%, #ff6b35 50%, #e8e6e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}

.sub-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #5a5a6e;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 6px;
}

.score-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.score-card:hover { border-color: #2e2e4e; }
.score-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.score-card.good::before { background: linear-gradient(90deg, #22c55e, #16a34a); }
.score-card.warn::before { background: linear-gradient(90deg, #f5c842, #f59e0b); }
.score-card.bad::before  { background: linear-gradient(90deg, #ef4444, #dc2626); }
.score-card.info::before { background: linear-gradient(90deg, #3b82f6, #6366f1); }

.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #5a5a6e;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.score-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #e8e6e1;
    line-height: 1;
}
.score-sub {
    font-size: 0.72rem;
    color: #5a5a6e;
    margin-top: 6px;
    font-family: 'DM Mono', monospace;
}

.metric-row {
    display: flex;
    gap: 16px;
    margin: 16px 0;
    flex-wrap: wrap;
}
.metric-chip {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 10px 16px;
    flex: 1;
    min-width: 140px;
}
.metric-chip-label {
    font-size: 0.65rem;
    color: #5a5a6e;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.metric-chip-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f5c842;
    margin-top: 4px;
}

.regret-card {
    background: linear-gradient(135deg, #110a0a, #1a0d0d);
    border: 1px solid #3d1515;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
}
.regret-amount {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #ef4444;
}
.regret-label {
    font-size: 0.75rem;
    color: #9a6a6a;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.insight-block {
    background: #0f0f1a;
    border-left: 3px solid #f5c842;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 12px 0;
    font-size: 0.88rem;
    color: #c9c7c0;
    line-height: 1.7;
}
.insight-block.red { border-left-color: #ef4444; }
.insight-block.green { border-left-color: #22c55e; }
.insight-block.blue { border-left-color: #3b82f6; }

.profile-badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 999px;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.profile-disciplined { background: #052e16; color: #22c55e; border: 1px solid #166534; }
.profile-balanced    { background: #1c1a07; color: #f5c842; border: 1px solid #713f12; }
.profile-impulsive   { background: #1c0a07; color: #f97316; border: 1px solid #7c2d12; }
.profile-at-risk     { background: #1c0707; color: #ef4444; border: 1px solid #7f1d1d; }

.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e6e1;
    margin: 24px 0 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-heading::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e1e2e;
}

.final-statement {
    background: linear-gradient(135deg, #0f0e1a, #130f0a);
    border: 1px solid #2e2520;
    border-radius: 14px;
    padding: 28px 32px;
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #f5c842;
    line-height: 1.6;
    text-align: center;
    margin: 20px 0;
    position: relative;
}
.final-statement::before {
    content: '"';
    position: absolute;
    top: 10px; left: 20px;
    font-size: 3rem;
    color: #2e2520;
    font-family: Georgia, serif;
    line-height: 1;
}

.rec-item {
    background: #0d120d;
    border: 1px solid #1a2e1a;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.85rem;
    color: #c9c7c0;
    line-height: 1.6;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}
.rec-num {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    color: #22c55e;
    background: #052e16;
    border-radius: 4px;
    padding: 2px 7px;
    flex-shrink: 0;
    margin-top: 2px;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0d0d14;
    border-bottom: 1px solid #1e1e2e;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #5a5a6e;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 12px 20px;
    border: none;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    color: #f5c842 !important;
    border-bottom: 2px solid #f5c842 !important;
    background: transparent !important;
}

.stButton > button {
    background: linear-gradient(135deg, #f5c842, #ff6b35);
    color: #0a0a0f;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    border: none;
    border-radius: 8px;
    padding: 14px 28px;
    width: 100%;
    cursor: pointer;
    letter-spacing: 0.04em;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.9; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: #0d0d14 !important;
    border: 1px solid #1e1e2e !important;
    color: #e8e6e1 !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 6px !important;
}

.stSlider > div > div > div { background: #1e1e2e; }

[data-testid="stExpander"] {
    background: #0d0d14;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
}

hr { border-color: #1e1e2e !important; }

div[data-testid="stMarkdownContainer"] p {
    color: #c9c7c0;
    font-family: 'DM Mono', monospace;
    font-size: 0.88rem;
    line-height: 1.7;
}

.urgency-critical { color: #ef4444; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; }
.urgency-high     { color: #f97316; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; }
.urgency-medium   { color: #f5c842; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; }
.urgency-low      { color: #22c55e; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

SKILL_MAP = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}

def safe_div(n, d, fb=0.0):
    return n / d if d != 0 else fb

class DataNormalizer:
    DEFAULTS = {
        "Full_Name": "Student", "Age": 20, "Gender": "Male", "Country": "India",
        "Education_Level": "Undergraduate", "Field_of_Study": "Computer Science",
        "Institution_Tier": 2, "CGPA": 7.0, "Study_Hours": 15,
        "Target_Career": "Software Developer", "Skill_Level": "Intermediate",
        "Internships": 0, "Consistency": 5,
        "Monthly_Income": 0, "Fixed_Expenses": 0, "Variable_Expenses": 0,
        "Weekly_Spending": 500, "Current_Savings": 0, "Savings_Target": 50000,
        "Savings_Duration": 12, "Family_Income": 30000, "Earning_Members": 1,
        "Dependents": 2, "Father_Occupation": "Unknown", "Mother_Occupation": "Homemaker",
        "Family_Support": 0, "Family_Responsibility": 0,
        "Screen_Time": 4, "Sleep_Duration": 7.0, "Sleep_Quality": 6,
        "Health_Score": 6, "Sick_Days": 1, "Medical_Expenses": 500,
    }

    @staticmethod
    def normalize(raw: dict) -> dict:
        data = DataNormalizer.DEFAULTS.copy()
        data.update({k: v for k, v in raw.items() if v is not None})
        data["Monthly_Income"] = max(float(data["Monthly_Income"]), 0)
        data["Fixed_Expenses"] = max(float(data["Fixed_Expenses"]), 0)
        data["Variable_Expenses"] = max(float(data["Variable_Expenses"]), 0)
        data["Weekly_Spending"] = max(float(data["Weekly_Spending"]), 0)
        data["Current_Savings"] = max(float(data["Current_Savings"]), 0)
        data["Savings_Target"] = max(float(data["Savings_Target"]), 1)
        data["CGPA"] = max(0.0, min(10.0, float(data["CGPA"])))
        data["Sleep_Duration"] = max(0.0, min(24.0, float(data["Sleep_Duration"])))
        data["Screen_Time"] = max(0.0, min(24.0, float(data["Screen_Time"])))
        data["Health_Score"] = max(0, min(10, int(data["Health_Score"])))
        data["Sleep_Quality"] = max(0, min(10, int(data["Sleep_Quality"])))
        data["Consistency"] = max(0, min(10, int(data["Consistency"])))
        data["Earning_Members"] = max(1, int(data["Earning_Members"]))
        data["Dependents"] = max(0, int(data["Dependents"]))
        data["Institution_Tier"] = max(1, min(5, int(data["Institution_Tier"])))
        data["Internships"] = max(0, int(data["Internships"]))
        data["Sick_Days"] = max(0, int(data["Sick_Days"]))
        return data

def _norm(v, lo, hi, invert=False):
    c = max(lo, min(hi, v))
    r = safe_div(c - lo, hi - lo, 0.5)
    return (1 - r) * 100 if invert else r * 100

class ScoringEngine:
    @staticmethod
    def academic(d):
        cgpa = _norm(d["CGPA"], 0, 10)
        study = _norm(d["Study_Hours"], 0, 40)
        tier = _norm(d["Institution_Tier"], 1, 5, invert=True)
        consistency = _norm(d["Consistency"], 0, 10)
        return round(cgpa * 0.40 + study * 0.30 + tier * 0.15 + consistency * 0.15, 2)

    @staticmethod
    def financial(d):
        income = max(d["Monthly_Income"] + d["Family_Support"], 1)
        total_exp = d["Fixed_Expenses"] + d["Variable_Expenses"] + d["Weekly_Spending"] * 4.33
        monthly_save = max(income - total_exp - d["Family_Responsibility"], 0)
        savings_rate = safe_div(monthly_save, income) * 100
        expense_ratio = safe_div(total_exp, income) * 100
        burn = safe_div(d["Variable_Expenses"] + d["Weekly_Spending"] * 4.33, income) * 100
        progress = safe_div(d["Current_Savings"], d["Savings_Target"]) * 100
        dep_ratio = safe_div(d["Dependents"], d["Earning_Members"]) * 100

        sr = _norm(savings_rate, 0, 50)
        er = _norm(expense_ratio, 0, 100, invert=True)
        br = _norm(burn, 0, 100, invert=True)
        pr = _norm(progress, 0, 100)
        dr = _norm(dep_ratio, 0, 300, invert=True)
        return round(sr * 0.30 + er * 0.20 + br * 0.20 + pr * 0.15 + dr * 0.15, 2)

    @staticmethod
    def career(d):
        skill = _norm(SKILL_MAP.get(d["Skill_Level"], 1), 1, 4)
        intern_ = _norm(d["Internships"], 0, 5)
        cons = _norm(d["Consistency"], 0, 10)
        study = _norm(d["Study_Hours"], 0, 40)
        cgpa = _norm(d["CGPA"], 0, 10)
        return round(skill * 0.35 + intern_ * 0.25 + cons * 0.20 + study * 0.10 + cgpa * 0.10, 2)

    @staticmethod
    def lifestyle(d):
        sleep_dev = abs(d["Sleep_Duration"] - 7.5)
        sd = _norm(sleep_dev, 0, 4, invert=True)
        sq = _norm(d["Sleep_Quality"], 0, 10)
        hs = _norm(d["Health_Score"], 0, 10)
        sc = _norm(d["Screen_Time"], 0, 16, invert=True)
        sick = _norm(d["Sick_Days"], 0, 30, invert=True)
        med = _norm(safe_div(d["Medical_Expenses"], max(d["Monthly_Income"], 1)) * 100, 0, 50, invert=True)
        return round(sd * 0.20 + sq * 0.20 + hs * 0.25 + sc * 0.20 + sick * 0.10 + med * 0.05, 2)

    @staticmethod
    def behavior(a, f, c, l):
        return round(a * 0.30 + f * 0.25 + c * 0.25 + l * 0.20, 2)


class FinancialEngine:
    @staticmethod
    def compute(d):
        income = max(d["Monthly_Income"] + d["Family_Support"], 1)
        total_exp = d["Fixed_Expenses"] + d["Variable_Expenses"] + d["Weekly_Spending"] * 4.33
        resp = d["Family_Responsibility"]
        net_save = max(income - total_exp - resp, 0)
        savings_rate = safe_div(net_save, income) * 100
        expense_ratio = safe_div(total_exp, income) * 100
        burn = safe_div(d["Variable_Expenses"] + d["Weekly_Spending"] * 4.33, income) * 100
        dep_ratio = safe_div(d["Dependents"], d["Earning_Members"])
        wealth_potential = safe_div(net_save * 12, income * 12) * 100
        months_needed = max(d["Savings_Target"] - d["Current_Savings"], 0)
        mts = math.ceil(safe_div(months_needed, net_save, 99999)) if net_save > 0 else 99999

        return {
            "effective_income": round(income, 2),
            "total_monthly_expenses": round(total_exp, 2),
            "monthly_savings": round(net_save, 2),
            "savings_rate_pct": round(savings_rate, 2),
            "expense_ratio_pct": round(expense_ratio, 2),
            "burn_rate_pct": round(burn, 2),
            "dependency_ratio": round(dep_ratio, 2),
            "wealth_accumulation_potential_pct": round(wealth_potential, 2),
            "months_to_savings_target": mts if mts < 99999 else "Never at current rate",
            "disposable_income": round(income - total_exp - resp, 2),
            "family_responsibility_load_pct": round(safe_div(resp, income) * 100, 2),
        }


class ProjectionEngine:
    @staticmethod
    def project(d, fin, years=(5, 10, 20, 30)):
        ms = fin["monthly_savings"]
        cs = d["Current_Savings"]
        r = 0.08 / 12
        result = {}
        for y in years:
            m = y * 12
            fv = ms * (((1 + r) ** m - 1) / r) + cs * (1 + r) ** m if r > 0 else ms * m + cs
            result[y] = round(fv, 2)

        opt_ms = max(d["Monthly_Income"] * 0.20, ms * 1.5, ms + 1000)
        opt = {}
        for y in years:
            m = y * 12
            fv = opt_ms * (((1 + r) ** m - 1) / r) + cs * (1 + r) ** m if r > 0 else opt_ms * m + cs
            opt[y] = round(fv, 2)

        age_now = d["Age"]
        career_milestones = []
        for y in years:
            age = age_now + y
            income_mult = 1 + (d["Consistency"] / 10) * 0.15 * y
            proj_income = d["Monthly_Income"] * income_mult
            career_milestones.append({"year": y, "age": age, "projected_monthly_income": round(proj_income, 0)})

        return {
            "current_behavior_wealth": result,
            "optimized_behavior_wealth": opt,
            "career_milestones": career_milestones,
            "optimized_monthly_savings_used": round(opt_ms, 2),
        }


class RegretEngine:
    @staticmethod
    def compute(d, fin):
        income = max(d["Monthly_Income"], 1)
        years = 35
        r_high = 0.12
        r_mid = 0.10

        weekly_annual = d["Weekly_Spending"] * 52
        disc_regret = weekly_annual * (((1 + r_high) ** years - 1) / r_high)

        screen_prod_loss_pct = min(max(d["Screen_Time"] - 3, 0) * 0.04, 0.40)
        screen_annual_loss = income * 12 * screen_prod_loss_pct
        screen_compounded = screen_annual_loss * (((1 + r_mid) ** years - 1) / r_mid)

        sleep_deficit = max(7.5 - d["Sleep_Duration"], 0)
        sleep_quality_gap = max(8 - d["Sleep_Quality"], 0) / 10
        sleep_drag = min(sleep_deficit * 0.06 + sleep_quality_gap * 0.03, 0.40)
        sleep_annual_loss = income * 12 * sleep_drag
        sleep_compounded = sleep_annual_loss * years

        cgpa_gap = max(9.0 - d["CGPA"], 0)
        skill_gap = max(3 - SKILL_MAP.get(d["Skill_Level"], 1), 0)
        career_drag = (cgpa_gap * 0.025 + skill_gap * 0.05 + max(2 - d["Internships"], 0) * 0.03)
        career_annual_loss = income * 12 * career_drag
        career_compounded = career_annual_loss * years

        health_drag = max(8 - d["Health_Score"], 0) * 0.015
        sick_drag = d["Sick_Days"] * 0.003
        health_total_drag = min(health_drag + sick_drag, 0.30)
        health_annual_loss = income * 12 * health_total_drag
        health_compounded = health_annual_loss * years

        late_start_years = max(d["Age"] - 18, 0)
        fv_missed = d["Weekly_Spending"] * 52 * (((1 + r_high) ** late_start_years - 1) / r_high) if late_start_years > 0 else 0

        total_regret = disc_regret + screen_compounded + sleep_compounded + career_compounded + health_compounded

        return {
            "discretionary_spending_regret": round(disc_regret, 2),
            "screen_time_wealth_loss": round(screen_compounded, 2),
            "sleep_deficit_income_loss": round(sleep_compounded, 2),
            "career_gap_wealth_loss": round(career_compounded, 2),
            "health_negligence_loss": round(health_compounded, 2),
            "late_investing_opportunity_loss": round(fv_missed, 2),
            "total_lifetime_regret_cost": round(total_regret, 2),
            "monthly_regret_equivalent": round(safe_div(total_regret, years * 12), 2),
            "screen_productivity_drag_pct": round(screen_prod_loss_pct * 100, 2),
            "sleep_productivity_drag_pct": round(sleep_drag * 100, 2),
            "career_drag_pct": round(career_drag * 100, 2),
            "health_drag_pct": round(health_total_drag * 100, 2),
            "projection_years": years,
        }


class BehavioralEngine:
    @staticmethod
    def classify(d, fin, scores):
        flags = []
        income = max(d["Monthly_Income"], 1)

        if fin["expense_ratio_pct"] > 85:
            flags.append(("OVERSPENDING", "critical"))
        elif fin["expense_ratio_pct"] > 70:
            flags.append(("OVERSPENDING", "high"))

        if d["Consistency"] < 4:
            flags.append(("LOW_EFFORT", "high"))
        elif d["Consistency"] < 6:
            flags.append(("LOW_EFFORT", "medium"))

        if d["Screen_Time"] > 8:
            flags.append(("EXCESSIVE_SCREEN_TIME", "critical"))
        elif d["Screen_Time"] > 6:
            flags.append(("EXCESSIVE_SCREEN_TIME", "high"))

        if d["Sleep_Duration"] < 6:
            flags.append(("POOR_SLEEP", "critical"))
        elif d["Sleep_Duration"] < 7:
            flags.append(("POOR_SLEEP", "high"))

        if d["Health_Score"] < 4:
            flags.append(("POOR_HEALTH", "critical"))
        elif d["Health_Score"] < 6:
            flags.append(("POOR_HEALTH", "medium"))

        if fin["savings_rate_pct"] < 5:
            flags.append(("ZERO_SAVINGS_HABIT", "critical"))
        elif fin["savings_rate_pct"] < 15:
            flags.append(("LOW_SAVINGS", "high"))

        if SKILL_MAP.get(d["Skill_Level"], 1) <= 1 and d["Internships"] == 0:
            flags.append(("STAGNANT_CAREER", "critical"))

        if d["CGPA"] < 6.0:
            flags.append(("LOW_ACADEMIC_PERFORMANCE", "high"))

        critical_count = sum(1 for _, sev in flags if sev == "critical")
        high_count = sum(1 for _, sev in flags if sev == "high")

        score = scores["behavior"]
        fin_s = scores["financial"]
        career_s = scores["career"]
        life_s = scores["lifestyle"]

        avg3 = (fin_s + career_s + life_s) / 3
        if avg3 >= 70 and critical_count == 0:
            profile = "Disciplined"
        elif avg3 >= 55 and critical_count <= 1:
            profile = "Balanced"
        elif avg3 >= 38 or (critical_count <= 2 and high_count <= 2):
            profile = "Impulsive"
        else:
            profile = "At Risk"

        if critical_count >= 3 or score < 30:
            urgency = "Critical"
        elif critical_count >= 2 or score < 45:
            urgency = "High"
        elif critical_count >= 1 or score < 60:
            urgency = "Medium"
        else:
            urgency = "Low"

        peer = "Above Average" if score >= 72 else ("Average" if score >= 50 else "Below Average")

        opp_costs = {
            "skill_upgrade_annual_gain": round(max(3 - SKILL_MAP.get(d["Skill_Level"], 1), 0) * income * 12 * 0.12, 2),
            "uninvested_savings_returns": round(d["Current_Savings"] * 0.08, 2),
            "screen_time_freelance_loss": round(max(d["Screen_Time"] - 3, 0) * 365 * safe_div(income, 22 * 8) * 0.15, 2),
            "internship_gap_loss": round(max(2 - d["Internships"], 0) * income * 2, 2),
            "consistency_career_loss_annual": round(max(8 - d["Consistency"], 0) * income * 0.08, 2),
        }

        return {
            "profile": profile,
            "urgency": urgency,
            "peer_comparison": peer,
            "flags": flags,
            "opportunity_costs": opp_costs,
            "total_annual_opportunity_cost": round(sum(opp_costs.values()), 2),
        }


class LLMEngine:
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.65,
            max_tokens=3500,
        )
        self.parser = JsonOutputParser()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a brutally honest, deeply analytical AI life mentor for students. "
                "You speak directly to the student. You use real numbers. You show consequences. "
                "You are not gentle — you are honest. You explain cause and effect clearly. "
                "Return ONLY valid JSON. No markdown. No preamble. No explanation outside JSON."
            )),
            ("human", "{input}"),
        ])
        self.chain = self.prompt | self.llm | self.parser

    def analyze(self, payload: dict) -> dict:
        user_str = json.dumps(payload, indent=2, ensure_ascii=False)
        prompt_text = f"""
Analyze this student's complete life data and computed metrics. Generate deep, brutally honest insights.

=== DATA ===
{user_str}

=== REQUIRED OUTPUT FORMAT (return ONLY this JSON) ===
{{
  "summary": "<3-4 sentence executive summary of trajectory and key risks>",
  "scores": {{
    "retirement_readiness": {{"value": <0-100>, "reason": "<data-driven, specific>"}},
    "savings_discipline_score": {{"value": <0-100>, "reason": "<specific>"}},
    "financial_burn_rate_indicator": {{"value": <0-100>, "reason": "<specific>"}},
    "lifestyle_risk_index": {{"value": <0-100>, "reason": "<specific>"}},
    "career_growth_potential_score": {{"value": <0-100>, "reason": "<specific>"}},
    "financial_dependency_ratio": {{"value": <0-100>, "reason": "<specific>"}},
    "wealth_acceleration_potential": {{"value": <0-100>, "reason": "<specific>"}},
    "intervention_urgency_level": {{"value": <0-100>, "reason": "<specific>"}}
  }},
  "future_projection": {{
    "qualitative": "<Where does this person end up at 60 if nothing changes? Paint a vivid picture.>",
    "numeric": "<Specific rupee projections at age 30, 40, 60 for current vs optimized behavior>"
  }},
  "retirement_delay_risk": "<Low/Medium/High/Critical>",
  "future_lifestyle_tier": "<Thriving/Stable/Struggling/At Risk/Critical>",
  "lifepath_analysis": {{
    "current_behavior": {{
      "wealth": "<specific wealth projection with numbers>",
      "career_growth": "<specific career trajectory>",
      "financial_stability": "<stability assessment with risks>"
    }},
    "optimized_behavior": {{
      "wealth": "<specific wealth if optimized with numbers>",
      "career_growth": "<career trajectory if optimized>",
      "financial_stability": "<stability if optimized>"
    }}
  }},
  "micro_regret": [
    "<5 brutally specific regret insights with exact rupee figures and timelines>"
  ],
  "opportunity_cost": [
    "<5 specific missed opportunities with exact figures and what could have been>"
  ],
  "behavior_profile": "<Disciplined/Balanced/Impulsive/At Risk>",
  "health_impact": "<Specific health-to-earnings analysis: how sleep, screen time, and health score are directly costing income and career progress — with numbers>",
  "peer_comparison": "<Below Average/Average/Above Average with context>",
  "recommendations": [
    "<5 specific, measurable, time-bound actions — each with an expected outcome in rupees or %>"
  ],
  "final_statement": "<2 sentences of maximum psychological impact. Make the student feel the weight of their current path and the hope of changing it.>"
}}
"""
        return self.chain.invoke({"input": prompt_text})


def score_color(v):
    if v >= 70: return "good"
    if v >= 45: return "warn"
    return "bad"


def fmt_inr(v):
    if v >= 10_000_000: return f"₹{v/10_000_000:.2f}Cr"
    if v >= 100_000: return f"₹{v/100_000:.2f}L"
    if v >= 1000: return f"₹{v/1000:.1f}K"
    return f"₹{v:.0f}"


def gauge_chart(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"family": "Syne", "size": 13, "color": "#9a9aaa"}},
        number={"font": {"family": "Syne", "size": 28, "color": "#e8e6e1"}, "suffix": ""},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#2e2e4e", "tickfont": {"color": "#5a5a6e", "size": 9}},
            "bar": {"color": color, "thickness": 0.6},
            "bgcolor": "#111118",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "#1a0707"},
                {"range": [40, 70], "color": "#1c1a07"},
                {"range": [70, 100], "color": "#052e16"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": value},
        },
    ))
    fig.update_layout(
        height=180, margin=dict(t=30, b=10, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono"),
    )
    return fig


def projection_chart(proj, d):
    years = [5, 10, 20, 30]
    curr = [proj["current_behavior_wealth"][y] for y in years]
    opt = [proj["optimized_behavior_wealth"][y] for y in years]
    age_labels = [f"Age {d['Age']+y}" for y in years]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=age_labels, y=curr, mode="lines+markers", name="Current Path",
        line=dict(color="#ef4444", width=2, dash="dot"),
        marker=dict(color="#ef4444", size=7),
        fill="tozeroy", fillcolor="rgba(239,68,68,0.06)",
    ))
    fig.add_trace(go.Scatter(
        x=age_labels, y=opt, mode="lines+markers", name="Optimized Path",
        line=dict(color="#22c55e", width=2),
        marker=dict(color="#22c55e", size=7),
        fill="tozeroy", fillcolor="rgba(34,197,94,0.06)",
    ))
    fig.update_layout(
        title=dict(text="Wealth Projection", font=dict(family="Syne", color="#e8e6e1", size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(family="DM Mono", color="#9a9aaa", size=11), bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#1e1e2e", color="#5a5a6e", tickfont=dict(size=10), tickprefix="₹"),
        xaxis=dict(gridcolor="#1e1e2e", color="#5a5a6e", tickfont=dict(size=11)),
        height=320, margin=dict(t=40, b=30, l=60, r=20),
        hovermode="x unified",
    )
    return fig


def regret_bar_chart(regret):
    labels = ["Discretionary\nSpending", "Screen Time\nLoss", "Sleep Deficit\nLoss", "Career Gap\nLoss", "Health\nNeglect"]
    values = [
        regret["discretionary_spending_regret"],
        regret["screen_time_wealth_loss"],
        regret["sleep_deficit_income_loss"],
        regret["career_gap_wealth_loss"],
        regret["health_negligence_loss"],
    ]
    colors = ["#ef4444", "#f97316", "#f5c842", "#e879f9", "#3b82f6"]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        text=[fmt_inr(v) for v in values], textposition="outside",
        textfont=dict(family="Syne", color="#e8e6e1", size=11),
    ))
    fig.update_layout(
        title=dict(text="Lifetime Regret Cost Breakdown", font=dict(family="Syne", color="#e8e6e1", size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="#1e1e2e", color="#5a5a6e", tickfont=dict(size=10), tickprefix="₹"),
        xaxis=dict(color="#9a9aaa", tickfont=dict(size=10, family="DM Mono")),
        height=320, margin=dict(t=40, b=30, l=60, r=20),
        bargap=0.35, showlegend=False,
    )
    return fig


def expense_pie(d, fin):
    fixed = d["Fixed_Expenses"]
    variable = d["Variable_Expenses"]
    weekly_monthly = d["Weekly_Spending"] * 4.33
    savings = fin["monthly_savings"]
    resp = d["Family_Responsibility"]

    labels = ["Fixed Expenses", "Variable Expenses", "Weekly Spending", "Family Responsibility", "Savings"]
    values = [fixed, variable, weekly_monthly, resp, max(savings, 0)]
    colors = ["#3b82f6", "#f97316", "#ef4444", "#e879f9", "#22c55e"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values, marker_colors=colors,
        hole=0.55, textfont=dict(family="DM Mono", size=11),
        textposition="outside",
    ))
    fig.update_layout(
        title=dict(text="Monthly Money Breakdown", font=dict(family="Syne", color="#e8e6e1", size=14)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(family="DM Mono", color="#9a9aaa", size=11), bgcolor="rgba(0,0,0,0)"),
        height=300, margin=dict(t=40, b=10, l=20, r=20),
    )
    return fig


def build_sidebar():
    st.markdown("""
    <div style='padding:20px 0 10px;'>
        <div style='font-family:Syne;font-size:1.1rem;font-weight:800;color:#f5c842;letter-spacing:-0.02em;'>
            🧠 SLIE
        </div>
        <div style='font-family:DM Mono;font-size:0.65rem;color:#3a3a4e;text-transform:uppercase;letter-spacing:0.1em;'>
            Student Life Intelligence Engine
        </div>
    </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

    data = {}
    with st.expander("👤 Personal", expanded=True):
        data["Full_Name"] = st.text_input("Full Name", "Default Student")
        c1, c2 = st.columns(2)
        data["Age"] = c1.number_input("Age", 16, 35, 21)
        data["Gender"] = c2.selectbox("Gender", ["Male", "Female", "Other"])
        data["Country"] = st.text_input("Country", "India")

    with st.expander("🎓 Education"):
        data["Education_Level"] = st.selectbox("Level", ["High School", "Undergraduate", "Postgraduate", "PhD"])
        data["Field_of_Study"] = st.text_input("Field", "Computer Science")
        c1, c2 = st.columns(2)
        data["Institution_Tier"] = c1.selectbox("Inst. Tier", [1, 2, 3, 4, 5], index=1)
        data["CGPA"] = c2.number_input("CGPA", 0.0, 10.0, 7.5, 0.1)
        c1, c2 = st.columns(2)
        data["Study_Hours"] = c1.number_input("Study Hrs/Week", 0, 80, 20)
        data["Consistency"] = c2.slider("Consistency (0-10)", 0, 10, 5)

    with st.expander("💼 Career"):
        data["Target_Career"] = st.text_input("Target Career", "Software Developer")
        c1, c2 = st.columns(2)
        data["Skill_Level"] = c1.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced", "Expert"], index=1)
        data["Internships"] = c2.number_input("Internships", 0, 20, 1)

    with st.expander("💰 Financial"):
        c1, c2 = st.columns(2)
        data["Monthly_Income"] = c1.number_input("Monthly Income (₹)", 0, 500000, 15000, 500)
        data["Fixed_Expenses"] = c2.number_input("Fixed Expenses (₹)", 0, 200000, 8000, 500)
        c1, c2 = st.columns(2)
        data["Variable_Expenses"] = c1.number_input("Variable Expenses (₹)", 0, 100000, 4000, 500)
        data["Weekly_Spending"] = c2.number_input("Weekly Spending (₹)", 0, 50000, 2000, 100)
        c1, c2 = st.columns(2)
        data["Current_Savings"] = c1.number_input("Current Savings (₹)", 0, 10000000, 25000, 1000)
        data["Savings_Target"] = c2.number_input("Savings Target (₹)", 1000, 10000000, 50000, 1000)
        data["Savings_Duration"] = st.number_input("Target Duration (months)", 1, 120, 12)

    with st.expander("👨‍👩‍👧 Family"):
        c1, c2 = st.columns(2)
        data["Family_Income"] = c1.number_input("Family Income (₹)", 0, 1000000, 60000, 1000)
        data["Earning_Members"] = c2.number_input("Earning Members", 1, 10, 2)
        c1, c2 = st.columns(2)
        data["Dependents"] = c1.number_input("Dependents", 0, 15, 3)
        data["Family_Support"] = c2.number_input("Family Support Recv (₹)", 0, 50000, 5000, 500)
        data["Father_Occupation"] = st.text_input("Father Occupation", "Private Job")
        data["Mother_Occupation"] = st.text_input("Mother Occupation", "Homemaker")
        data["Family_Responsibility"] = st.number_input("Monthly Family Resp (₹)", 0, 50000, 2000, 500)

    with st.expander("🌙 Lifestyle"):
        c1, c2 = st.columns(2)
        data["Screen_Time"] = c1.number_input("Screen Time (hrs/day)", 0.0, 20.0, 6.0, 0.5)
        data["Sleep_Duration"] = c2.number_input("Sleep (hrs/night)", 0.0, 12.0, 6.5, 0.5)
        c1, c2 = st.columns(2)
        data["Sleep_Quality"] = c1.slider("Sleep Quality (0-10)", 0, 10, 6)
        data["Health_Score"] = c2.slider("Health Score (0-10)", 0, 10, 6)
        c1, c2 = st.columns(2)
        data["Sick_Days"] = c1.number_input("Sick Days/Month", 0, 30, 2)
        data["Medical_Expenses"] = c2.number_input("Medical Expenses (₹/mo)", 0, 50000, 1000, 100)

    run = st.button("⚡ RUN ANALYSIS")
    return data, api_key, run


def render_overview(d, scores, fin, behav, proj):
    name = d["Full_Name"]
    st.markdown(f"""
    <div style='margin:0 0 24px;'>
        <div class='main-title'>Life Intelligence Report</div>
        <div class='sub-title'>Analysis for {name} · Age {d['Age']} · {d['Field_of_Study']}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "Overall Score", f"{scores['behavior']}", score_color(scores['behavior']), f"Peer: {behav['peer_comparison']}"),
        (c2, "Academic", f"{scores['academic']}", score_color(scores['academic']), "30% weight"),
        (c3, "Financial", f"{scores['financial']}", score_color(scores['financial']), "25% weight"),
        (c4, "Career", f"{scores['career']}", score_color(scores['career']), "25% weight"),
        (c5, "Lifestyle", f"{scores['lifestyle']}", score_color(scores['lifestyle']), "20% weight"),
    ]
    for col, label, val, cls, sub in cards:
        with col:
            st.markdown(f"""
            <div class='score-card {cls}'>
                <div class='score-label'>{label}</div>
                <div class='score-value'>{val}</div>
                <div class='score-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='metric-chip'>
            <div class='metric-chip-label'>Behavior Profile</div>
            <div class='metric-chip-value'>{behav['profile']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        urg = behav['urgency']
        urg_cls = urg.lower().replace(" ", "-")
        st.markdown(f"""
        <div class='metric-chip'>
            <div class='metric-chip-label'>Intervention Urgency</div>
            <div class='urgency-{urg_cls}'>{urg}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-chip'>
            <div class='metric-chip-label'>Monthly Savings</div>
            <div class='metric-chip-value'>{fmt_inr(fin['monthly_savings'])}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-chip'>
            <div class='metric-chip-label'>Savings Rate</div>
            <div class='metric-chip-value'>{fin['savings_rate_pct']}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    gc1, gc2, gc3, gc4 = st.columns(4)
    gauge_data = [
        (gc1, scores["academic"], "Academic", "#3b82f6"),
        (gc2, scores["financial"], "Financial", "#f5c842"),
        (gc3, scores["career"], "Career", "#a855f7"),
        (gc4, scores["lifestyle"], "Lifestyle", "#22c55e"),
    ]
    for col, val, title, color in gauge_data:
        with col:
            st.plotly_chart(gauge_chart(val, title, color), use_container_width=True, config={"displayModeBar": False})

    if behav["flags"]:
        st.markdown("<div class='section-heading'>⚠ Detected Risk Flags</div>", unsafe_allow_html=True)
        flag_cols = st.columns(min(len(behav["flags"]), 3))
        for i, (flag, sev) in enumerate(behav["flags"]):
            sev_colors = {"critical": "#ef4444", "high": "#f97316", "medium": "#f5c842"}
            color = sev_colors.get(sev, "#9a9aaa")
            with flag_cols[i % 3]:
                st.markdown(f"""
                <div style='background:#111118;border:1px solid {color}33;border-left:3px solid {color};
                border-radius:8px;padding:10px 14px;margin:4px 0;'>
                    <div style='font-family:DM Mono;font-size:0.7rem;color:{color};text-transform:uppercase;
                    letter-spacing:0.08em;'>{sev.upper()}</div>
                    <div style='font-family:Syne;font-size:0.85rem;color:#e8e6e1;font-weight:600;margin-top:4px;'>
                    {flag.replace("_", " ")}</div>
                </div>""", unsafe_allow_html=True)


def render_financial(d, fin, proj):
    st.markdown("<div class='section-heading'>📊 Financial Health Breakdown</div>", unsafe_allow_html=True)

    metrics = [
        ("Effective Income", fmt_inr(fin["effective_income"]), "info"),
        ("Total Expenses", fmt_inr(fin["total_monthly_expenses"]), "bad" if fin["expense_ratio_pct"] > 80 else "warn"),
        ("Monthly Savings", fmt_inr(fin["monthly_savings"]), score_color(fin["savings_rate_pct"] * 2)),
        ("Burn Rate", f"{fin['burn_rate_pct']:.1f}%", "bad" if fin["burn_rate_pct"] > 60 else "warn"),
        ("Expense Ratio", f"{fin['expense_ratio_pct']:.1f}%", "bad" if fin["expense_ratio_pct"] > 80 else "warn"),
        ("Dependency Ratio", f"{fin['dependency_ratio']:.2f}", "bad" if fin["dependency_ratio"] > 1.5 else "warn"),
        ("Savings Rate", f"{fin['savings_rate_pct']:.1f}%", score_color(fin["savings_rate_pct"] * 2)),
        ("Months to Target", str(fin["months_to_savings_target"]), "bad" if fin["months_to_savings_target"] == "Never at current rate" else "warn"),
    ]
    cols = st.columns(4)
    for i, (label, val, cls) in enumerate(metrics):
        with cols[i % 4]:
            st.markdown(f"""
            <div class='score-card {cls}' style='margin:6px 0;'>
                <div class='score-label'>{label}</div>
                <div style='font-family:Syne;font-size:1.4rem;font-weight:800;color:#e8e6e1;'>{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(projection_chart(proj, d), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(expense_pie(d, fin), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-heading'>📈 Savings Growth Projections</div>", unsafe_allow_html=True)
    years = [5, 10, 20, 30]
    proj_data = []
    for y in years:
        proj_data.append({
            "Timeline": f"{y} Years (Age {d['Age']+y})",
            "Current Path": fmt_inr(proj["current_behavior_wealth"][y]),
            "Optimized Path": fmt_inr(proj["optimized_behavior_wealth"][y]),
            "Gap": fmt_inr(proj["optimized_behavior_wealth"][y] - proj["current_behavior_wealth"][y]),
        })
    df = pd.DataFrame(proj_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timeline": st.column_config.TextColumn(width="medium"),
            "Current Path": st.column_config.TextColumn(width="medium"),
            "Optimized Path": st.column_config.TextColumn(width="medium"),
            "Gap": st.column_config.TextColumn(width="medium"),
        }
    )


def render_projection(d, proj, fin):
    st.markdown("<div class='section-heading'>🔭 Life Path Projections</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div style='font-family:Syne;font-size:0.9rem;font-weight:700;color:#ef4444;margin-bottom:12px;'>⚠ CURRENT PATH</div>", unsafe_allow_html=True)
        for y in [5, 10, 20, 30]:
            val = proj["current_behavior_wealth"][y]
            st.markdown(f"""
            <div style='background:#110808;border:1px solid #2e1515;border-radius:8px;padding:12px 16px;margin:6px 0;
            display:flex;justify-content:space-between;align-items:center;'>
                <div style='font-family:DM Mono;font-size:0.8rem;color:#9a6a6a;'>Age {d['Age']+y} (+{y}yr)</div>
                <div style='font-family:Syne;font-size:1.1rem;font-weight:800;color:#ef4444;'>{fmt_inr(val)}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='font-family:Syne;font-size:0.9rem;font-weight:700;color:#22c55e;margin-bottom:12px;'>✅ OPTIMIZED PATH</div>", unsafe_allow_html=True)
        for y in [5, 10, 20, 30]:
            val = proj["optimized_behavior_wealth"][y]
            st.markdown(f"""
            <div style='background:#060e06;border:1px solid #1a2e1a;border-radius:8px;padding:12px 16px;margin:6px 0;
            display:flex;justify-content:space-between;align-items:center;'>
                <div style='font-family:DM Mono;font-size:0.8rem;color:#6a9a6a;'>Age {d['Age']+y} (+{y}yr)</div>
                <div style='font-family:Syne;font-size:1.1rem;font-weight:800;color:#22c55e;'>{fmt_inr(val)}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-heading'>💼 Career Milestone Projections</div>", unsafe_allow_html=True)
    for m in proj["career_milestones"]:
        pct_growth = ((m["projected_monthly_income"] - d["Monthly_Income"]) / max(d["Monthly_Income"], 1)) * 100
        st.markdown(f"""
        <div style='background:#0f0f1a;border:1px solid #1e1e2e;border-radius:8px;padding:12px 16px;margin:6px 0;
        display:flex;justify-content:space-between;align-items:center;'>
            <div>
                <div style='font-family:Syne;font-size:0.85rem;font-weight:700;color:#e8e6e1;'>
                    +{m["year"]} Years · Age {m["age"]}</div>
                <div style='font-family:DM Mono;font-size:0.72rem;color:#5a5a6e;margin-top:3px;'>
                    Based on consistency score {d['Consistency']}/10</div>
            </div>
            <div style='text-align:right;'>
                <div style='font-family:Syne;font-size:1.1rem;font-weight:800;color:#f5c842;'>
                    {fmt_inr(m["projected_monthly_income"])}/mo</div>
                <div style='font-family:DM Mono;font-size:0.72rem;color:{"#22c55e" if pct_growth > 0 else "#ef4444"};margin-top:2px;'>
                    {"+"+f"{pct_growth:.0f}%" if pct_growth >= 0 else f"{pct_growth:.0f}%"} from now</div>
            </div>
        </div>""", unsafe_allow_html=True)


def render_regret(regret, behav):
    st.markdown("<div class='section-heading'>💸 Lifetime Regret Cost Analysis</div>", unsafe_allow_html=True)

    total = regret["total_lifetime_regret_cost"]
    monthly_equiv = regret["monthly_regret_equivalent"]

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#130707,#1a0a0a);border:1px solid #3d1515;border-radius:14px;
    padding:28px;text-align:center;margin:0 0 24px;'>
        <div style='font-family:DM Mono;font-size:0.72rem;color:#7a4a4a;text-transform:uppercase;
        letter-spacing:0.12em;margin-bottom:10px;'>Total Estimated Lifetime Regret Cost</div>
        <div style='font-family:Syne;font-size:3rem;font-weight:800;color:#ef4444;line-height:1;'>
            {fmt_inr(total)}</div>
        <div style='font-family:DM Mono;font-size:0.78rem;color:#9a5a5a;margin-top:10px;'>
            ≈ {fmt_inr(monthly_equiv)} per month in lost potential, compounded over {regret["projection_years"]} years</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    regret_items = [
        (c1, "Discretionary Spending", regret["discretionary_spending_regret"], f"₹{round(regret['discretionary_spending_regret']/regret['projection_years']/12):,}/mo compounded"),
        (c2, "Screen Time Loss", regret["screen_time_wealth_loss"], f"{regret['screen_productivity_drag_pct']}% productivity drag"),
        (c3, "Sleep Deficit", regret["sleep_deficit_income_loss"], f"{regret['sleep_productivity_drag_pct']}% productivity drag"),
    ]
    for col, label, val, sub in regret_items:
        with col:
            st.markdown(f"""
            <div class='regret-card'>
                <div class='regret-label'>{label}</div>
                <div class='regret-amount'>{fmt_inr(val)}</div>
                <div style='font-family:DM Mono;font-size:0.7rem;color:#7a4a4a;margin-top:6px;'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    regret_items2 = [
        (c1, "Career Gap Loss", regret["career_gap_wealth_loss"], f"{regret['career_drag_pct']}% career income drag"),
        (c2, "Health Negligence", regret["health_negligence_loss"], f"{regret['health_drag_pct']}% health drag"),
        (c3, "Late Investing Loss", regret["late_investing_opportunity_loss"], "Opportunity cost of delayed start"),
    ]
    for col, label, val, sub in regret_items2:
        with col:
            st.markdown(f"""
            <div class='regret-card'>
                <div class='regret-label'>{label}</div>
                <div class='regret-amount'>{fmt_inr(val)}</div>
                <div style='font-family:DM Mono;font-size:0.7rem;color:#7a4a4a;margin-top:6px;'>{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.plotly_chart(regret_bar_chart(regret), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-heading'>💡 Opportunity Costs</div>", unsafe_allow_html=True)
    opp = behav["opportunity_costs"]
    opp_items = [
        ("Skill Upgrade Annual Gain", opp["skill_upgrade_annual_gain"]),
        ("Uninvested Savings Returns", opp["uninvested_savings_returns"]),
        ("Screen Time Freelance Loss", opp["screen_time_freelance_loss"]),
        ("Internship Gap Loss", opp["internship_gap_loss"]),
        ("Consistency Career Loss", opp["consistency_career_loss_annual"]),
    ]
    oc1, oc2 = st.columns(2)
    for i, (label, val) in enumerate(opp_items):
        with (oc1 if i % 2 == 0 else oc2):
            st.markdown(f"""
            <div style='background:#0d120d;border:1px solid #1a2e1a;border-radius:8px;padding:12px 16px;margin:6px 0;
            display:flex;justify-content:space-between;align-items:center;'>
                <div style='font-family:DM Mono;font-size:0.78rem;color:#6a9a6a;'>{label}</div>
                <div style='font-family:Syne;font-size:1rem;font-weight:700;color:#22c55e;'>{fmt_inr(val)}/yr</div>
            </div>""", unsafe_allow_html=True)


def render_ai_insights(llm_out, d):
    if not llm_out:
        st.info("Run the analysis first to see AI insights.")
        return

    summary = llm_out.get("summary", "")
    st.markdown(f"""
    <div class='insight-block'>
        <div style='font-family:DM Mono;font-size:0.68rem;color:#5a5a6e;text-transform:uppercase;
        letter-spacing:0.1em;margin-bottom:8px;'>Executive Summary</div>
        {summary}
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-heading'>🎯 AI-Computed Scores</div>", unsafe_allow_html=True)
    ai_scores = llm_out.get("scores", {})
    if ai_scores:
        score_keys = list(ai_scores.keys())
        cols = st.columns(4)
        for i, key in enumerate(score_keys):
            item = ai_scores[key]
            val = item.get("value", 0)
            reason = item.get("reason", "")
            label = key.replace("_", " ").title()
            cls = score_color(val)
            with cols[i % 4]:
                st.markdown(f"""
                <div class='score-card {cls}' style='margin:6px 0;min-height:110px;'>
                    <div class='score-label'>{label}</div>
                    <div style='font-family:Syne;font-size:1.6rem;font-weight:800;color:#e8e6e1;'>{val}</div>
                    <div style='font-family:DM Mono;font-size:0.67rem;color:#5a5a6e;margin-top:6px;
                    line-height:1.5;'>{reason[:90]}{"..." if len(reason) > 90 else ""}</div>
                </div>""", unsafe_allow_html=True)

    fp = llm_out.get("future_projection", {})
    if fp:
        st.markdown("<div class='section-heading'>🔮 Future Projection</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class='insight-block red'>
                <div style='font-family:DM Mono;font-size:0.68rem;color:#7a3a3a;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:6px;'>Qualitative Outlook</div>
                {fp.get('qualitative', '')}
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='insight-block blue'>
                <div style='font-family:DM Mono;font-size:0.68rem;color:#3a5a7a;text-transform:uppercase;
                letter-spacing:0.1em;margin-bottom:6px;'>Numeric Projection</div>
                {fp.get('numeric', '')}
            </div>""", unsafe_allow_html=True)

    la = llm_out.get("lifepath_analysis", {})
    if la:
        st.markdown("<div class='section-heading'>🛤 Life Path Analysis</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='font-family:Syne;font-size:0.85rem;font-weight:700;color:#ef4444;margin-bottom:10px;'>⚠ Current Behavior</div>", unsafe_allow_html=True)
            for k, v in la.get("current_behavior", {}).items():
                st.markdown(f"""
                <div style='background:#110808;border:1px solid #2e1515;border-radius:6px;padding:10px 14px;
                margin:5px 0;'>
                    <div style='font-family:DM Mono;font-size:0.67rem;color:#7a4a4a;text-transform:uppercase;
                    margin-bottom:4px;'>{k}</div>
                    <div style='font-family:DM Mono;font-size:0.82rem;color:#c9a0a0;'>{v}</div>
                </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("<div style='font-family:Syne;font-size:0.85rem;font-weight:700;color:#22c55e;margin-bottom:10px;'>✅ Optimized Behavior</div>", unsafe_allow_html=True)
            for k, v in la.get("optimized_behavior", {}).items():
                st.markdown(f"""
                <div style='background:#060e06;border:1px solid #1a2e1a;border-radius:6px;padding:10px 14px;
                margin:5px 0;'>
                    <div style='font-family:DM Mono;font-size:0.67rem;color:#4a7a4a;text-transform:uppercase;
                    margin-bottom:4px;'>{k}</div>
                    <div style='font-family:DM Mono;font-size:0.82rem;color:#a0c9a0;'>{v}</div>
                </div>""", unsafe_allow_html=True)

    micro = llm_out.get("micro_regret", [])
    if micro:
        st.markdown("<div class='section-heading'>😔 Micro-Regret Insights</div>", unsafe_allow_html=True)
        for item in micro:
            st.markdown(f"<div class='insight-block red'>{item}</div>", unsafe_allow_html=True)

    opp = llm_out.get("opportunity_cost", [])
    if opp:
        st.markdown("<div class='section-heading'>💡 Opportunity Cost Insights</div>", unsafe_allow_html=True)
        for item in opp:
            st.markdown(f"<div class='insight-block'>{item}</div>", unsafe_allow_html=True)

    health = llm_out.get("health_impact", "")
    if health:
        st.markdown("<div class='section-heading'>🏥 Health Impact Analysis</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='insight-block blue'>{health}</div>", unsafe_allow_html=True)

    recs = llm_out.get("recommendations", [])
    if recs:
        st.markdown("<div class='section-heading'>✅ Action Plan</div>", unsafe_allow_html=True)
        for i, rec in enumerate(recs, 1):
            st.markdown(f"""
            <div class='rec-item'>
                <div class='rec-num'>0{i}</div>
                <div>{rec}</div>
            </div>""", unsafe_allow_html=True)

    final = llm_out.get("final_statement", "")
    if final:
        st.markdown(f"<div class='final-statement'>{final}</div>", unsafe_allow_html=True)


def main():
    with st.sidebar:
        raw_data, api_key, run_clicked = build_sidebar()

    if not run_clicked:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
        min-height:60vh;text-align:center;padding:40px;'>
            <div style='font-size:3.5rem;margin-bottom:16px;'>🧠</div>
            <div class='main-title' style='font-size:2rem;'>Student Life Intelligence Engine</div>
            <div style='font-family:DM Mono;font-size:0.82rem;color:#3a3a5e;max-width:480px;
            margin-top:16px;line-height:1.8;'>
                Fill in your details in the sidebar and click <strong style='color:#f5c842;'>RUN ANALYSIS</strong>
                to receive a brutally honest, data-driven analysis of your life trajectory.
            </div>
            <div style='margin-top:40px;display:flex;gap:20px;flex-wrap:wrap;justify-content:center;'>
                <div style='background:#111118;border:1px solid #1e1e2e;border-radius:10px;padding:16px 20px;
                min-width:140px;'>
                    <div style='font-size:1.5rem;'>📊</div>
                    <div style='font-family:Syne;font-size:0.8rem;color:#5a5a6e;margin-top:8px;'>Multi-Dimensional<br>Scoring</div>
                </div>
                <div style='background:#111118;border:1px solid #1e1e2e;border-radius:10px;padding:16px 20px;
                min-width:140px;'>
                    <div style='font-size:1.5rem;'>💸</div>
                    <div style='font-family:Syne;font-size:0.8rem;color:#5a5a6e;margin-top:8px;'>Life Regret<br>Simulation</div>
                </div>
                <div style='background:#111118;border:1px solid #1e1e2e;border-radius:10px;padding:16px 20px;
                min-width:140px;'>
                    <div style='font-size:1.5rem;'>🔮</div>
                    <div style='font-family:Syne;font-size:0.8rem;color:#5a5a6e;margin-top:8px;'>Future Path<br>Projections</div>
                </div>
                <div style='background:#111118;border:1px solid #1e1e2e;border-radius:10px;padding:16px 20px;
                min-width:140px;'>
                    <div style='font-size:1.5rem;'>🤖</div>
                    <div style='font-family:Syne;font-size:0.8rem;color:#5a5a6e;margin-top:8px;'>AI-Powered<br>Insights</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar.")
        return

    with st.spinner("Running deep analysis..."):
        try:
            d = DataNormalizer.normalize(raw_data)
            ac = ScoringEngine.academic(d)
            fi = ScoringEngine.financial(d)
            ca = ScoringEngine.career(d)
            li = ScoringEngine.lifestyle(d)
            bh = ScoringEngine.behavior(ac, fi, ca, li)
            scores = {"academic": ac, "financial": fi, "career": ca, "lifestyle": li, "behavior": bh}

            fin = FinancialEngine.compute(d)
            proj = ProjectionEngine.project(d, fin)
            regret = RegretEngine.compute(d, fin)
            behav = BehavioralEngine.classify(d, fin, scores)

            llm_payload = {
                "user_input": d,
                "scores": scores,
                "financial_indicators": fin,
                "projections": {
                    "current_wealth_5yr": proj["current_behavior_wealth"][5],
                    "current_wealth_10yr": proj["current_behavior_wealth"][10],
                    "current_wealth_20yr": proj["current_behavior_wealth"][20],
                    "current_wealth_30yr": proj["current_behavior_wealth"][30],
                    "optimized_wealth_30yr": proj["optimized_behavior_wealth"][30],
                },
                "regret_analysis": regret,
                "behavioral_profile": {
                    "profile": behav["profile"],
                    "urgency": behav["urgency"],
                    "peer_comparison": behav["peer_comparison"],
                    "flags": [f"{f}:{s}" for f, s in behav["flags"]],
                    "total_annual_opportunity_cost": behav["total_annual_opportunity_cost"],
                },
            }

            llm_engine = LLMEngine(api_key)
            llm_out = llm_engine.analyze(llm_payload)

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "  Overview  ", "  Financial Analysis  ", "  Future Projection  ",
        "  Life Regret  ", "  AI Insights  "
    ])

    with tab1:
        render_overview(d, scores, fin, behav, proj)
    with tab2:
        render_financial(d, fin, proj)
    with tab3:
        render_projection(d, proj, fin)
    with tab4:
        render_regret(regret, behav)
    with tab5:
        render_ai_insights(llm_out, d)


if __name__ == "__main__":
    main()