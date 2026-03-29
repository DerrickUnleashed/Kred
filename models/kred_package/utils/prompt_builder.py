"""
utils/prompt_builder.py — Reusable, parameterised prompt factories.

All prompts enforce strict JSON output so json_parser can extract cleanly.
Keeping prompts here avoids scattering f-strings throughout engine logic.
"""

from __future__ import annotations

from typing import Any


# ── Helper ─────────────────────────────────────────────────────────────────────
def _indent(text: str, spaces: int = 2) -> str:
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())


# ══════════════════════════════════════════════════════════════════════════════
#  FUTURE SELF ENGINE PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def future_self_scenario_prompt(
    *,
    horizon_label: str,
    age: int,
    country: str,
    field: str,
    career_status: str,
    fin_status: str,
    life_quality: str,
    income_lpa: float,
    scores: dict[str, Any],
) -> str:
    """
    Builds a structured scenario narrative prompt for one time horizon.
    Forces JSON output with a 'narrative' key.
    """
    return f"""\
You are a behavioural scientist and life-trajectory expert writing vivid,
country-aware daily-life narratives.

CONTEXT:
  Horizon   : {horizon_label} from now
  Age       : {age}
  Country   : {country}
  Field     : {field}
  Career    : {career_status}
  Finances  : {fin_status}
  Quality   : {life_quality}
  Income    : ₹{income_lpa} LPA
  Scores    :
    Academic  {scores.get('academic', 0):.1f}/100
    Financial {scores.get('financial', 0):.1f}/100
    Career    {scores.get('career', 0):.1f}/100
    Lifestyle {scores.get('lifestyle', 0):.1f}/100
    Composite {scores.get('composite', 0):.1f}/100

TASK:
Write ONE vivid paragraph (5-7 sentences) describing this person's daily life
covering: morning routine & home environment in {country}, their work setup,
financial reality, physical energy & health, and the emotional tone of their life.
Be specific, grounded, and honest. No generic platitudes.

RESPOND ONLY with valid JSON — no preamble, no markdown fences:
{{"narrative": "<your paragraph here>"}}"""


def future_self_analysis_prompt(
    *,
    user: dict[str, Any],
    scores: dict[str, Any],
    sim: dict[str, Any],
) -> str:
    """Deep analysis prompt — returns structured JSON sections."""
    country = user.get("country", "India")
    return f"""\
You are a behavioural scientist and life-trajectory expert.

STUDENT PROFILE:
  Age {user['age']} | Country: {country} | {user['edu_level']} in {user['field']} | {user['college_tier']}
  CGPA: {user['cgpa']} | Study hrs/wk: {user['study_hours']} | Target: {user['target_career']}
  Skill: {user['skill']} | Experience: {user['experience']} | Consistency: {user['consistency']}
  Monthly spend: ₹{user['monthly_spend']} | Savings: {user['savings']} | Family BG: {user['family_bg']}
  Discipline: {user['discipline']} | Screen: {user['screen_time']} | Health: {user['health']} | Sleep: {user['sleep']}

SCORES:
  Academic {scores['academic']} | Financial {scores['financial']} | Career {scores['career']} | Lifestyle {scores['lifestyle']}
  Composite {scores['composite']} | Risk: {scores['risk']} | Trend: {scores['trend']}

PROJECTIONS:
  5yr  → {sim['5_year']['career_status']} | {sim['5_year']['fin_status']} | ₹{sim['5_year']['income_lpa']} LPA
  10yr → {sim['10_year']['career_status']} | {sim['10_year']['fin_status']} | ₹{sim['10_year']['income_lpa']} LPA
  25yr → {sim['25_year']['career_status']} | {sim['25_year']['fin_status']} | ₹{sim['25_year']['income_lpa']} LPA

TASK: Write a comprehensive trajectory analysis for this student in {country}.

RESPOND ONLY with valid JSON — no preamble, no markdown:
{{
  "current_state": "<3-4 brutally honest sentences>",
  "five_year_outlook": "<vivid paragraph>",
  "ten_year_outlook": "<vivid paragraph>",
  "twenty_five_year_outlook": "<vivid paragraph>",
  "key_risks": ["<risk1>", "<risk2>", "<risk3>", "<risk4>", "<risk5>"],
  "top_strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "priority_actions": ["<action1>", "<action2>", "<action3>", "<action4>", "<action5>"]
}}"""


