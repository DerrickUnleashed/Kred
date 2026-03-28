"""
Future Life Simulator — Enhanced v5.0
=======================================
• Captures name + personal details for personalized experience
• Generates ONE single photorealistic lifestyle image (not per-year)
• Uses FLUX.1-schnell for hyper-realistic image generation
• Groq (Llama 3.3) for deep narrative analysis
• Scoring engine unchanged from v4.0

Run:  streamlit run app.py
Env:  GROQ_API_KEY    mandatory
      HF_TOKEN        mandatory for FLUX
"""

import os, io, json, datetime, random, math
from pathlib import Path

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

from groq import Groq

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Future Life Simulator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  STYLES — cinematic dark editorial
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,500;1,700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg:#05060c; --bg2:#090b16; --bg3:#0d0f1e;
  --border:rgba(255,255,255,.055); --gold:rgba(232,184,75,1);
  --gold2:#f5d080; --cyan:#22d3ee; --red:#fb7185;
  --green:#34d399; --amber:#fb923c;
  --text:#e4e8f5; --text2:rgba(228,232,245,.48); --text3:rgba(228,232,245,.26);
}

html,body,[class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:var(--bg); color:var(--text); }

/* ── HERO ── */
.hero {
  background:linear-gradient(135deg,#06080f 0%,#0e0b20 48%,#060d13 100%);
  border:1px solid rgba(232,184,75,.16);
  border-radius:22px; padding:3rem 2.8rem 2.6rem;
  margin-bottom:2.2rem; position:relative; overflow:hidden;
}
.hero::before { content:''; position:absolute; top:-120px; right:-80px; width:380px; height:380px;
  background:radial-gradient(circle,rgba(232,184,75,.1) 0%,transparent 65%); border-radius:50%; }
.hero::after  { content:''; position:absolute; bottom:-70px; left:-50px; width:240px; height:240px;
  background:radial-gradient(circle,rgba(34,211,238,.07) 0%,transparent 65%); border-radius:50%; }
.hero-eyebrow { font-family:'JetBrains Mono',monospace; font-size:.6rem; letter-spacing:.32em;
  text-transform:uppercase; color:rgba(232,184,75,.7); margin-bottom:.7rem; position:relative; z-index:1; }
.hero-title { font-family:'Bebas Neue',sans-serif; font-size:4.2rem; letter-spacing:.06em;
  line-height:.92; color:#f2ead6; position:relative; z-index:1; }
.hero-title em { color:var(--gold); font-style:normal; }
.hero-sub { font-size:.87rem; color:var(--text2); font-weight:300; margin-top:.9rem;
  position:relative; z-index:1; letter-spacing:.03em; max-width:580px; line-height:1.7; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] { background:#040508 !important; border-right:1px solid rgba(232,184,75,.09); }
.sb-logo { font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:.2em; color:var(--gold);
  border-bottom:1px solid rgba(232,184,75,.1); padding-bottom:.7rem; margin-bottom:1rem; }
.sb-sec { font-family:'JetBrains Mono',monospace; font-size:.56rem; letter-spacing:.26em;
  text-transform:uppercase; color:var(--text3); margin:1.2rem 0 .38rem; }
.sb-user-preview { background:rgba(232,184,75,.05); border:1px solid rgba(232,184,75,.15);
  border-radius:12px; padding:.9rem 1rem; margin:.7rem 0; }
.sb-user-name { font-family:'Cormorant Garamond',serif; font-size:1.2rem; font-weight:700;
  color:#f2ead6; }
.sb-user-detail { font-family:'JetBrains Mono',monospace; font-size:.62rem;
  color:var(--text2); margin-top:.25rem; }

/* ── WIDGETS ── */
.stSelectbox>div>div,.stNumberInput>div,.stTextInput>div>div {
  background:rgba(255,255,255,.022) !important; border-color:rgba(232,184,75,.14) !important;
  border-radius:9px !important; color:var(--text) !important; }
.stTextArea textarea { background:rgba(255,255,255,.022) !important;
  border-color:rgba(232,184,75,.14) !important; border-radius:9px !important; color:var(--text) !important; }
.stButton>button {
  background:linear-gradient(135deg,#9a6e1a,#e8b84b) !important;
  color:#050609 !important; border:none !important; border-radius:11px !important;
  font-family:'JetBrains Mono',monospace !important; font-weight:600 !important;
  letter-spacing:.09em !important; padding:.72rem 1.6rem !important;
  transition:all .22s !important; font-size:.78rem !important; text-transform:uppercase !important; }
.stButton>button:hover { transform:translateY(-2px) !important;
  box-shadow:0 10px 36px rgba(232,184,75,.32) !important; }
.stProgress>div>div { background:linear-gradient(90deg,var(--gold),var(--cyan)) !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important;
  border-bottom:1px solid rgba(232,184,75,.11); gap:.3rem; }
.stTabs [data-baseweb="tab"] { font-family:'JetBrains Mono',monospace !important; font-size:.66rem !important;
  letter-spacing:.13em !important; color:var(--text3) !important; text-transform:uppercase !important;
  border:none !important; background:transparent !important; padding:.55rem .9rem !important; }
.stTabs [aria-selected="true"] { color:var(--gold) !important; border-bottom:2px solid var(--gold) !important; }

/* ── CARDS ── */
.card { background:rgba(255,255,255,.018); border:1px solid var(--border);
  border-radius:14px; padding:1.3rem 1.5rem; margin-bottom:1rem; }
.card-gold { background:rgba(232,184,75,.038); border:1px solid rgba(232,184,75,.18);
  border-radius:14px; padding:1.3rem 1.5rem; margin-bottom:1rem; }
.card-person { background:linear-gradient(135deg,rgba(232,184,75,.06),rgba(34,211,238,.03));
  border:1px solid rgba(232,184,75,.2); border-radius:16px; padding:1.5rem 1.6rem; margin-bottom:1.2rem; }

/* ── PERSON BANNER ── */
.person-name { font-family:'Cormorant Garamond',serif; font-size:2rem;
  font-weight:700; color:#f2ead6; line-height:1.1; }
.person-meta { font-family:'JetBrains Mono',monospace; font-size:.68rem;
  color:var(--text2); margin-top:.3rem; letter-spacing:.05em; }
.person-tag { display:inline-block; background:rgba(232,184,75,.1);
  border:1px solid rgba(232,184,75,.22); border-radius:6px;
  font-family:'JetBrains Mono',monospace; font-size:.62rem;
  color:var(--gold); padding:.18rem .55rem; margin:.15rem .1rem; }

/* ── KPI ── */
.kpi { background:rgba(3,4,10,.88); border:1px solid rgba(232,184,75,.14);
  border-radius:14px; padding:1.2rem; text-align:center; }
.kpi-label { font-family:'JetBrains Mono',monospace; font-size:.56rem;
  letter-spacing:.22em; text-transform:uppercase; color:var(--text3); margin-bottom:.5rem; }
.kpi-value { font-family:'Cormorant Garamond',serif; font-size:2.4rem;
  font-weight:700; line-height:1; }
.kpi-sub { font-size:.73rem; color:var(--text3); margin-top:.3rem; }

/* ── BADGES ── */
.b-low  { background:#071d12;border:1px solid #34d399;color:#34d399;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:600;display:inline-block; }
.b-mod  { background:#1c1208;border:1px solid #fbbf24;color:#fbbf24;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:600;display:inline-block; }
.b-high { background:#1a0808;border:1px solid #fb7185;color:#fb7185;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:600;display:inline-block; }

/* ── ALERTS ── */
.a-ok   { background:#071d12;border-left:3px solid #34d399;border-radius:0 9px 9px 0;padding:.85rem 1.1rem;font-size:.86rem;margin:.5rem 0; }
.a-warn { background:#1c1208;border-left:3px solid #fbbf24;border-radius:0 9px 9px 0;padding:.85rem 1.1rem;font-size:.86rem;margin:.5rem 0; }
.a-err  { background:#1a0808;border-left:3px solid #fb7185;border-radius:0 9px 9px 0;padding:.85rem 1.1rem;font-size:.86rem;margin:.5rem 0; }

/* ── NARRATIVE ── */
.narrative { background:rgba(232,184,75,.04); border-left:3px solid var(--gold);
  border-radius:0 13px 13px 0; padding:1.1rem 1.4rem;
  font-size:.9rem; line-height:1.92; color:rgba(232,226,210,.88); margin:.8rem 0; }

/* ── SCORE ROW ── */
.score-row { display:flex; justify-content:space-between; align-items:center; margin:.28rem 0; }
.score-bar-bg { flex:1; height:4px; background:rgba(255,255,255,.05);
  border-radius:2px; margin:0 .6rem; }

/* ── IMAGE SHOWCASE ── */
.img-showcase { border:1px solid rgba(232,184,75,.2); border-radius:18px;
  overflow:hidden; box-shadow:0 20px 80px rgba(0,0,0,.75); position:relative; }

/* ── TIMELINE CARD ── */
.tl-card { background:linear-gradient(145deg,rgba(10,12,26,.95),rgba(5,7,16,.95));
  border:1px solid rgba(232,184,75,.17); border-radius:14px; padding:1.2rem; }
.tl-year { font-family:'JetBrains Mono',monospace;font-size:.56rem;letter-spacing:.24em;color:rgba(232,184,75,.58);margin-bottom:.4rem; }
.tl-income { font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:700;color:var(--gold); }
.tl-stat { font-family:'JetBrains Mono',monospace;font-size:.64rem;color:var(--text3);margin-top:.2rem; }

/* ── WELCOME ── */
.welcome { border:1px solid rgba(232,184,75,.11); border-radius:22px;
  padding:4.5rem 2.8rem; text-align:center;
  background:linear-gradient(145deg,rgba(7,8,16,.88),rgba(3,4,10,.96)); margin-top:1rem; }
.welcome-title { font-family:'Bebas Neue',sans-serif;font-size:3rem;letter-spacing:.06em;color:#f2ead6;margin-bottom:.7rem; }
.welcome-body { color:var(--text2);max-width:520px;margin:0 auto 1.5rem;line-height:1.85;font-size:.9rem; }

hr { border-color:var(--border) !important; }
.stDownloadButton>button { background:rgba(232,184,75,.07) !important; color:var(--gold) !important;
  border:1px solid rgba(232,184,75,.2) !important; border-radius:7px !important;
  font-family:'JetBrains Mono',monospace !important; font-size:.66rem !important;
  padding:.35rem .8rem !important; text-transform:uppercase !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  OUTPUT DIRS + SESSION
# ══════════════════════════════════════════════════════════════════════════════
OUTPUT_DIR = Path("models/FSVE")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_SESS_DEFAULTS = dict(
    scores={}, simulation={}, llm_analysis="",
    life_narrative="", flux_prompt="", final_image=None,
    analysis_done=False,
)
for k, v in _SESS_DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  GROQ CLIENT
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_groq_client():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return None
    try:
        return Groq(api_key=key)
    except Exception:
        return None

def groq_call(prompt: str, temperature: float = 0.72, max_tokens: int = 2048) -> str:
    client = get_groq_client()
    if not client:
        return "[Groq API key not configured — add GROQ_API_KEY to .env]"
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return completion.choices[0].message.content.strip() or "[Empty response]"
    except Exception as e:
        return f"[Groq error: {e}]"

# ══════════════════════════════════════════════════════════════════════════════
#  SCORING ENGINE (unchanged from v4.0)
# ══════════════════════════════════════════════════════════════════════════════
def score_academic(cgpa, study_hours, college_tier, edu_level) -> float:
    cgpa_n  = (cgpa / 4.0 if cgpa <= 4.0 else cgpa / 10.0) * 100
    study_s = min(study_hours / 42.0 * 100, 100)
    tier_s  = {"Tier 1": 95, "Tier 2": 65, "Tier 3": 38}[college_tier]
    lvl_m   = {"High School": .80, "Undergraduate": 1.0, "Postgraduate": 1.15, "PhD": 1.25}[edu_level]
    return round(min((cgpa_n * .50 + study_s * .30 + tier_s * .20) * lvl_m, 100), 1)

def score_financial(monthly_spend, savings, family_bg, discipline) -> float:
    sv = {"Low": 28, "Medium": 62, "High": 92}[savings]
    di = {"Impulsive": 22, "Balanced": 58, "Disciplined": 94}[discipline]
    fa = {"Low": 38, "Middle": 65, "High": 88}[family_bg]
    sp = max(0, 100 - monthly_spend / 500.0)
    return round(min(sv*.35 + di*.35 + fa*.20 + sp*.10, 100), 1)

def score_career(skill, experience, consistency) -> float:
    sk = {"Beginner": 38, "Intermediate": 68, "Advanced": 94}[skill]
    ex = 88 if experience else 48
    co = {"Low": 32, "Medium": 62, "High": 92}[consistency]
    return round(min(sk*.40 + ex*.35 + co*.25, 100), 1)

def score_lifestyle(screen, health, sleep) -> float:
    sk = screen.split()[0]
    sc = {"Low": 88, "Medium": 58, "High": 28}.get(sk, 55)
    hc = {"Poor": 28, "Average": 58, "Good": 92}[health]
    sl = {"Poor": 32, "Average": 62, "Good": 92}[sleep]
    return round(min(hc*.38 + sl*.38 + sc*.24, 100), 1)

def compute_scores(u: dict) -> dict:
    ac = score_academic(u["cgpa"], u["study_hours"], u["college_tier"], u["edu_level"])
    fi = score_financial(u["monthly_spend"], u["savings"], u["family_bg"], u["discipline"])
    ca = score_career(u["skill"], u["experience"], u["consistency"])
    li = score_lifestyle(u["screen_time"], u["health"], u["sleep"])
    co = round(ac*.30 + fi*.25 + ca*.25 + li*.20, 1)
    risk    = "Low" if co > 74 else ("Moderate" if co >= 50 else "High")
    profile = "Disciplined" if co > 74 else ("Balanced" if co >= 50 else "At Risk")
    trend   = ("Improving" if ac > 68 and ca > 68 else
               "Declining" if ac < 48 or ca < 48 else "Stable")
    return dict(academic=ac, financial=fi, career=ca, lifestyle=li,
                composite=co, risk=risk, profile=profile, trend=trend)

def simulate(u: dict, s: dict) -> dict:
    """Project to a SINGLE future horizon: 10 years (the primary visualisation point)."""
    r_map = {"Improving": .026, "Stable": .005, "Declining": -.022}
    r = r_map[s["trend"]]
    income_base = {
        "Engineering / Technology": 7, "Science": 5, "Commerce / Business": 5.5,
        "Arts / Humanities": 3, "Medicine / Healthcare": 8, "Law": 5.5, "Other": 4,
    }.get(u["field"], 4.5)
    sm = {"Beginner": .7, "Intermediate": 1.0, "Advanced": 1.35}[u["skill"]]
    tm = {"Tier 1": 1.3, "Tier 2": 1.0, "Tier 3": .75}[u["college_tier"]]

    def lbl(v, ls): return ls[min(int(v / 20), len(ls) - 1)]
    out = {}
    for yrs, key in [(5, "5_year"), (10, "10_year"), (25, "25_year")]:
        proj = {d: round(min(100, max(0, s[d] * ((1 + r) ** yrs))), 1)
                for d in ("academic", "financial", "career", "lifestyle")}
        co   = round(proj["academic"]*.30 + proj["financial"]*.25 +
                     proj["career"]*.25   + proj["lifestyle"]*.20, 1)
        income = round(income_base * sm * tm * (1.085 ** yrs) * (co / 65.0), 1)
        out[key] = {
            "years": yrs, "age": u["age"] + yrs, **proj, "composite": co,
            "career_status": lbl(proj["career"],   ["Unstable","Emerging","Stable","Strong","Elite"]),
            "fin_status":    lbl(proj["financial"], ["Struggling","Tight","Moderate","Comfortable","Wealthy"]),
            "life_quality":  lbl(proj["lifestyle"], ["Poor","Below Avg","Average","Good","Excellent"]),
            "income_lpa":    income,
        }
    return out

# ══════════════════════════════════════════════════════════════════════════════
#  GROQ: COMPREHENSIVE ANALYSIS + LIFE NARRATIVE
# ══════════════════════════════════════════════════════════════════════════════
def run_analysis(u: dict, s: dict, sim: dict) -> str:
    name = u.get("name", "the student")
    prompt = f"""You are a behavioural scientist and life-trajectory expert.

PERSONAL PROFILE:
Name: {name} | Age: {u['age']} | Gender: {u.get('gender','Not specified')}
Country: {u.get('country','India')} | Occupation/Goal: {u.get('occupation','')}
Bio note: {u.get('bio','')}

ACADEMIC: {u['edu_level']} in {u['field']} | {u['college_tier']} | CGPA {u['cgpa']} | {u['study_hours']} hrs/wk study
CAREER: Target: {u['target_career']} | Skill: {u['skill']} | Experience: {u['experience']} | Consistency: {u['consistency']}
FINANCIAL: ₹{u['monthly_spend']}/mo spend | Savings: {u['savings']} | Family: {u['family_bg']} | Discipline: {u['discipline']}
LIFESTYLE: Screen: {u['screen_time']} | Health: {u['health']} | Sleep: {u['sleep']}

SCORES: Academic {s['academic']} | Financial {s['financial']} | Career {s['career']} | Lifestyle {s['lifestyle']}
Composite {s['composite']} | Risk: {s['risk']} | Trend: {s['trend']}

PROJECTIONS:
5yr  → {sim['5_year']['career_status']} | {sim['5_year']['fin_status']} | ₹{sim['5_year']['income_lpa']} LPA (Age {sim['5_year']['age']})
10yr → {sim['10_year']['career_status']} | {sim['10_year']['fin_status']} | ₹{sim['10_year']['income_lpa']} LPA (Age {sim['10_year']['age']})
25yr → {sim['25_year']['career_status']} | {sim['25_year']['fin_status']} | ₹{sim['25_year']['income_lpa']} LPA (Age {sim['25_year']['age']})

Address {name} directly throughout. Write with warmth, honesty, and precision.

**CURRENT STATE**
3–4 sentences addressing {name} directly. Be honest, specific, compassionate.

**10-YEAR VISION**
A vivid paragraph painting {name}'s life in {u.get('country','India')} at age {sim['10_year']['age']}.
Their home, desk, morning routine, city, emotional state, financial freedom or constraint.

**25-YEAR OUTLOOK**
One paragraph on retirement readiness, health, legacy, life satisfaction.

**KEY RISKS**
3–5 specific bullet points. Data-referenced. No platitudes.

**TOP STRENGTHS**
2–3 bullet points. Genuine competitive advantages for {name}.

**PRIORITY ACTIONS — 5 Steps for {name}**
5 numbered, concrete, measurable steps tailored to their specific situation.

Be brutally honest yet kind. Reference the country context ({u.get('country','India')})."""
    return groq_call(prompt, 0.72, 2048)


def run_life_narrative(u: dict, s: dict, sim: dict) -> str:
    """Generate the vivid one-paragraph narrative used to build the FLUX prompt."""
    name  = u.get("name", "this person")
    d     = sim["10_year"]  # primary visualisation horizon
    prompt = f"""Describe the PHYSICAL ENVIRONMENT and DAILY LIFE of {name} 10 years from now in {u.get('country','India')}.

Scores → Academic:{s['academic']} Financial:{s['financial']} Career:{s['career']} Lifestyle:{s['lifestyle']}
Outcome → Career:{d['career_status']} Finance:{d['fin_status']} Quality:{d['life_quality']}
Income: ₹{d['income_lpa']} LPA | Age: {d['age']} | Field: {u['field']} | Country: {u.get('country','India')}

Write ONE vivid, sensory paragraph (6–8 sentences):
• Their home / room — specific objects, lighting, city visible outside
• Their desk and work setup — what is on the screen, quality of equipment
• Their clothing and physical appearance (energy, posture, well-dressed or dishevelled)
• One specific activity they are doing at this desk at this moment
• The emotional atmosphere — calm confidence, stress, contentment, struggle

No advice. Be specific, cinematic, grounded in the scores."""
    return groq_call(prompt, 0.88, 512)

# ══════════════════════════════════════════════════════════════════════════════
#  HYPER-REALISTIC FLUX PROMPT BUILDER — single scene
# ══════════════════════════════════════════════════════════════════════════════
def build_flux_prompt(u: dict, s: dict, sim: dict) -> str:
    """Builds a hyper-realistic FLUX prompt that consistently produces photorealistic images"""
    d       = sim["10_year"]
    fin_s   = d["fin_status"]
    car_s   = d["career_status"]
    lif_s   = d["life_quality"]
    age     = d["age"]
    income  = d["income_lpa"]
    country = u.get("country", "India")
    field   = u.get("field",   "Engineering / Technology")
    name    = u.get("name",    "the professional")

    # ── Wealth environment (minimal, realistic) ────────────────────────────────
    wealth_env = {
        "Wealthy": "ultra-luxury penthouse interior, floor-to-ceiling windows with panoramic city skyline, polished marble floors, designer furniture, minimalist luxury",
        "Comfortable": "modern apartment interior, large windows with city view, hardwood floors, quality contemporary furniture, well-lit",
        "Moderate": "standard apartment interior, laminate flooring, functional furniture, typical urban living space",
        "Tight": "small room interior, basic furniture, simple desk, modest living space",
        "Struggling": "sparse room interior, worn furniture, minimal possessions, humble living environment",
    }.get(fin_s, "apartment interior with standard furniture")

    # ── Career context (minimal) ────────────────────────────────────────────────
    career_ctx = {
        "Elite": "high-end professional workspace with multiple displays",
        "Strong": "professional workspace with dual monitors, organized desk",
        "Stable": "standard workspace with monitor, typical office setup",
        "Emerging": "simple workspace with laptop, basic setup",
        "Unstable": "makeshift workspace with laptop",
    }.get(car_s, "desk workspace")

    # ── Lifestyle signals ──────────────────────────────────────────────────────
    life_ctx = {
        "Excellent": "bright natural light, healthy plants, organized space",
        "Good": "clean organized space, natural lighting",
        "Average": "lived-in space, moderate tidiness",
        "Below Avg": "slightly cluttered, dim lighting",
        "Poor": "disorganized, poor lighting",
    }.get(lif_s, "functional space")

    # ── Country context ─────────────────────────────────────────────────────────
    country_ctx = {
        "India": "Indian apartment interior, typical Indian urban setting",
        "United States": "American apartment interior, US urban view",
        "United Kingdom": "UK flat interior, British architecture",
        "Canada": "Canadian apartment interior, North American style",
        "Australia": "Australian apartment interior, coastal light",
        "Germany": "German apartment interior, European style",
        "Singapore": "Singapore apartment interior, tropical city view",
        "UAE": "Dubai apartment interior, modern architecture",
    }.get(country, f"{country} apartment interior")

    # ── Lighting (realistic) ────────────────────────────────────────────────────
    light = {
        "Excellent": "golden hour sunlight streaming through windows",
        "Good": "bright morning natural light",
        "Average": "neutral afternoon daylight",
        "Below Avg": "evening lamp light",
        "Poor": "artificial overhead light",
    }.get(lif_s, "natural daylight")

    # ── HYPER-REALISTIC PROMPT (stripped of numbers and text-inducing elements) ──
    prompt = f"""REAL PHOTOGRAPH. Interior scene. {wealth_env}. {career_ctx}. {country_ctx}. {light}. {life_ctx}.

Style: Editorial interior photography. Shot on Hasselblad medium format camera. 50mm lens. Natural ambient light. Shallow depth of field. Architectural Digest magazine quality. Photorealistic. Professional real estate photography. Hyper-detailed textures. Realistic materials. Natural reflections. Cinematic composition.

CRITICAL: NO text. NO words. NO letters. NO numbers. NO people. NO human figures. NO faces. NO watermarks. NO logos. NO signs. NO labels. NO CGI. NO 3D render. NO illustration. NO cartoon. NO animation. NO stylized elements. NO AI artifacts. NO pixelation."""
    
    return prompt

# ══════════════════════════════════════════════════════════════════════════════
#  FLUX IMAGE GENERATION — HYPER-REALISTIC
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_hf_client():
    try:
        from huggingface_hub import InferenceClient
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        return InferenceClient(token=token) if token else None
    except Exception:
        return None


def generate_flux_image(prompt: str) -> Image.Image | None:
    """Generate hyper-realistic FLUX image with strict parameters"""
    client = get_hf_client()
    if not client:
        return None

    # Enhanced prompt with explicit photorealism instructions
    enhanced_prompt = f"""{prompt}

IMPORTANT: This is a REAL PHOTOGRAPH taken with a professional camera. The image must look exactly like a high-end architectural photography spread. No text anywhere. No artificial elements. Pure realism."""
    
    try:
        result = client.text_to_image(
            prompt=enhanced_prompt,
            model="black-forest-labs/FLUX.1-schnell",
            parameters={
                "guidance_scale": 7.5,
                "num_inference_steps": 12,
                "width": 1024,
                "height": 768,
            }
        )
        
        if isinstance(result, Image.Image):
            img = result.resize((1024, 768), Image.LANCZOS)
            # Crop bottom 10% to remove any potential text
            w, h = img.size
            img = img.crop((0, 0, w, int(h * 0.92)))
            return img
            
        img = Image.open(io.BytesIO(result))
        img = img.resize((1024, 768), Image.LANCZOS)
        w, h = img.size
        img = img.crop((0, 0, w, int(h * 0.92)))
        return img
        
    except Exception as e:
        st.warning(f"FLUX generation error: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  PIL FALLBACK — hyper-realistic scene
# ══════════════════════════════════════════════════════════════════════════════
def make_fallback_image(u: dict, s: dict, sim: dict) -> Image.Image:
    """Hyper-realistic PIL fallback when FLUX unavailable"""
    W, H    = 1024, 768
    d       = sim["10_year"]
    fin_s   = d["fin_status"]
    car_s   = d["career_status"]
    lif_s   = d["life_quality"]
    comp    = d["composite"]
    income  = d["income_lpa"]
    age     = d["age"]
    field   = u.get("field", "Engineering / Technology")

    fin_r = {"Struggling":0,"Tight":1,"Moderate":2,"Comfortable":3,"Wealthy":4}.get(fin_s, 2)
    car_r = {"Unstable":0,"Emerging":1,"Stable":2,"Strong":3,"Elite":4}.get(car_s, 2)
    lif_r = {"Poor":0,"Below Avg":1,"Average":2,"Good":3,"Excellent":4}.get(lif_s, 2)
    rng   = random.Random(int(comp * 100 + age * 333))

    # Realistic color palettes
    skies = {
        4:[(4,7,20),(12,18,46)], 3:[(7,13,30),(17,25,52)],
        2:[(13,17,36),(23,29,50)], 1:[(17,17,28),(27,25,38)],
        0:[(19,13,13),(29,19,17)],
    }
    c1, c2 = skies.get(fin_r, skies[2])

    canvas = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(canvas)

    # Background gradient
    for y in range(H):
        t = y / H
        draw.line([(0,y),(W,y)], fill=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)))

    # City skyline
    sky_y = int(H * .52)
    if fin_r >= 1:
        for _ in range(4 + fin_r*3):
            bx = rng.randint(-40,W+40)
            bh = rng.randint(int(50+fin_r*26), int(105+fin_r*52))
            bw = rng.randint(20, 42+fin_r*8)
            bc = tuple(int(c1[i]+rng.randint(5,22)) for i in range(3))
            draw.rectangle([bx, sky_y-bh, bx+bw, sky_y+3], fill=bc)

    # Wall + floor
    floor_y = int(H * .62)
    wall_colors = {4:(26,22,42),3:(34,38,52),2:(42,42,56),1:(50,46,44),0:(56,48,40)}
    wc = wall_colors.get(fin_r, (42,42,56))
    for y in range(int(H*.30), floor_y+5):
        t = (y-int(H*.30))/(floor_y-int(H*.30))
        draw.line([(0,y),(W,y)], fill=tuple(max(0,int(wc[i]-11*t)) for i in range(3)))
    
    floor_colors = {4:(50,42,32),3:(56,48,38),2:(63,56,46),1:(70,62,52),0:(76,68,58)}
    fc = floor_colors.get(fin_r,(63,56,46))
    for y in range(floor_y, H):
        t = (y-floor_y)/(H-floor_y)
        draw.line([(0,y),(W,y)], fill=tuple(max(0,int(fc[i]-16*t)) for i in range(3)))

    # Windows
    n_win = max(1, fin_r+1)
    win_w = 85+fin_r*22
    win_h = 82+fin_r*18
    win_y = int(H*.33)
    spacing = W//(n_win+1)
    for wi in range(n_win):
        wx = spacing*(wi+1) - win_w//2
        fr = (170,150,115) if fin_r>=3 else (98,90,78) if fin_r>=2 else (64,58,50)
        draw.rectangle([wx-4,win_y-4,wx+win_w+4,win_y+win_h+4], fill=fr)
        for wy2 in range(win_h):
            t = wy2/win_h
            sc = tuple(int(c1[i]*(1-t)+max(0,c1[i]-14)*t) for i in range(3))
            draw.line([(wx,win_y+wy2),(wx+win_w,win_y+wy2)], fill=sc)

    # Desk
    dx = int(W*.06)
    dy = floor_y-15
    dw = int(W*.88)
    dd = 18
    desk_c = {4:(66,48,26),3:(56,42,25),2:(72,62,44),1:(78,68,52),0:(86,76,60)}.get(fin_r,(72,62,44))
    draw.rectangle([dx,dy,dx+dw,dy+dd], fill=desk_c)

    # Monitors
    mon_n = 1 if car_r<=1 else 2 if car_r<=3 else 3
    if mon_n==1:   mon_xs=[dx+dw//2-70]
    elif mon_n==2: mon_xs=[dx+50, dx+dw//2+22]
    else:          mon_xs=[dx+16, dx+dw//2-68, dx+dw-192]
    mw=128+car_r*13
    mh=86+car_r*10
    my=int(H*.23)-mh
    for mpx in mon_xs:
        bez = (10,10,16) if car_r>=3 else (20,18,14)
        draw.rectangle([mpx-6,my-6,mpx+mw+6,my+mh+6], fill=bez)
        draw.rectangle([mpx,my,mpx+mw,my+mh], fill=(4,8,22) if car_r>=3 else (9,13,26))
        acc = (125,170,250) if fin_r>=2 else (90,120,190)
        # Screen content based on field
        is_tech = any(x in field for x in ["Tech","Eng","Sci"])
        if is_tech:
            for li in range(7):
                lw = rng.randint(int(mw*.2),int(mw*.8))
                draw.line([(mpx+5,my+8+li*11),(mpx+5+lw,my+8+li*11)],
                          fill=acc if rng.random()>.35 else (72,95,125), width=1)

    # Keyboard
    kbx = mon_xs[0]+(mw-105)//2
    kby = dy-20
    kbc = (26,24,20) if fin_r>=3 else (46,42,36)
    draw.rectangle([kbx,kby,kbx+105,kby+14], fill=kbc, outline=(72,70,62), width=1)
    for kr in range(2):
        for kc2 in range(11):
            draw.rectangle([kbx+3+kc2*9,kby+3+kr*5,kbx+9+kc2*9,kby+6+kr*5],
                          fill=tuple(min(255,c+20) for c in kbc))

    # Info overlay (minimal, no text on image area)
    arr = np.array(canvas)
    bar_h = 85
    arr[H-bar_h:] = np.clip(arr[H-bar_h:]*0.2 + np.array([4,4,12])*0.8, 0, 255).astype(np.uint8)
    canvas = Image.fromarray(arr)

    # Add film grain for realism
    noise_arr = np.array(canvas).astype(np.float32)
    canvas = Image.fromarray(np.clip(noise_arr + np.random.normal(0, 4, noise_arr.shape), 0, 255).astype(np.uint8))
    
    return canvas

# ══════════════════════════════════════════════════════════════════════════════
#  SAVE OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
def save_output(image: Image.Image, u: dict, s: dict, sim: dict,
                flux_prompt: str, analysis: str):
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name  = (u.get("name") or "user").replace(" ","_").lower()[:20]
    img_p = OUTPUT_DIR / f"{name}_{ts}.png"
    image.save(img_p)
    meta  = {
        "timestamp": ts, "name": u.get("name",""), "age": u["age"],
        "country": u.get("country","India"),
        "scores":  {k:s[k] for k in ("academic","financial","career","lifestyle","composite","risk","trend")},
        "10yr": {"age":sim["10_year"]["age"],"composite":sim["10_year"]["composite"],
                 "income_lpa":sim["10_year"]["income_lpa"],
                 "career_status":sim["10_year"]["career_status"],
                 "fin_status":sim["10_year"]["fin_status"]},
        "flux_prompt": flux_prompt,
        "analysis_excerpt": analysis[:400],
    }
    with open(OUTPUT_DIR / f"{name}_{ts}_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    return str(img_p)

# ══════════════════════════════════════════════════════════════════════════════
#  CHARTS (same as v4.0)
# ══════════════════════════════════════════════════════════════════════════════
_PT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(family="DM Sans", color="#9aa0bc", size=12),
           margin=dict(l=10, r=10, t=40, b=10))

def _sc(v):
    return "#34d399" if v>=75 else "#e8b84b" if v>=55 else "#fb923c" if v>=40 else "#fb7185"

def bar_chart(s):
    cats=["Academic","Financial","Career","Lifestyle"]
    vals=[s[c.lower()] for c in cats]
    fig=go.Figure(go.Bar(x=cats,y=vals,marker_color=[_sc(v) for v in vals],
        text=[f"{v:.0f}" for v in vals],textposition="outside",marker_line_width=0))
    fig.update_layout(yaxis=dict(range=[0,112],gridcolor="rgba(255,255,255,.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,.05)"),
        title=dict(text="Current Domain Scores",font=dict(size=13,color="#e8b84b")),**_PT)
    return fig

def radar_chart(s):
    cats=["Academic","Financial","Career","Lifestyle"]
    vals=[s[c.lower()] for c in cats]
    fig=go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill="toself",
        line=dict(color="#e8b84b",width=2),fillcolor="rgba(232,184,75,.12)"))
    fig.update_layout(polar=dict(
        radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(255,255,255,.06)",linecolor="rgba(255,255,255,.06)"),
        angularaxis=dict(gridcolor="rgba(255,255,255,.06)"),bgcolor="rgba(0,0,0,0)"),
        showlegend=False,title=dict(text="Profile Radar",font=dict(size=13,color="#e8b84b")),**_PT)
    return fig

def trajectory_chart(s, sim):
    periods=["Now","5 Years","10 Years","25 Years"]
    comps=[s["composite"],sim["5_year"]["composite"],sim["10_year"]["composite"],sim["25_year"]["composite"]]
    incomes=[None,sim["5_year"]["income_lpa"],sim["10_year"]["income_lpa"],sim["25_year"]["income_lpa"]]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=periods,y=comps,mode="lines+markers+text",name="Score",
        line=dict(color="#e8b84b",width=3),marker=dict(size=9,color="#e8b84b"),
        text=[f"{c:.0f}" for c in comps],textposition="top center"))
    fig.add_trace(go.Scatter(x=periods[1:],y=incomes[1:],mode="lines+markers+text",
        name="Income (LPA)",line=dict(color="#22d3ee",width=2,dash="dot"),
        marker=dict(size=8,color="#22d3ee"),
        text=[f"₹{i}" for i in incomes[1:]],textposition="bottom center",yaxis="y2"))
    fig.add_hline(y=75,line_dash="dash",line_color="rgba(52,211,153,.3)",annotation_text="Low Risk")
    fig.add_hline(y=50,line_dash="dash",line_color="rgba(251,146,60,.3)",annotation_text="Moderate Risk")
    fig.update_layout(
        yaxis=dict(range=[0,112],title="Score",gridcolor="rgba(255,255,255,.05)"),
        yaxis2=dict(title="Income LPA",overlaying="y",side="right",showgrid=False),
        legend=dict(orientation="h",y=1.1),
        title=dict(text="Score & Income Trajectory",font=dict(size=13,color="#e8b84b")),**_PT)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  ACTION HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _act_academic(s,u):
    if s["academic"]>=75: return f"Strong profile. Target competitive exams or research publications to stand out at {u['college_tier']} level."
    elif s["academic"]>=50: return f"CGPA {u['cgpa']} is recoverable — 35+ study hrs/week + spaced repetition. Target +0.5 CGPA per semester."
    else: return f"Critical: {u['cgpa']} CGPA limits early opportunities. Build a strong project portfolio to compensate now."

def _act_financial(s,u):
    if s["financial"]>=75: return "Excellent habits. Invest 20% of income in index funds. Resist lifestyle inflation as earnings grow."
    elif s["financial"]>=50: return f"Start ₹{max(500,u['monthly_spend']//20)}/month SIP today. Track spending 30 days — find your biggest leak."
    else: return "Immediate: freeze discretionary spending 2 weeks. Map income vs. expenses honestly. Emergency fund first."

def _act_career(s,u):
    t=u.get("target_career","your target role") or "your target role"
    if s["career"]>=75: return f"On track for {t}. Build your brand on LinkedIn/GitHub so opportunities come to you."
    elif s["career"]>=50: return f"Gap vs {t}: one intensive 12-week course + one real project this quarter closes it."
    else: return f"Skill deficit is primary blocker. 2 hrs/day for 90 days on {t}-specific skills. Find a mentor."

def _act_lifestyle(s,u):
    if s["lifestyle"]>=75: return "Healthy habits are your cognitive multiplier. Protect sleep above everything else."
    elif s["lifestyle"]>=50: return "Fix sleep first: same time every night, 7.5 hrs. Focus and discipline follow automatically."
    else: return "Poor health + poor sleep + high screen time silently destroys capacity. 10-min walk + phone off at 10 PM — start today."

# ══════════════════════════════════════════════════════════════════════════════
#  COUNTRIES
# ══════════════════════════════════════════════════════════════════════════════
COUNTRIES = [
    "India","United States","United Kingdom","Canada","Australia",
    "Germany","France","Singapore","UAE","Netherlands","Sweden",
    "Japan","South Korea","New Zealand","Ireland","Switzerland",
    "Malaysia","Bangladesh","Sri Lanka","Nepal","Pakistan",
    "South Africa","Nigeria","Kenya","Brazil","Mexico",
    "Italy","Spain","Portugal","Poland","Other",
]

# ══════════════════════════════════════════════════════════════════════════════
#  UI — HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">⬡ AI-Powered Life Trajectory · FLUX + Groq</div>
  <div class="hero-title">Future <em>Life</em><br>Simulator</div>
  <div class="hero-sub">
    Enter your details. The scoring engine projects your life trajectory —
    then FLUX.1-schnell generates <strong>one definitive photorealistic image</strong>
    of your predicted future: your home, your workspace, your environment,
    shaped exactly by your scores.
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-logo">⬡ FLS · v5.0</div>', unsafe_allow_html=True)

    # ── Personal Details ─────────────────────────────────────────────────
    st.markdown('<div class="sb-sec">👤 Personal Details</div>', unsafe_allow_html=True)
    name        = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
    occupation  = st.text_input("Current Role / Status", placeholder="e.g. 2nd Year B.Tech Student")
    bio         = st.text_area("One-line bio (optional)", placeholder="e.g. Aspiring ML engineer from Chennai…", height=68)

    st.markdown('<div class="sb-sec">🌍 Country</div>', unsafe_allow_html=True)
    country = st.selectbox("Country / Region", COUNTRIES, index=0)

    st.markdown('<div class="sb-sec">📋 Basic Info</div>', unsafe_allow_html=True)
    age    = st.slider("Current Age", 15, 35, 20)
    gender = st.selectbox("Gender", ["Prefer not to say","Male","Female","Non-binary"])

    st.markdown('<div class="sb-sec">🎓 Academic</div>', unsafe_allow_html=True)
    edu_level    = st.selectbox("Education Level", ["High School","Undergraduate","Postgraduate","PhD"])
    cgpa         = st.number_input("CGPA / GPA", 0.0, 10.0, 7.5, 0.1, help="4.0 or 10.0 scale — auto-detected")
    field        = st.selectbox("Field of Study", ["Engineering / Technology","Science","Commerce / Business","Arts / Humanities","Medicine / Healthcare","Law","Other"])
    college_tier = st.selectbox("Institution Tier", ["Tier 1","Tier 2","Tier 3"], help="Tier 1 = top national/global")
    study_hours  = st.slider("Study Hours / Week", 0, 80, 20)

    st.markdown('<div class="sb-sec">💼 Career</div>', unsafe_allow_html=True)
    target_career = st.text_input("Target Career", placeholder="e.g. Software Engineer, Doctor")
    skill         = st.selectbox("Current Skill Level", ["Beginner","Intermediate","Advanced"])
    experience    = st.checkbox("Has Internship / Work Experience")
    consistency   = st.selectbox("Work & Study Consistency", ["Low","Medium","High"])

    st.markdown('<div class="sb-sec">💰 Financial</div>', unsafe_allow_html=True)
    monthly_spend = st.number_input("Monthly Spending (₹)", 0, 100_000, 8_000, 500)
    savings       = st.selectbox("Savings Habit", ["Low","Medium","High"])
    family_bg     = st.selectbox("Family Income Background", ["Low","Middle","High"])
    discipline    = st.selectbox("Financial Discipline", ["Impulsive","Balanced","Disciplined"])

    st.markdown('<div class="sb-sec">🌱 Lifestyle</div>', unsafe_allow_html=True)
    screen_time = st.selectbox("Daily Screen Time", ["Low (<4 h)","Medium (4–8 h)","High (>8 h)"])
    health      = st.selectbox("Health Habits", ["Poor","Average","Good"])
    sleep       = st.selectbox("Sleep Quality", ["Poor","Average","Good"])

    # Live preview in sidebar
    if name:
        st.markdown(f"""<div class="sb-user-preview">
          <div class="sb-user-name">{name}</div>
          <div class="sb-user-detail">{occupation or edu_level} · {country} · Age {age}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    run_btn = st.button("🚀 Generate My Future Life", use_container_width=True)

# Collect user dict
user = dict(
    name=name.strip() if name else "",
    occupation=occupation.strip() if occupation else "",
    bio=bio.strip() if bio else "",
    country=country, age=age, gender=gender,
    edu_level=edu_level, cgpa=cgpa, field=field,
    college_tier=college_tier, study_hours=study_hours,
    target_career=target_career or "Not specified",
    skill=skill, experience=experience, consistency=consistency,
    monthly_spend=monthly_spend, savings=savings,
    family_bg=family_bg, discipline=discipline,
    screen_time=screen_time, health=health, sleep=sleep,
)

# ══════════════════════════════════════════════════════════════════════════════
#  WELCOME STATE
# ══════════════════════════════════════════════════════════════════════════════
if not run_btn and not st.session_state.analysis_done:
    st.markdown("""
    <div class="welcome">
      <div style="font-size:4.5rem;margin-bottom:1.2rem;">🔮</div>
      <div class="welcome-title">Your Future, Visualised</div>
      <div class="welcome-body">
        Enter your name, fill in your profile — and press <strong>Generate My Future Life</strong>.<br/><br/>
        The engine scores your trajectory, Groq writes your story,
        and <strong>FLUX</strong> generates a single photorealistic image
        of <em>exactly</em> what your life environment will look like — 
        your home, your desk, your city — 10 years from now.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col,icon,ttl,body in [
        (c1,"🪪","Personalised","Enter your name, bio, occupation. The analysis speaks to you by name — not a generic report."),
        (c2,"🎨","One Definitive Image","One single hyper-realistic FLUX image of your predicted future environment."),
        (c3,"📖","Deep Narrative","Groq Llama 3.3 writes a brutally honest, country-specific, personally addressed life trajectory analysis."),
    ]:
        with col:
            st.markdown(f'<div class="card"><div style="font-size:2rem;margin-bottom:.5rem;">{icon}</div>'
                        f'<div style="font-family:JetBrains Mono,monospace;font-size:.63rem;letter-spacing:.14em;'
                        f'color:rgba(232,184,75,.6);text-transform:uppercase;margin-bottom:.4rem;">{ttl}</div>'
                        f'<div style="font-size:.85rem;color:rgba(226,230,243,.55);line-height:1.72;">{body}</div></div>',
                        unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    with st.status("⚙ Running your personal simulation…", expanded=True) as status:

        st.write("📐 Computing behavioural scores…")
        s   = compute_scores(user)
        sim = simulate(user, s)
        st.session_state.scores     = s
        st.session_state.simulation = sim

        st.write("🤖 Groq writing your personalised analysis…")
        analysis = run_analysis(user, s, sim)
        st.session_state.llm_analysis = analysis

        st.write("📖 Crafting your life narrative…")
        narrative = run_life_narrative(user, s, sim)
        st.session_state.life_narrative = narrative

        st.write("✍️ Building FLUX prompt from your scores…")
        flux_prompt = build_flux_prompt(user, s, sim)
        st.session_state.flux_prompt = flux_prompt

        st.write("🎨 Generating hyper-realistic future life image with FLUX.1-schnell…")
        final_image = generate_flux_image(flux_prompt)
        if final_image is None:
            st.write("  ↳ FLUX unavailable — rendering detailed hyper-realistic scene…")
            final_image = make_fallback_image(user, s, sim)
        else:
            final_image = final_image.resize((1024, 768), Image.LANCZOS)

        st.session_state.final_image = final_image

        st.write("💾 Saving to models/FSVE/…")
        save_output(final_image, user, s, sim, flux_prompt, analysis)

        st.session_state.analysis_done = True
        status.update(label=f"✅ {user.get('name','Your')} future is ready!", state="complete", expanded=False)

# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS (same as previous but with no face upload references)
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.analysis_done:
    st.stop()

s   = st.session_state.scores
sim = st.session_state.simulation

# ── PERSON BANNER ──────────────────────────────────────────────────────────────
disp_name = user.get("name") or "Your Future Self"
disp_occ  = user.get("occupation") or user["edu_level"]
disp_bio  = user.get("bio", "")

st.markdown(f"""
<div class="card-person">
  <div style="display: flex; gap: 1.5rem; align-items: flex-start; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 200px;">
      <div class="person-name">{disp_name}</div>
      <div class="person-meta">{disp_occ} · {user.get('country','India')} · Age {user['age']}</div>
      {f'<div style="font-size: .84rem; color: rgba(228,232,245,.5); margin-top: .4rem; line-height: 1.6;">{disp_bio}</div>' if disp_bio else ""}
      <div style="margin-top: .6rem;">
        <span class="person-tag">{user['field']}</span>
        <span class="person-tag">{user['college_tier']}</span>
        <span class="person-tag">{user['skill']} Level</span>
        <span class="person-tag">{"Has Experience" if user['experience'] else "No Experience"}</span>
        <span class="person-tag">{s['risk']} Risk</span>
        <span class="person-tag">{s['trend']}</span>
      </div>
    </div>
    <div style="text-align: right; flex-shrink: 0;">
      <div style="font-family: 'JetBrains Mono', monospace; font-size: .56rem; letter-spacing: .2em; text-transform: uppercase; color: rgba(232,184,75,.45); margin-bottom: .3rem;">10-Year Income</div>
      <div style="font-family: 'Cormorant Garamond', serif; font-size: 2.2rem; font-weight: 700; color: {_sc(sim['10_year']['composite'])};">₹{sim['10_year']['income_lpa']} LPA</div>
      <div style="font-family: 'JetBrains Mono', monospace; font-size: .62rem; color: rgba(228,232,245,.4);">{sim['10_year']['career_status']} · {sim['10_year']['fin_status']}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🖼️  Future Image",
    "📊  Dashboard",
    "🤖  AI Analysis",
    "💡  Action Plan",
])

# ─── TAB 1: THE IMAGE ─────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🖼️ Your Hyper-Realistic Future Life")

    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        st.markdown('<div class="a-warn">⚠️ <b>HF_TOKEN not set</b> — using high-quality hyper-realistic renderer. Add <code>HF_TOKEN=hf_...</code> to .env for FLUX images.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="a-ok">✅ <b>FLUX.1-schnell active</b> — hyper-realistic image generated from your actual computed scores.</div>', unsafe_allow_html=True)

    img_col, info_col = st.columns([3, 2])

    with img_col:
        img = st.session_state.final_image
        if img:
            st.markdown('<div class="img-showcase">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            name_slug = (user.get("name","user") or "user").replace(" ","_").lower()
            st.download_button(
                f"⬇ Download — {disp_name}'s Future",
                buf.getvalue(),
                file_name=f"{name_slug}_future.png",
                mime="image/png",
            )

    with info_col:
        d = sim["10_year"]
        st.markdown(f"""<div class="card-gold">
          <div style="font-family:'JetBrains Mono',monospace;font-size:.56rem;letter-spacing:.2em;
               text-transform:uppercase;color:rgba(232,184,75,.42);">10-Year Projection · Age {d['age']}</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:700;
               color:{_sc(d['composite'])};margin:.3rem 0;">₹{d['income_lpa']} LPA</div>
          <div style="display:flex;gap:.45rem;flex-wrap:wrap;margin-top:.6rem;">
            {"".join([
              f'<span style="background:rgba(232,184,75,.07);border:1px solid rgba(232,184,75,.2);'
              f'border-radius:6px;padding:.18rem .5rem;font-size:.68rem;'
              f'font-family:JetBrains Mono,monospace;">{t}</span>'
              for t in [d["career_status"], d["fin_status"], d["life_quality"]]
            ])}
          </div>
        </div>""", unsafe_allow_html=True)

        # Domain scores at 10yr
        st.markdown(f"""<div class="card" style="font-size:.82rem;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:.54rem;letter-spacing:.18em;
               text-transform:uppercase;color:rgba(232,184,75,.36);margin-bottom:.6rem;">Scores @ 10 Years</div>
          {"".join([
            f'<div class="score-row">'
            f'<span style="color:rgba(228,232,245,.5);font-size:.82rem;min-width:70px;">{k}</span>'
            f'<div class="score-bar-bg"><div style="width:{d[k.lower()]:.0f}%;height:4px;'
            f'background:{_sc(d[k.lower()])};border-radius:2px;"></div></div>'
            f'<span style="color:{_sc(d[k.lower()])};font-family:JetBrains Mono,monospace;'
            f'font-size:.7rem;font-weight:600;">{d[k.lower()]:.0f}</span></div>'
            for k in ["Academic","Financial","Career","Lifestyle"]
          ])}
        </div>""", unsafe_allow_html=True)

        # Life narrative
        narr = st.session_state.life_narrative
        if narr:
            st.markdown(f'<div class="narrative" style="font-size:.86rem;">{narr}</div>', unsafe_allow_html=True)

        # FLUX prompt
        prmp = st.session_state.flux_prompt
        if prmp:
            with st.expander("🎨 FLUX Prompt Used"):
                st.code(prmp, language=None)

    # ── Timeline row (5/10/25yr) ───────────────────────────────────────────
    st.markdown("<br/>**Projected Milestones**", unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    for col, key, lbl in zip([tc1,tc2,tc3],
                              ["5_year","10_year","25_year"],
                              ["5 Years","10 Years","25 Years"]):
        d2 = sim[key]; cl = _sc(d2["composite"])
        with col:
            st.markdown(f"""<div class="tl-card">
              <div class="tl-year">{lbl.upper()} · AGE {d2['age']}</div>
              <div class="tl-income" style="color:{cl};">₹{d2['income_lpa']} LPA</div>
              <div class="tl-stat">Score {d2['composite']}/100</div>
              <div style="margin-top:.6rem;display:flex;flex-direction:column;gap:.2rem;">
                <div class="tl-stat">💼 {d2['career_status']}</div>
                <div class="tl-stat">💰 {d2['fin_status']}</div>
                <div class="tl-stat">🌱 {d2['life_quality']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

# ─── TAB 2: DASHBOARD ─────────────────────────────────────────────────────────
with tab2:
    st.markdown(f"### 📊 Behavioural Dashboard — {disp_name}")

    k1,k2,k3,k4 = st.columns(4)
    rb = {"Low":"#34d399","Moderate":"#fbbf24","High":"#fb7185"}[s["risk"]]
    ti = {"Improving":"📈","Stable":"➡️","Declining":"📉"}[s["trend"]]
    tc = {"Improving":"#34d399","Stable":"#e8b84b","Declining":"#fb7185"}[s["trend"]]
    with k1:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Composite Score</div>'
                    f'<div class="kpi-value" style="color:{_sc(s["composite"])};">{s["composite"]:.0f}</div>'
                    f'<div class="kpi-sub">out of 100</div></div>', unsafe_allow_html=True)
    with k2:
        bc = {"Low":"b-low","Moderate":"b-mod","High":"b-high"}[s["risk"]]
        st.markdown(f'<div class="kpi"><div class="kpi-label">Risk Level</div>'
                    f'<div style="margin-top:.5rem;"><span class="{bc}">{s["risk"]}</span></div>'
                    f'<div class="kpi-sub" style="margin-top:.4rem;">{s["profile"]}</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Growth Trend</div>'
                    f'<div class="kpi-value" style="color:{tc};font-size:1.5rem;">{ti} {s["trend"]}</div></div>',
                    unsafe_allow_html=True)
    with k4:
        est = sim["25_year"]["income_lpa"]
        st.markdown(f'<div class="kpi"><div class="kpi-label">25-yr Est. Income</div>'
                    f'<div class="kpi-value" style="color:#22d3ee;">₹{est}</div>'
                    f'<div class="kpi-sub">LPA</div></div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca: st.plotly_chart(bar_chart(s), use_container_width=True)
    with cb: st.plotly_chart(radar_chart(s), use_container_width=True)
    st.plotly_chart(trajectory_chart(s, sim), use_container_width=True)

# ─── TAB 3: AI ANALYSIS ───────────────────────────────────────────────────────
with tab3:
    st.markdown(f"### 🤖 Groq Analysis — Addressed to {disp_name}")
    st.markdown(f'<div style="color:rgba(228,232,245,.4);font-size:.8rem;margin-bottom:1rem;">'
                f'Groq Llama 3.3 · {user.get("country","India")} context · Personalised for {disp_name}'
                f'</div>', unsafe_allow_html=True)

    analysis = st.session_state.llm_analysis
    if analysis and not analysis.startswith("["):
        st.markdown('<div class="narrative">', unsafe_allow_html=True)
        st.markdown(analysis)
        st.markdown('</div>', unsafe_allow_html=True)

        report = f"""FUTURE LIFE SIMULATION REPORT
===================================
Name:    {disp_name}
Role:    {disp_occ}
Country: {user.get('country','India')}
Age:     {user['age']}
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SCORES
Academic: {s['academic']}  Financial: {s['financial']}  Career: {s['career']}  Lifestyle: {s['lifestyle']}
Composite: {s['composite']}  Risk: {s['risk']}  Trend: {s['trend']}

10-YEAR PROJECTION
Income: ₹{sim['10_year']['income_lpa']} LPA  Career: {sim['10_year']['career_status']}  Finance: {sim['10_year']['fin_status']}

FULL ANALYSIS
{analysis}

---
Future Life Simulator v5.0
"""
        st.download_button("📄 Download Full Report", report,
            file_name=f"{(user.get('name','user') or 'user').lower().replace(' ','_')}_fls_report.txt",
            mime="text/plain")
    else:
        if analysis and analysis.startswith("["): st.warning(analysis)
        st.info("Add GROQ_API_KEY to .env to enable personalised AI analysis.")

# ─── TAB 4: ACTION PLAN ───────────────────────────────────────────────────────
with tab4:
    st.markdown(f"### 💡 Action Plan — {disp_name}'s Priority Moves")

    risk = s["risk"]
    if   risk=="High":     st.markdown('<div class="a-err">⚠️ <b>High Risk</b> — Immediate corrective action needed. The gaps are real but fixable.</div>', unsafe_allow_html=True)
    elif risk=="Moderate": st.markdown('<div class="a-warn">⚡ <b>Moderate Risk</b> — You have solid foundations. The improvements below are high-leverage.</div>', unsafe_allow_html=True)
    else:                  st.markdown('<div class="a-ok">✅ <b>Low Risk</b> — Excellent trajectory. Focus on compounding your strengths.</div>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    for icon, domain, score, action in [
        ("📚", "Academic",  s["academic"],  _act_academic(s, user)),
        ("💰", "Financial", s["financial"], _act_financial(s, user)),
        ("💼", "Career",    s["career"],    _act_career(s, user)),
        ("🌱", "Lifestyle", s["lifestyle"], _act_lifestyle(s, user)),
    ]:
        color  = _sc(score)
        impact = "HIGH IMPACT" if score < 55 else "MEDIUM"
        st.markdown(f"""<div style="display:flex;gap:1rem;align-items:flex-start;
             background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.055);
             border-radius:12px;padding:.95rem 1.2rem;margin:.5rem 0;">
          <div style="font-size:1.2rem;flex-shrink:0;padding-top:.1rem;">{icon}</div>
          <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.3rem;">
              <span style="font-family:JetBrains Mono,monospace;font-size:.6rem;letter-spacing:.16em;
                   text-transform:uppercase;color:#e8b84b;">{domain}</span>
              <div style="flex:1;height:3px;background:rgba(255,255,255,.05);border-radius:2px;">
                <div style="width:{int(score)}%;height:3px;background:{color};border-radius:2px;"></div>
              </div>
              <span style="font-family:JetBrains Mono,monospace;font-size:.66rem;
                   color:{color};font-weight:600;">{score:.0f}/100</span>
            </div>
            <div style="font-size:.87rem;line-height:1.65;color:rgba(228,232,245,.78);">{action}</div>
          </div>
          <div style="font-family:JetBrains Mono,monospace;font-size:.58rem;
               color:{color};flex-shrink:0;letter-spacing:.1em;text-transform:uppercase;">{impact}</div>
        </div>""", unsafe_allow_html=True)

    analysis = st.session_state.llm_analysis
    if analysis and not analysis.startswith("["):
        with st.expander("📋 Full Groq Priority Actions"):
            idx = analysis.lower().find("priority actions")
            st.markdown(analysis[idx:] if idx >= 0 else analysis)

    st.markdown("---")
    st.markdown(f"""<div class="card" style="font-size:.87rem;color:rgba(228,232,245,.52);line-height:1.88;">
      <strong style="color:#e8b84b;">{disp_name}, remember the Compound Effect</strong> —
      Every projection shown is your current trajectory, extended.
      A 1% daily improvement in your weakest domain compounds to 37× over one year.
      The people who succeed are not the most talented — they are the most deliberate.
      <br/><br/>
      <span style="font-family:'JetBrains Mono',monospace;font-size:.64rem;color:rgba(232,184,75,.38);">
      COMPOSITE {s["composite"]:.0f}/100 · {s["risk"].upper()} RISK · {s["trend"].upper()} · 
      {user.get('country','India').upper()} · {user['field'].upper()}
      </span>
    </div>""", unsafe_allow_html=True)