from __future__ import annotations
import os, json, re
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ─── Model Initialisation ─────────────────────────────────────────────────────

def _get_llm(temperature: float = 0.7) -> ChatGroq:
    """Initialise ChatGroq with Qwen model."""
    return ChatGroq(
        model="qwen-qwq-32b",          # Qwen model via Groq
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=1024,
    )


# ─── Prompt Templates ─────────────────────────────────────────────────────────

BEHAVIOR_NARRATIVE_TEMPLATE = PromptTemplate(
    input_variables=[
        "name_placeholder", "age", "field", "cgpa", "college_tier",
        "target_career", "skill_level", "savings_habit", "fin_discipline",
        "health_habits", "sleep_quality",
        "academic_score", "financial_score", "career_score", "lifestyle_score",
        "composite_score", "risk_level", "profile", "trend",
        "weakest_domain", "strongest_domain",
    ],
    template="""
You are a behavioral scientist and life-trajectory analyst specialising in student development.

STUDENT PROFILE:
- Age: {age} | Field: {field} | CGPA: {cgpa}/10 | College: {college_tier}
- Target Career: {target_career} | Skill Level: {skill_level}
- Savings Habit: {savings_habit} | Financial Discipline: {fin_discipline}
- Health Habits: {health_habits} | Sleep Quality: {sleep_quality}

COMPUTED SCORES (out of 100):
- Academic: {academic_score} | Financial: {financial_score}
- Career: {career_score} | Lifestyle: {lifestyle_score}
- Composite: {composite_score}

BEHAVIORAL PROFILE:
- Risk Level: {risk_level} | Profile Type: {profile} | Growth Trend: {trend}
- Strongest Domain: {strongest_domain} | Weakest Domain: {weakest_domain}

YOUR TASK:
Write a DEEP, PERSONALISED behavioral narrative for this student in 4–5 sentences.
Address them directly ("You are…", "Your pattern shows…").
Be honest and insightful — not just motivational fluff.
Focus on how their current habits are COMPOUNDING into their future.
Mention both their strength AND the specific risk pattern in their weakest domain.
Do NOT use bullet points. Write in flowing, intelligent prose.
""".strip()
)

# ──────────────────────────────────────────────────────────────────────────────

FUTURE_NARRATIVE_TEMPLATE = PromptTemplate(
    input_variables=[
        "field", "target_career", "composite_score", "risk_level", "trend",
        "y5_career", "y5_fin", "y5_income",
        "y10_career", "y10_fin", "y10_income",
        "y25_career", "y25_fin", "y25_income",
    ],
    template="""
You are a futurist and life-trajectory forecaster.

STUDENT TRAJECTORY DATA:
- Field: {field} | Target: {target_career}
- Current Composite Score: {composite_score}/100 | Risk: {risk_level} | Trend: {trend}

PROJECTED OUTCOMES:
5-Year  → Career: {y5_career}  | Finances: {y5_fin}  | Est. Income: ₹{y5_income} LPA
10-Year → Career: {y10_career} | Finances: {y10_fin} | Est. Income: ₹{y10_income} LPA
25-Year → Career: {y25_career} | Finances: {y25_fin} | Est. Income: ₹{y25_income} LPA

YOUR TASK:
Write THREE distinct future-narrative paragraphs — one per time horizon.
Each paragraph must describe the ENVIRONMENT and DAILY LIFE at that stage, not just career stats.
Paint a picture: What does their morning look like? What kind of home, city, relationships?
Be specific, vivid, and grounded in the data. Acknowledge if the trajectory is concerning.

Format EXACTLY as:
5_YEAR: <paragraph>
10_YEAR: <paragraph>
25_YEAR: <paragraph>
""".strip()
)

# ──────────────────────────────────────────────────────────────────────────────