# ══════════════════════════════════════════════════════════════════════════════
#  BEHAVIOR ANALYSIS ENGINE PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def behavior_analysis_prompt(
    *,
    user_id: int,
    risk_level: str,
    behavior_score: int,
    behavior_profile: str,
    overspending: dict[str, Any],
    categories: list[dict[str, Any]],
    trend: dict[str, Any],
    insights: list[str],
    raw_recommendations: list[str],
) -> str:
    """
    Enriches the rule-based behavior analysis with LLM-driven narrative
    and prioritised recommendations. Returns structured JSON.
    """
    high_risk_cats = [c["category"] for c in categories if c.get("risk") == "high"]
    return f"""\
You are a personal finance AI assistant with deep expertise in behavioural economics.

USER FINANCIAL BEHAVIOR SUMMARY:
  User ID         : {user_id}
  Risk Level      : {risk_level}
  Behavior Score  : {behavior_score}/100
  Profile         : {behavior_profile}
  Overspend Freq  : {overspending.get('frequency', 0):.1%} of days
  Avg Daily Dev   : ₹{overspending.get('avg_deviation', 0):.0f} from limit
  Weekly Trend    : {trend.get('weekly_trend', 'unknown')}
  High-Risk Cats  : {', '.join(high_risk_cats) if high_risk_cats else 'None'}

RULE-BASED INSIGHTS: {insights}
INITIAL ACTIONS   : {raw_recommendations}

TASK:
1. Validate and enrich the insights with behavioural science context.
2. Prioritise the top 5 concrete, measurable actions.
3. Add a short motivational summary (2 sentences) calibrated to the risk level.

RESPOND ONLY with valid JSON — no preamble, no markdown:
{{
  "enriched_insights": ["<insight1>", "<insight2>", "<insight3>"],
  "priority_actions": ["<action1>", "<action2>", "<action3>", "<action4>", "<action5>"],
  "motivational_summary": "<2 sentences>",
  "behavioral_archetype": "<one of: Impulsive Spender | Cautious Saver | Balanced Manager | Disciplined Investor>"
}}"""


# ══════════════════════════════════════════════════════════════════════════════
#  LIFEPATH REGRET ENGINE PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def lifepath_regret_prompt(
    *,
    user_id: int,
    avg_daily_spend: float,
    daily_limit: float,
    overspend_frequency: float,
    compounded_loss_5y: float,
    compounded_loss_10y: float,
    opportunity_cost_5y: float,
    opportunity_cost_10y: float,
    risk_profile: str,
    behavior_profile: str,
) -> str:
    """
    Builds the LifePath Regret Engine prompt with pre-computed financial math.
    All monetary values are injected so the LLM focuses on narrative + insight,
    not arithmetic (which LLMs do poorly).
    """
    return f"""\
You are a financial psychologist specialising in long-term regret analysis
and the emotional cost of poor financial decisions.

PRE-COMPUTED FINANCIAL ANALYSIS:
  User ID               : {user_id}
  Avg Daily Spend       : ₹{avg_daily_spend:.0f}
  Daily Limit           : ₹{daily_limit:.0f}
  Overspend Days        : {overspend_frequency:.1%} of total days
  Risk Profile          : {risk_profile}
  Behavior Profile      : {behavior_profile}

COMPOUNDED FINANCIAL LOSS (at {12:.0f}% annual CAGR opportunity cost):
  5-year compounded loss      : ₹{compounded_loss_5y:,.0f}
  10-year compounded loss     : ₹{compounded_loss_10y:,.0f}
  5-year opportunity cost     : ₹{opportunity_cost_5y:,.0f}
  10-year opportunity cost    : ₹{opportunity_cost_10y:,.0f}

TASK:
Write a deeply personalised LifePath Regret analysis. Cover:
1. The emotional reality of these numbers at year 5 and year 10.
2. What this person will likely be unable to afford due to compounding losses.
3. A concrete "redemption path" — what changes today lead to which outcome.
4. One powerful metaphor that captures their current trajectory.

RESPOND ONLY with valid JSON — no preamble, no markdown:
{{
  "regret_score": <integer 0-100, higher = more regret>,
  "five_year_regret": "<vivid 2-3 sentence description of financial pain at year 5>",
  "ten_year_regret": "<vivid 2-3 sentence description at year 10>",
  "missed_milestones": ["<milestone1>", "<milestone2>", "<milestone3>"],
  "redemption_path": "<concrete 3-step path to reverse trajectory>",
  "trajectory_metaphor": "<one powerful metaphor>",
  "urgency_level": "<one of: Critical | High | Moderate | Low>"
}}"""
