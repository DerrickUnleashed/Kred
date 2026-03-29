import os
import json
import math
import re
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Student Life Intelligence Engine", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SKILL_MAP = {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4}


def safe_div(n, d, fb=0.0):
    return n / d if d != 0 else fb


class AnalyzeRequest(BaseModel):
    Full_Name: Optional[str] = "Student"
    Age: Optional[int] = 20
    Gender: Optional[str] = "Male"
    Country: Optional[str] = "India"
    Education_Level: Optional[str] = "Undergraduate"
    Field_of_Study: Optional[str] = "Computer Science"
    Institution_Tier: Optional[int] = 2
    CGPA: Optional[float] = 7.0
    Study_Hours: Optional[int] = 15
    Target_Career: Optional[str] = "Software Developer"
    Skill_Level: Optional[str] = "Intermediate"
    Internships: Optional[int] = 0
    Consistency: Optional[int] = 5
    Monthly_Income: Optional[float] = 0
    Fixed_Expenses: Optional[float] = 0
    Variable_Expenses: Optional[float] = 0
    Weekly_Spending: Optional[float] = 500
    Current_Savings: Optional[float] = 0
    Savings_Target: Optional[float] = 50000
    Savings_Duration: Optional[int] = 12
    Family_Income: Optional[float] = 30000
    Earning_Members: Optional[int] = 1
    Dependents: Optional[int] = 2
    Father_Occupation: Optional[str] = "Unknown"
    Mother_Occupation: Optional[str] = "Homemaker"
    Family_Support: Optional[float] = 0
    Family_Responsibility: Optional[float] = 0
    Screen_Time: Optional[float] = 4
    Sleep_Duration: Optional[float] = 7.0
    Sleep_Quality: Optional[int] = 6
    Health_Score: Optional[int] = 6
    Sick_Days: Optional[int] = 1
    Medical_Expenses: Optional[float] = 500
    groq_api_key: str = Field(..., description="Groq API key")


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


def normalize_data(raw: dict) -> dict:
    data = DEFAULTS.copy()
    data.update({k: v for k, v in raw.items() if v is not None and k != "groq_api_key"})
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


def score_academic(d):
    cgpa = _norm(d["CGPA"], 0, 10)
    study = _norm(d["Study_Hours"], 0, 40)
    tier = _norm(d["Institution_Tier"], 1, 5, invert=True)
    consistency = _norm(d["Consistency"], 0, 10)
    return round(cgpa * 0.40 + study * 0.30 + tier * 0.15 + consistency * 0.15, 2)


def score_financial(d):
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


def score_career(d):
    skill = _norm(SKILL_MAP.get(d["Skill_Level"], 1), 1, 4)
    intern_ = _norm(d["Internships"], 0, 5)
    cons = _norm(d["Consistency"], 0, 10)
    study = _norm(d["Study_Hours"], 0, 40)
    cgpa = _norm(d["CGPA"], 0, 10)
    return round(skill * 0.35 + intern_ * 0.25 + cons * 0.20 + study * 0.10 + cgpa * 0.10, 2)


def score_lifestyle(d):
    sleep_dev = abs(d["Sleep_Duration"] - 7.5)
    sd = _norm(sleep_dev, 0, 4, invert=True)
    sq = _norm(d["Sleep_Quality"], 0, 10)
    hs = _norm(d["Health_Score"], 0, 10)
    sc = _norm(d["Screen_Time"], 0, 16, invert=True)
    sick = _norm(d["Sick_Days"], 0, 30, invert=True)
    med = _norm(safe_div(d["Medical_Expenses"], max(d["Monthly_Income"], 1)) * 100, 0, 50, invert=True)
    return round(sd * 0.20 + sq * 0.20 + hs * 0.25 + sc * 0.20 + sick * 0.10 + med * 0.05, 2)


def score_behavior(a, f, c, l):
    return round(a * 0.30 + f * 0.25 + c * 0.25 + l * 0.20, 2)


def compute_financials(d):
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


def compute_projections(d, fin, years=(5, 10, 20, 30)):
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


def compute_regret(d, fin):
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
    career_drag = cgpa_gap * 0.025 + skill_gap * 0.05 + max(2 - d["Internships"], 0) * 0.03
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