IMAGE_SCENE_TEMPLATE = PromptTemplate(
    input_variables=[
        "horizon_label", "career_stability", "fin_condition",
        "lifestyle_qual", "composite_score", "field", "location",
        "narrative_snippet",
    ],
    template="""
You are a creative director for AI image generation, specialising in lifestyle and environment photography.

SCENE PARAMETERS:
- Time Horizon: {horizon_label}
- Career Stability: {career_stability}
- Financial Condition: {fin_condition}
- Lifestyle Quality: {lifestyle_qual}
- Overall Score: {composite_score}/100
- Field / Career: {field}
- Location Context: {location}
- Life Narrative Snippet: {narrative_snippet}

YOUR TASK:
Write a single, highly detailed image generation prompt (no more than 120 words).
Describe a REALISTIC ENVIRONMENT — NOT a person's face.
Focus on: living space, work setup, visible lifestyle indicators, financial signals,
city/nature environment, time of day, mood and lighting.

Rules:
- No faces, no specific people
- Must reflect the financial and career status accurately
- Be cinematic, atmospheric, hyper-realistic
- Include specific details (furniture brands, city type, desk setup, clutter or cleanliness)
- Mention photographic style: "shot on Canon 5D, natural light, 35mm lens, photorealistic"

Output ONLY the prompt text, nothing else.
""".strip()
)

# ──────────────────────────────────────────────────────────────────────────────

INSIGHTS_JSON_TEMPLATE = PromptTemplate(
    input_variables=[
        "academic_score", "financial_score", "career_score", "lifestyle_score",
        "composite_score", "risk_level", "profile", "trend",
        "weakest_domain", "field", "target_career",
        "savings_habit", "fin_discipline", "health_habits", "sleep_quality",
        "study_hours", "skill_level",
    ],
    template="""
You are a student success analyst. Analyse this student's data and return ONLY a valid JSON object.

SCORES: Academic={academic_score}, Financial={financial_score}, Career={career_score},
        Lifestyle={lifestyle_score}, Composite={composite_score}
PROFILE: Risk={risk_level}, Type={profile}, Trend={trend}, Weakest={weakest_domain}
DETAILS: Field={field}, Target={target_career}, Savings={savings_habit},
         Financial Discipline={fin_discipline}, Health={health_habits},
         Sleep={sleep_quality}, Study Hours/week={study_hours}, Skill={skill_level}

Return EXACTLY this JSON structure (no markdown fences, no extra text):
{{
  "academic_risk": "one sentence about academic risk pattern",
  "financial_risk": "one sentence about financial instability pattern",
  "career_signal": "one sentence about career stagnation or growth signal",
  "lifestyle_warning": "one sentence about lifestyle degradation or strength",
  "top_strength": "single phrase — their biggest asset",
  "top_threat": "single phrase — their biggest risk factor",
  "improvement_priority": "the ONE thing they must fix first",
  "recommendations": [
    {{"area": "Academic", "action": "specific action", "impact": "High/Medium/Low"}},
    {{"area": "Financial", "action": "specific action", "impact": "High/Medium/Low"}},
    {{"area": "Career", "action": "specific action", "impact": "High/Medium/Low"}},
    {{"area": "Lifestyle", "action": "specific action", "impact": "High/Medium/Low"}},
    {{"area": "Mindset", "action": "specific action", "impact": "High/Medium/Low"}}
  ]
}}
""".strip()
)


# ─── Chain Execution Helpers ──────────────────────────────────────────────────

def _run_chain(template: PromptTemplate, inputs: dict, temperature: float = 0.7) -> str:
    """Execute a single LangChain chain and return the string output."""
    llm   = _get_llm(temperature)
    chain = template | llm | StrOutputParser()
    try:
        return chain.invoke(inputs)
    except Exception as e:
        return f"[LLM unavailable: {e}]"


def _safe_json(text: str) -> dict:
    """Extract and parse JSON from LLM output robustly."""
    # Strip markdown fences if present
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        # Try to find a JSON object in the text
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


# ─── Public API ───────────────────────────────────────────────────────────────