def classify_behavior(d, fin, scores):
    flags = []
    income = max(d["Monthly_Income"], 1)
    if fin["expense_ratio_pct"] > 85:
        flags.append({"flag": "OVERSPENDING", "severity": "critical"})
    elif fin["expense_ratio_pct"] > 70:
        flags.append({"flag": "OVERSPENDING", "severity": "high"})
    if d["Consistency"] < 4:
        flags.append({"flag": "LOW_EFFORT", "severity": "high"})
    elif d["Consistency"] < 6:
        flags.append({"flag": "LOW_EFFORT", "severity": "medium"})
    if d["Screen_Time"] > 8:
        flags.append({"flag": "EXCESSIVE_SCREEN_TIME", "severity": "critical"})
    elif d["Screen_Time"] > 6:
        flags.append({"flag": "EXCESSIVE_SCREEN_TIME", "severity": "high"})
    if d["Sleep_Duration"] < 6:
        flags.append({"flag": "POOR_SLEEP", "severity": "critical"})
    elif d["Sleep_Duration"] < 7:
        flags.append({"flag": "POOR_SLEEP", "severity": "high"})
    if d["Health_Score"] < 4:
        flags.append({"flag": "POOR_HEALTH", "severity": "critical"})
    elif d["Health_Score"] < 6:
        flags.append({"flag": "POOR_HEALTH", "severity": "medium"})
    if fin["savings_rate_pct"] < 5:
        flags.append({"flag": "ZERO_SAVINGS_HABIT", "severity": "critical"})
    elif fin["savings_rate_pct"] < 15:
        flags.append({"flag": "LOW_SAVINGS", "severity": "high"})
    if SKILL_MAP.get(d["Skill_Level"], 1) <= 1 and d["Internships"] == 0:
        flags.append({"flag": "STAGNANT_CAREER", "severity": "critical"})
    if d["CGPA"] < 6.0:
        flags.append({"flag": "LOW_ACADEMIC_PERFORMANCE", "severity": "high"})
    critical_count = sum(1 for f in flags if f["severity"] == "critical")
    high_count = sum(1 for f in flags if f["severity"] == "high")
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


def parse_llm_json(raw_text: str) -> dict:
    """Robustly parse JSON from LLM output, stripping markdown fences if present."""
    # Strip ```json ... ``` or ``` ... ``` fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```", "", cleaned).strip()

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to extract the first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response. Raw output:\n{raw_text[:500]}")


def run_llm_analysis(api_key: str, payload: dict) -> dict:
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="qwen/qwen3-32b",
        temperature=0.65,
        max_tokens=3500,
    )

    # Use StrOutputParser — we handle JSON parsing ourselves robustly
    str_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a brutally honest, deeply analytical AI life mentor for students. "
            "You speak directly to the student. You use real numbers. You show consequences. "
            "You are not gentle — you are honest. You explain cause and effect clearly. "
            "Return ONLY valid JSON. No markdown. No preamble. No explanation outside JSON. "
            "Do NOT wrap your response in code fences or backticks."
        )),
        ("human", "{input}"),
    ])
    chain = prompt | llm | str_parser

    user_str = json.dumps(payload, indent=2, ensure_ascii=False)
    prompt_text = f"""
Analyze this student's complete life data and computed metrics. Generate deep, brutally honest insights.

=== DATA ===
{user_str}

=== REQUIRED OUTPUT FORMAT (return ONLY this JSON, no markdown, no backticks) ===
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

    raw_text = chain.invoke({"input": prompt_text})
    return parse_llm_json(raw_text)


@app.get("/")
def root():
    return {"status": "ok", "service": "Student Life Intelligence Engine"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        raw = req.dict()
        api_key = raw.pop("groq_api_key")

        if not api_key or not api_key.strip():
            raise HTTPException(status_code=400, detail="groq_api_key is required and cannot be empty.")

        d = normalize_data(raw)

        ac = score_academic(d)
        fi = score_financial(d)
        ca = score_career(d)
        li = score_lifestyle(d)
        bh = score_behavior(ac, fi, ca, li)
        scores = {"academic": ac, "financial": fi, "career": ca, "lifestyle": li, "behavior": bh}

        fin = compute_financials(d)
        proj = compute_projections(d, fin)
        regret = compute_regret(d, fin)
        behav = classify_behavior(d, fin, scores)

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
                "flags": [f"{f['flag']}:{f['severity']}" for f in behav["flags"]],
                "total_annual_opportunity_cost": behav["total_annual_opportunity_cost"],
            },
        }

        llm_out = run_llm_analysis(api_key, llm_payload)

        return {
            "input": d,
            "computed_metrics": {
                "scores": scores,
                "financials": fin,
                "projections": proj,
                "regret_analysis": regret,
                "behavioral_profile": behav,
            },
            "scores": scores,
            "financials": fin,
            "projections": proj,
            "regret_analysis": regret,
            "behavioral_profile": behav,
            "llm_output": llm_out,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.post("/scores-only")
def scores_only(req: AnalyzeRequest):
    try:
        raw = req.dict()
        raw.pop("groq_api_key", None)
        d = normalize_data(raw)
        ac = score_academic(d)
        fi = score_financial(d)
        ca = score_career(d)
        li = score_lifestyle(d)
        bh = score_behavior(ac, fi, ca, li)
        scores = {"academic": ac, "financial": fi, "career": ca, "lifestyle": li, "behavior": bh}
        fin = compute_financials(d)
        proj = compute_projections(d, fin)
        regret = compute_regret(d, fin)
        behav = classify_behavior(d, fin, scores)
        return {
            "scores": scores,
            "financials": fin,
            "projections": proj,
            "regret_analysis": regret,
            "behavioral_profile": behav,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=traceback.format_exc())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)