def run_llm_analysis(processed: dict, scores: dict, behavior: dict, simulation: dict) -> dict:
    """
    Run all LLM chains and return consolidated output dict.
    Chain order:
      1. behavior_narrative  → prose description of current state
      2. future_narrative    → time-horizon prose (5/10/25 yr)
      3. insights_json       → structured JSON for recommendations
    """
    s = scores
    b = behavior
    p = processed
    sim = simulation

    # ── Chain 1: Behavior Narrative ──────────────────────────────────────────
    behavior_text = _run_chain(
        BEHAVIOR_NARRATIVE_TEMPLATE,
        {
            "name_placeholder": "the student",
            "age":           p["age"],
            "field":         p["field_of_study"],
            "cgpa":          p["cgpa"],
            "college_tier":  p["college_tier"],
            "target_career": p["target_career"],
            "skill_level":   p["skill_level"],
            "savings_habit": p["savings_habit"],
            "fin_discipline":p["fin_discipline"],
            "health_habits": p["health_habits"],
            "sleep_quality": p["sleep_quality"],
            "academic_score":  s["academic"],
            "financial_score": s["financial"],
            "career_score":    s["career"],
            "lifestyle_score": s["lifestyle"],
            "composite_score": s["composite"],
            "risk_level":      b["risk_level"],
            "profile":         b["profile"],
            "trend":           b["trend"],
            "weakest_domain":  b["weakest"],
            "strongest_domain":b["strongest"],
        },
        temperature=0.75,
    )

    # ── Chain 2: Future Narratives ───────────────────────────────────────────
    future_text = _run_chain(
        FUTURE_NARRATIVE_TEMPLATE,
        {
            "field":          p["field_of_study"],
            "target_career":  p["target_career"],
            "composite_score":s["composite"],
            "risk_level":     b["risk_level"],
            "trend":          b["trend"],
            "y5_career":  sim["5_year"]["career_stability"],
            "y5_fin":     sim["5_year"]["fin_condition"],
            "y5_income":  sim["5_year"]["income_lpa"],
            "y10_career": sim["10_year"]["career_stability"],
            "y10_fin":    sim["10_year"]["fin_condition"],
            "y10_income": sim["10_year"]["income_lpa"],
            "y25_career": sim["25_year"]["career_stability"],
            "y25_fin":    sim["25_year"]["fin_condition"],
            "y25_income": sim["25_year"]["income_lpa"],
        },
        temperature=0.80,
    )

    # Parse future narratives
    future_narratives = {"5_year": "", "10_year": "", "25_year": ""}
    for line in future_text.split("\n"):
        line = line.strip()
        if line.startswith("5_YEAR:"):
            future_narratives["5_year"] = line[7:].strip()
        elif line.startswith("10_YEAR:"):
            future_narratives["10_year"] = line[8:].strip()
        elif line.startswith("25_YEAR:"):
            future_narratives["25_year"] = line[8:].strip()

    # ── Chain 3: Structured Insights JSON ───────────────────────────────────
    insights_raw = _run_chain(
        INSIGHTS_JSON_TEMPLATE,
        {
            "academic_score":  s["academic"],
            "financial_score": s["financial"],
            "career_score":    s["career"],
            "lifestyle_score": s["lifestyle"],
            "composite_score": s["composite"],
            "risk_level":      b["risk_level"],
            "profile":         b["profile"],
            "trend":           b["trend"],
            "weakest_domain":  b["weakest"],
            "field":           p["field_of_study"],
            "target_career":   p["target_career"],
            "savings_habit":   p["savings_habit"],
            "fin_discipline":  p["fin_discipline"],
            "health_habits":   p["health_habits"],
            "sleep_quality":   p["sleep_quality"],
            "study_hours":     p["study_hours"],
            "skill_level":     p["skill_level"],
        },
        temperature=0.3,  # Low temp for structured output
    )
    insights_json = _safe_json(insights_raw)

    return {
        "behavior_narrative": behavior_text,
        "future_narratives":  future_narratives,
        "insights_json":      insights_json,
        "raw_insights":       insights_raw,
    }


def generate_lifestyle_prompt(
    processed: dict, scores: dict, behavior: dict,
    simulation: dict, llm_output: dict, horizon: str
) -> str:
    """Generate the image scene prompt for a given time horizon."""
    sim_h    = simulation[horizon]
    narr     = llm_output["future_narratives"].get(horizon, "")
    snippet  = narr[:200] if narr else f"{sim_h['career_stability']} professional lifestyle"

    labels = {"5_year": "5 Years from Now", "10_year": "10–15 Years from Now", "25_year": "25+ Years from Now"}

    return _run_chain(
        IMAGE_SCENE_TEMPLATE,
        {
            "horizon_label":    labels[horizon],
            "career_stability": sim_h["career_stability"],
            "fin_condition":    sim_h["fin_condition"],
            "lifestyle_qual":   sim_h["lifestyle_qual"],
            "composite_score":  sim_h["composite"],
            "field":            processed["field_of_study"],
            "location":         processed["location"],
            "narrative_snippet":snippet,
        },
        temperature=0.85,
    )
