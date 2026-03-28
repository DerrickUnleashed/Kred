"""
Future Life Simulator — FLUX-powered Lifestyle Image Generation
================================================================
Uses HuggingFace FLUX.1-schnell to generate photorealistic lifestyle
environment images based on computed scores. Country-aware prompting.

Run:  streamlit run app.py
Env:  GEMINI_API_KEY  (mandatory — Gemini 2.0 Flash analysis)
      HF_TOKEN        (mandatory — FLUX.1-schnell image generation)
"""

import os, io, json, datetime, random
from pathlib import Path

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()

from google import genai
from google.genai import types

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
#  STYLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg:#06070e; --bg2:#0a0c18; --bg3:#0e1022;
  --border:rgba(255,255,255,.06); --border2:rgba(232,184,75,.18);
  --gold:#e8b84b; --gold2:#f5d080; --cyan:#22d3ee;
  --red:#fb7185; --green:#34d399; --amber:#fb923c;
  --text:#e2e6f3; --text2:rgba(226,230,243,.5); --text3:rgba(226,230,243,.28);
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background:var(--bg);color:var(--text);}

.hero{background:linear-gradient(135deg,#070910 0%,#0d0a1e 45%,#060e14 100%);
  border:1px solid var(--border2);border-radius:20px;padding:2.8rem 2.6rem 2.4rem;
  margin-bottom:2rem;position:relative;overflow:hidden;}
.hero::before{content:'';position:absolute;top:-100px;right:-80px;width:360px;height:360px;
  background:radial-gradient(circle,rgba(232,184,75,.12) 0%,transparent 65%);border-radius:50%;}
.hero::after{content:'';position:absolute;bottom:-60px;left:-40px;width:200px;height:200px;
  background:radial-gradient(circle,rgba(34,211,238,.08) 0%,transparent 65%);border-radius:50%;}
.hero-eye{font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.3em;
  text-transform:uppercase;color:var(--gold);margin-bottom:.6rem;position:relative;z-index:1;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:4rem;letter-spacing:.04em;
  line-height:.95;color:#f0ead8;position:relative;z-index:1;}
.hero-title span{color:var(--gold);}
.hero-sub{font-size:.88rem;color:var(--text2);font-weight:300;margin-top:.8rem;
  position:relative;z-index:1;letter-spacing:.04em;max-width:600px;}

section[data-testid="stSidebar"]{background:#050609 !important;border-right:1px solid rgba(232,184,75,.1);}
.sb-logo{font-family:'Bebas Neue',monospace;font-size:1.3rem;letter-spacing:.18em;color:var(--gold);
  border-bottom:1px solid rgba(232,184,75,.12);padding-bottom:.7rem;margin-bottom:1rem;}
.sb-sec{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.24em;
  text-transform:uppercase;color:var(--text3);margin:1.1rem 0 .35rem;}

.stSelectbox>div>div,.stNumberInput>div,.stTextInput>div>div{
  background:rgba(255,255,255,.025) !important;border-color:rgba(232,184,75,.15) !important;
  border-radius:8px !important;color:var(--text) !important;}
.stButton>button{background:linear-gradient(135deg,#9a6e1a,#e8b84b) !important;
  color:#06070e !important;border:none !important;border-radius:10px !important;
  font-family:'JetBrains Mono',monospace !important;font-weight:600 !important;
  letter-spacing:.08em !important;padding:.68rem 1.5rem !important;
  transition:all .2s !important;font-size:.8rem !important;text-transform:uppercase !important;}
.stButton>button:hover{transform:translateY(-2px) !important;box-shadow:0 8px 32px rgba(232,184,75,.35) !important;}
.stProgress>div>div{background:linear-gradient(90deg,var(--gold),var(--cyan)) !important;}
.stTabs [data-baseweb="tab-list"]{background:transparent !important;border-bottom:1px solid rgba(232,184,75,.12);gap:.3rem;}
.stTabs [data-baseweb="tab"]{font-family:'JetBrains Mono',monospace !important;font-size:.68rem !important;
  letter-spacing:.12em !important;color:var(--text3) !important;text-transform:uppercase !important;
  border:none !important;background:transparent !important;padding:.55rem .9rem !important;}
.stTabs [aria-selected="true"]{color:var(--gold) !important;border-bottom:2px solid var(--gold) !important;}

.card{background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:14px;padding:1.3rem 1.5rem;margin-bottom:1rem;}
.card-gold{background:rgba(232,184,75,.04);border:1px solid var(--border2);border-radius:14px;padding:1.3rem 1.5rem;margin-bottom:1rem;}

.kpi{background:rgba(4,5,12,.85);border:1px solid rgba(232,184,75,.15);border-radius:14px;padding:1.2rem;text-align:center;}
.kpi-label{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.22em;text-transform:uppercase;color:var(--text3);margin-bottom:.5rem;}
.kpi-value{font-family:'DM Serif Display',serif;font-size:2.3rem;line-height:1;}
.kpi-sub{font-size:.74rem;color:var(--text3);margin-top:.3rem;}

.b-low{background:#071d12;border:1px solid #34d399;color:#34d399;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:600;display:inline-block;}
.b-mod{background:#1c1208;border:1px solid #fbbf24;color:#fbbf24;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:600;display:inline-block;}
.b-high{background:#1a0808;border:1px solid #fb7185;color:#fb7185;padding:.22rem .8rem;border-radius:999px;font-family:'JetBrains Mono',monospace;font-size:.68rem;font-weight:600;display:inline-block;}

.narrative{background:rgba(232,184,75,.05);border-left:3px solid var(--gold);border-radius:0 12px 12px 0;
  padding:1.1rem 1.4rem;font-size:.9rem;line-height:1.9;color:rgba(230,225,210,.88);margin:.8rem 0;}
.a-ok{background:#071d12;border-left:3px solid #34d399;border-radius:0 8px 8px 0;padding:.8rem 1rem;font-size:.86rem;margin:.5rem 0;}
.a-warn{background:#1c1208;border-left:3px solid #fbbf24;border-radius:0 8px 8px 0;padding:.8rem 1rem;font-size:.86rem;margin:.5rem 0;}
.a-err{background:#1a0808;border-left:3px solid #fb7185;border-radius:0 8px 8px 0;padding:.8rem 1rem;font-size:.86rem;margin:.5rem 0;}

.tl-card{background:linear-gradient(145deg,rgba(10,12,26,.95),rgba(5,7,16,.95));border:1px solid rgba(232,184,75,.18);border-radius:14px;padding:1.2rem;}
.tl-year{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.24em;color:rgba(232,184,75,.6);margin-bottom:.4rem;}
.tl-income{font-family:'DM Serif Display',serif;font-size:1.75rem;color:var(--gold);}
.tl-stat{font-family:'JetBrains Mono',monospace;font-size:.66rem;color:var(--text3);margin-top:.2rem;}

.welcome{border:1px solid rgba(232,184,75,.12);border-radius:20px;padding:4.5rem 2.5rem;text-align:center;
  background:linear-gradient(145deg,rgba(8,9,18,.85),rgba(4,5,12,.95));margin-top:1rem;}
.welcome-title{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:.06em;color:#f0ead8;margin-bottom:.7rem;}
.welcome-body{color:var(--text2);max-width:520px;margin:0 auto 1.5rem;line-height:1.85;font-size:.91rem;}
.img-frame{border:1px solid var(--border2);border-radius:16px;overflow:hidden;box-shadow:0 16px 60px rgba(0,0,0,.7);}
hr{border-color:var(--border) !important;}
.stDownloadButton>button{background:rgba(232,184,75,.08) !important;color:var(--gold) !important;
  border:1px solid rgba(232,184,75,.22) !important;border-radius:7px !important;
  font-family:'JetBrains Mono',monospace !important;font-size:.68rem !important;
  padding:.35rem .8rem !important;text-transform:uppercase !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DIRS + SESSION
# ══════════════════════════════════════════════════════════════════════════════
OUTPUT_DIR = Path("models/FSVE")
for _f in ["5_year", "10_year", "25_year"]:
    (OUTPUT_DIR / _f).mkdir(parents=True, exist_ok=True)

for k, v in dict(
    scores={}, simulation={}, llm_analysis="",
    future_scenarios={}, flux_prompts={}, images={},
    analysis_done=False,
).items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_gemini():
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None
    try:
        return genai.Client(api_key=key)
    except Exception:
        return None

def gemini_call(prompt: str, temperature: float = 0.72, max_tokens: int = 2048) -> str:
    client = get_gemini()
    if not client:
        return "[Gemini API key not configured — add GEMINI_API_KEY to .env]"
    try:
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        cfg = types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_tokens)
        resp = client.models.generate_content(
            model="gemini-2.0-flash-exp", contents=contents, config=cfg
        )
        text = "".join(
            part.text for part in resp.candidates[0].content.parts
            if hasattr(part, "text") and part.text
        )
        return text.strip() or "[Empty response]"
    except Exception as e:
        return f"[Gemini error: {e}]"

# ══════════════════════════════════════════════════════════════════════════════
#  SCORING ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def score_academic(cgpa, study_hours, college_tier, edu_level) -> float:
    cgpa_n = (cgpa / 4.0 if cgpa <= 4.0 else cgpa / 10.0) * 100
    study_s = min(study_hours / 42.0 * 100, 100)
    tier_s  = {"Tier 1": 95, "Tier 2": 65, "Tier 3": 38}[college_tier]
    lvl_m   = {"High School": .80, "Undergraduate": 1.0, "Postgraduate": 1.15, "PhD": 1.25}[edu_level]
    return round(min((cgpa_n * .50 + study_s * .30 + tier_s * .20) * lvl_m, 100), 1)

def score_financial(monthly_spend, savings, family_bg, discipline) -> float:
    sv = {"Low": 28, "Medium": 62, "High": 92}[savings]
    di = {"Impulsive": 22, "Balanced": 58, "Disciplined": 94}[discipline]
    fa = {"Low": 38, "Middle": 65, "High": 88}[family_bg]
    sp = max(0, 100 - monthly_spend / 500.0)
    return round(min(sv * .35 + di * .35 + fa * .20 + sp * .10, 100), 1)

def score_career(skill, experience, consistency) -> float:
    sk = {"Beginner": 38, "Intermediate": 68, "Advanced": 94}[skill]
    ex = 88 if experience else 48
    co = {"Low": 32, "Medium": 62, "High": 92}[consistency]
    return round(min(sk * .40 + ex * .35 + co * .25, 100), 1)

def score_lifestyle(screen, health, sleep) -> float:
    sk = screen.split()[0]
    sc = {"Low": 88, "Medium": 58, "High": 28}.get(sk, 55)
    hc = {"Poor": 28, "Average": 58, "Good": 92}[health]
    sl = {"Poor": 32, "Average": 62, "Good": 92}[sleep]
    return round(min(hc * .38 + sl * .38 + sc * .24, 100), 1)

def compute_scores(u: dict) -> dict:
    ac = score_academic(u["cgpa"], u["study_hours"], u["college_tier"], u["edu_level"])
    fi = score_financial(u["monthly_spend"], u["savings"], u["family_bg"], u["discipline"])
    ca = score_career(u["skill"], u["experience"], u["consistency"])
    li = score_lifestyle(u["screen_time"], u["health"], u["sleep"])
    co = round(ac * .30 + fi * .25 + ca * .25 + li * .20, 1)
    risk    = "Low" if co > 74 else ("Moderate" if co >= 50 else "High")
    profile = "Disciplined" if co > 74 else ("Balanced" if co >= 50 else "At Risk")
    trend   = ("Improving" if ac > 68 and ca > 68 else
               "Declining" if ac < 48 or ca < 48 else "Stable")
    return dict(academic=ac, financial=fi, career=ca, lifestyle=li,
                composite=co, risk=risk, profile=profile, trend=trend)

def simulate(u: dict, s: dict) -> dict:
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
        co = round(proj["academic"]*.30 + proj["financial"]*.25 +
                   proj["career"]*.25 + proj["lifestyle"]*.20, 1)
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
#  FLUX PROMPT BUILDER — fully data-driven
# ══════════════════════════════════════════════════════════════════════════════
def build_flux_prompt(key: str, sim_data: dict, user: dict, scores: dict) -> str:
    """
    Builds a rich, specific FLUX prompt from actual computed scores.
    Every visual element maps to real data — nothing generic.
    """
    fin_s   = sim_data["fin_status"]
    car_s   = sim_data["career_status"]
    lif_s   = sim_data["life_quality"]
    age     = sim_data["age"]
    income  = sim_data["income_lpa"]
    comp    = sim_data["composite"]
    country = user.get("country", "India")
    field   = user.get("field", "Engineering / Technology")

    # ── WEALTH → home/office environment ──────────────────────────────────
    wealth_desc = {
        "Wealthy": (
            "ultra-luxury penthouse apartment with floor-to-ceiling panoramic glass windows, "
            "city skyline visible at golden hour, polished marble and dark oak floors, "
            "minimalist bespoke furniture, designer walnut standing desk, "
            "three ultrawide curved monitors, warm ambient LED lighting, "
            "original canvas artwork on concrete walls, large indoor fiddle-leaf fig tree, "
            "premium La Marzocco espresso machine, immaculate and serene"
        ),
        "Comfortable": (
            "modern well-appointed apartment, large windows with city or leafy suburb view, "
            "light hardwood floors, ergonomic Herman Miller chair and sit-stand desk, "
            "two monitors, curated bookshelves, indoor plants, tasteful Scandinavian decor, "
            "comfortable and organised, soft natural light"
        ),
        "Moderate": (
            "mid-range furnished apartment, standard windows, laminate flooring, "
            "practical IKEA-style desk with single widescreen monitor, "
            "modest furniture, a few personal items on shelves, average overhead lighting, "
            "functional and lived-in with some clutter"
        ),
        "Tight": (
            "small rented room or shared flat, basic furniture, cluttered desk with budget laptop, "
            "dim yellow overhead light, minimal decor, stacked textbooks and papers, "
            "mismatched items, cramped and utilitarian"
        ),
        "Struggling": (
            "very sparse bare room, worn second-hand furniture, harsh fluorescent overhead light, "
            "almost no personal decor, old second-hand computer or just a phone, "
            "visible signs of financial hardship, peeling paint, minimal belongings"
        ),
    }.get(fin_s, "modest apartment with functional work setup")

    # ── CAREER → work context ─────────────────────────────────────────────
    career_desc = {
        "Elite": f"executive home office or glass-walled corner office in a skyscraper, multiple high-resolution displays showing {field} work, industry awards and framed credentials on wall, premium desk accessories",
        "Strong": f"professional home office or corporate open-plan space for {field}, dual monitors with professional software, organized desk with notebook and quality coffee mug",
        "Stable": f"standard office or neat home desk for {field}, single monitor, reasonable organisation, typical professional environment",
        "Emerging": f"co-working space or simple home desk, laptop open, early-career {field} environment, casual and functional",
        "Unstable": "informal workspace, laptop on dining table, scattered papers, uncertain work environment",
    }.get(car_s, "standard workspace")

    # ── LIFESTYLE → ambient quality ────────────────────────────────────────
    life_desc = {
        "Excellent": "yoga mat rolled up in corner, fruit bowl, water carafe, vibrant healthy energy, plants thriving, sunlit and airy",
        "Good": "water bottle, healthy snacks, clean and organised, positive calm atmosphere",
        "Average": "coffee mug, moderate tidiness, everyday lived-in feel",
        "Below Avg": "energy drink cans, takeout bag, messy desk, dark curtains drawn, signs of poor sleep",
        "Poor": "junk food wrappers, very messy, dark and stuffy, neglected space, visible exhaustion in the environment",
    }.get(lif_s, "ordinary living space")

    # ── COUNTRY → architecture & cultural context ─────────────────────────
    country_map = {
        "India": {
            "Wealthy":     "luxury high-rise apartment in Bandra Mumbai or Koramangala Bangalore, Indian cultural art pieces, monsoon city lights outside",
            "Comfortable": "well-maintained apartment in an Indian metro city like Pune or Hyderabad, Indian design accents",
            "Moderate":    "mid-tier apartment in an Indian city, typical Indian urban neighbourhood visible outside",
            "Tight":       "small rented room in a PG or modest locality in an Indian city",
            "Struggling":  "basic room in a low-income area of an Indian city",
        },
        "United States": {
            "Wealthy":     "upscale Manhattan or San Francisco apartment, American luxury interior design",
            "Comfortable": "comfortable American suburban home office or urban apartment",
            "Moderate":    "standard American apartment in a mid-tier US city",
            "Tight":       "small apartment in a US city, budget American furnishings",
            "Struggling":  "bare budget room in the US, minimal American furnishings",
        },
        "United Kingdom": {
            "Wealthy":     "elegant Kensington or Chelsea London flat, British luxury interior with heritage accents",
            "Comfortable": "comfortable UK flat in London or Manchester, contemporary British design",
            "Moderate":    "standard UK terraced house flat, typical British interior",
            "Tight":       "small rented UK flat, modest British furnishings",
            "Struggling":  "sparse UK bedsit or shared house room",
        },
        "Canada": {
            "Wealthy":     "luxury condo in Toronto or Vancouver with mountain or lake view, Canadian modern interior",
            "Comfortable": "comfortable Canadian apartment or townhouse, warm Scandinavian-Canadian decor",
            "Moderate":    "standard Canadian apartment, functional Canadian style",
            "Tight":       "small rented room in a Canadian city",
            "Struggling":  "sparse basic room in Canada",
        },
        "Australia": {
            "Wealthy":     "luxury beachside apartment in Sydney or Melbourne, Australian indoor-outdoor design, bright natural light",
            "Comfortable": "comfortable Australian home or apartment, relaxed coastal Australian aesthetic",
            "Moderate":    "standard Australian suburban apartment, casual Australian interior",
            "Tight":       "small rented room in an Australian city",
            "Struggling":  "sparse basic Australian room",
        },
        "Germany": {
            "Wealthy":     "sleek Frankfurt or Munich premium apartment, precise German minimalist design, floor-to-ceiling windows",
            "Comfortable": "modern German apartment with Bauhaus-influenced furniture, functional and clean",
            "Moderate":    "standard German Altbau apartment, functional European interior",
            "Tight":       "small German Zimmer or WG room",
            "Struggling":  "sparse basic German room",
        },
        "Singapore": {
            "Wealthy":     "ultra-modern Singapore high-rise with Marina Bay skyline view, sleek pan-Asian luxury interior",
            "Comfortable": "comfortable Singapore condo, clean modern Southeast Asian design",
            "Moderate":    "HDB flat in Singapore, neat and functional",
            "Tight":       "small HDB room in Singapore",
            "Struggling":  "sparse room in a Singapore HDB block",
        },
        "UAE": {
            "Wealthy":     "ultra-luxury Dubai apartment with Burj Khalifa and skyline view, Arabic contemporary interior design",
            "Comfortable": "modern UAE apartment in Dubai or Abu Dhabi, contemporary Gulf interior",
            "Moderate":    "standard UAE apartment, functional modern interior",
            "Tight":       "small rented apartment in UAE",
            "Struggling":  "sparse basic room in UAE",
        },
    }
    country_detail = country_map.get(country, {}).get(
        fin_s, f"urban setting in {country} reflecting local architecture and culture at a {fin_s.lower()} financial level"
    )

    # ── TIME OF DAY ────────────────────────────────────────────────────────
    time_light = {
        "Excellent": "warm golden morning light streaming through windows",
        "Good":      "bright morning natural light",
        "Average":   "neutral afternoon daylight",
        "Below Avg": "late evening with artificial lamp light, curtains closed",
        "Poor":      "harsh artificial overhead light at night, windows dark",
    }.get(lif_s, "natural daylight")

    horizon_label = {"5_year": "5 years", "10_year": "10 years", "25_year": "25 years"}.get(key, "")

    prompt = (
        f"Photorealistic interior lifestyle photograph for a {field} professional, "
        f"{horizon_label} into their career, age {age}. "
        f"Setting: {wealth_desc}. "
        f"Work context: {career_desc}. "
        f"Lifestyle details: {life_desc}. "
        f"Location: {country_detail}. "
        f"Lighting: {time_light}. "
        f"This person earns approximately {income} LPA annually "
        f"with a {car_s} career and {fin_s} financial standing. "
        f"NO people, NO faces, NO human figures visible in the scene. "
        f"NO text, NO signs, NO watermarks in the image. "
        f"Style: editorial interior photography, cinematic, "
        f"shot on Phase One medium format camera, 45mm tilt-shift lens, "
        f"natural ambient light, shallow depth of field, "
        f"photorealistic 8K architectural magazine photography, "
        f"hyper-detailed textures, realistic materials, "
        f"no cartoon, no illustration, no CGI render look, no AI art style."
    )
    return prompt

# ══════════════════════════════════════════════════════════════════════════════
#  FLUX IMAGE GENERATION
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_hf_client():
    try:
        from huggingface_hub import InferenceClient
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        if not token:
            return None
        return InferenceClient(token=token)
    except Exception:
        return None

def generate_flux_image(prompt: str) -> Image.Image | None:
    client = get_hf_client()
    if not client:
        return None
    try:
        result = client.text_to_image(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        if isinstance(result, Image.Image):
            return result
        return Image.open(io.BytesIO(result))
    except Exception as e:
        st.warning(f"FLUX generation error: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  PIL FALLBACK — data-driven scene when FLUX unavailable
# ══════════════════════════════════════════════════════════════════════════════
def make_fallback_image(key: str, sim_data: dict, scores: dict, field: str) -> Image.Image:
    W, H = 800, 520
    fin_s  = sim_data["fin_status"]
    car_s  = sim_data["career_status"]
    lif_s  = sim_data["life_quality"]
    comp   = sim_data["composite"]
    income = sim_data["income_lpa"]
    age    = sim_data["age"]

    fin_r = {"Struggling":0,"Tight":1,"Moderate":2,"Comfortable":3,"Wealthy":4}.get(fin_s,2)
    car_r = {"Unstable":0,"Emerging":1,"Stable":2,"Strong":3,"Elite":4}.get(car_s,2)
    lif_r = {"Poor":0,"Below Avg":1,"Average":2,"Good":3,"Excellent":4}.get(lif_s,2)
    rng   = random.Random(int(comp*100 + sim_data["years"]*777))

    skies = {
        4:[(5,8,22),(14,20,48)],3:[(8,14,32),(18,26,54)],
        2:[(14,18,38),(24,30,52)],1:[(18,18,30),(28,26,40)],0:[(20,14,14),(30,20,18)],
    }
    c1,c2 = skies.get(fin_r,skies[2])

    canvas = Image.new("RGB",(W,H))
    draw   = ImageDraw.Draw(canvas)

    for y in range(H):
        t=y/H; r=int(c1[0]+(c2[0]-c1[0])*t); g=int(c1[1]+(c2[1]-c1[1])*t); b=int(c1[2]+(c2[2]-c1[2])*t)
        draw.line([(0,y),(W,y)],fill=(r,g,b))

    if fin_r>=3:
        for _ in range(rng.randint(30,55)):
            sx,sy=rng.randint(0,W),rng.randint(0,int(H*.38))
            br=rng.randint(130,235)
            draw.ellipse([sx-1,sy-1,sx+1,sy+1],fill=(br,br,min(255,br+30)))

    sky_y=int(H*.50)
    if fin_r>=1:
        for _ in range(4+fin_r*3):
            bx=rng.randint(-40,W+40); bh=rng.randint(int(55+fin_r*28),int(110+fin_r*55))
            bw=rng.randint(22,44+fin_r*8)
            bc=(int(c1[0]+rng.randint(5,25)),int(c1[1]+rng.randint(5,22)),int(c1[2]+rng.randint(10,35)))
            draw.rectangle([bx,sky_y-bh,bx+bw,sky_y+3],fill=bc)
            for wr in range(max(1,bh//16)):
                for wc in range(max(1,bw//10)):
                    if rng.random()<.5:
                        wx=bx+3+wc*10; wy=sky_y-bh+5+wr*16; wb=rng.randint(155,240)
                        draw.rectangle([wx,wy,wx+6,wy+10],fill=(wb,int(wb*.82),int(wb*.48)))

    floor_y=int(H*.60)
    wc_map={4:(28,24,44),3:(36,40,54),2:(44,44,58),1:(52,48,46),0:(58,50,42)}
    wc=wc_map.get(fin_r,(44,44,58))
    for y in range(int(H*.30),floor_y+5):
        t=(y-int(H*.30))/(floor_y-int(H*.30)); cc=tuple(max(0,int(wc[i]-12*t)) for i in range(3))
        draw.line([(0,y),(W,y)],fill=cc)

    fc_map={4:(52,44,34),3:(58,50,40),2:(65,58,48),1:(72,64,54),0:(78,70,60)}
    fc=fc_map.get(fin_r,(65,58,48))
    for y in range(floor_y,H):
        t=(y-floor_y)/(H-floor_y); cc=tuple(max(0,int(fc[i]-18*t)) for i in range(3))
        draw.line([(0,y),(W,y)],fill=cc)

    if fin_r>=3:
        for rx in range(0,W,3):
            sh=int(rng.uniform(.04,.14)*255)
            draw.line([(rx,floor_y),(rx,floor_y+5)],fill=(sh,sh,sh))

    n_win=max(1,fin_r+1); win_w=88+fin_r*22; win_h=84+fin_r*18; win_y=int(H*.33); spacing=W//(n_win+1)
    for wi in range(n_win):
        wx=spacing*(wi+1)-win_w//2
        fr=(175,155,118) if fin_r>=3 else (100,92,80) if fin_r>=2 else (66,60,52)
        draw.rectangle([wx-4,win_y-4,wx+win_w+4,win_y+win_h+4],fill=fr)
        for wy2 in range(win_h):
            t=wy2/win_h; sc=tuple(int(c1[i]*(1-t)+max(0,c1[i]-15)*t) for i in range(3))
            draw.line([(wx,win_y+wy2),(wx+win_w,win_y+wy2)],fill=sc)
        draw.line([(wx+win_w//2,win_y),(wx+win_w//2,win_y+win_h)],fill=fr,width=2)
        draw.line([(wx,win_y+win_h//2),(wx+win_w,win_y+win_h//2)],fill=fr,width=2)

    dx=int(W*.07); dy=floor_y-14; dw=int(W*.86); dd=18
    desk_c={4:(68,50,28),3:(58,44,26),2:(74,64,46),1:(80,70,54),0:(88,78,62)}.get(fin_r,(74,64,46))
    draw.rectangle([dx,dy,dx+dw,dy+dd],fill=desk_c)
    draw.line([(dx,dy),(dx+dw,dy)],fill=tuple(min(255,c+45) for c in desk_c),width=1)
    for lx in [dx+12,dx+dw-18]:
        draw.rectangle([lx,dy+dd,lx+10,floor_y+5],fill=tuple(max(0,c-22) for c in desk_c))

    mon_n=1 if car_r<=1 else 2 if car_r<=3 else 3
    if mon_n==1: mon_xs=[dx+dw//2-75]
    elif mon_n==2: mon_xs=[dx+55,dx+dw//2+25]
    else: mon_xs=[dx+18,dx+dw//2-72,dx+dw-198]

    mw=130+car_r*14; mh=88+car_r*10; my=int(H*.24)-mh
    for mpx in mon_xs:
        bez=(12,12,18) if car_r>=3 else (22,20,16)
        draw.rectangle([mpx-6,my-6,mpx+mw+6,my+mh+6],fill=bez)
        draw.rectangle([mpx,my,mpx+mw,my+mh],fill=(5,9,24) if car_r>=3 else (10,14,28))
        acc=(130,175,255) if fin_r>=2 else (95,125,195)
        is_tech=any(x in field for x in ["Tech","Eng","Sci"])
        is_biz=any(x in field for x in ["Comm","Bus","Law","Med"])
        if is_tech:
            for li in range(7):
                lw=rng.randint(int(mw*.2),int(mw*.82))
                draw.line([(mpx+5,my+8+li*11),(mpx+5+lw,my+8+li*11)],
                          fill=acc if rng.random()>.35 else (75,98,128),width=1)
        elif is_biz:
            bvs=[rng.randint(18,68) for _ in range(5)]; bmax=max(bvs); bsp=(mw-14)//5
            for bi,bv in enumerate(bvs):
                bh2=int(bv/bmax*(mh-20)); bx2=mpx+7+bi*bsp
                draw.rectangle([bx2,my+mh-5-bh2,bx2+bsp-3,my+mh-5],fill=acc)
        else:
            for _ in range(14):
                ddx=mpx+rng.randint(4,mw-4); ddy=my+rng.randint(4,mh-4)
                draw.ellipse([ddx-2,ddy-2,ddx+2,ddy+2],fill=acc)
        sbx=mpx+mw//2-7
        draw.rectangle([sbx,my+mh+4,sbx+14,dy+2],fill=tuple(max(0,c-30) for c in bez))
        draw.rectangle([sbx-14,dy-2,sbx+28,dy+3],fill=tuple(max(0,c-22) for c in bez))

    kbx=mon_xs[0]+(mw-105)//2; kby=dy-20
    kbc=(28,26,22) if fin_r>=3 else (48,44,38)
    draw.rectangle([kbx,kby,kbx+105,kby+14],fill=kbc,outline=(75,72,65),width=1)
    for kr in range(2):
        for kc2 in range(11):
            draw.rectangle([kbx+3+kc2*9,kby+3+kr*5,kbx+9+kc2*9,kby+6+kr*5],
                           fill=tuple(min(255,c+22) for c in kbc))
    draw.ellipse([kbx+116,kby-1,kbx+132,kby+18],fill=kbc,outline=(85,82,75))

    if fin_r>=2:
        plx=dx+20; ply=dy
        draw.rectangle([plx,ply-30,plx+24,ply+2],fill=(68,42,18))
        for _ in range(rng.randint(5,8)):
            lx2=plx+12+rng.randint(-34,34); ly2=ply-30+rng.randint(-38,12)
            draw.ellipse([lx2-9,ly2-9,lx2+9,ly2+9],fill=(18,rng.randint(85,138),32))

    if fin_r>=1:
        bkx=dx+dw-165
        for _ in range(rng.randint(2,4+fin_r)):
            bw2=rng.randint(13,24); bh2=rng.randint(38,65+fin_r*8)
            draw.rectangle([bkx,dy-bh2,bkx+bw2,dy+1],
                           fill=(rng.randint(80,200),rng.randint(40,120),rng.randint(40,88)))
            bkx+=bw2+3

    if fin_r>=2:
        lpx=dx+dw-48; lpc=(185,170,148) if fin_r>=3 else (115,108,98)
        draw.rectangle([lpx,dy-4,lpx+16,dy+2],fill=lpc)
        draw.line([(lpx+8,dy-4),(lpx+8,dy-50)],fill=lpc,width=3)
        shc=(255,218,95) if fin_r>=3 else (215,178,78)
        draw.ellipse([lpx-10,dy-64,lpx+26,dy-44],fill=shc)

    if fin_r>=3:
        rc=(65,48,95) if fin_r==4 else (78,58,42)
        draw.rectangle([dx+8,floor_y+6,dx+dw-8,floor_y+38],fill=rc)
        draw.rectangle([dx+14,floor_y+10,dx+dw-14,floor_y+34],
                       outline=tuple(min(255,c+44) for c in rc),width=1)

    mgx=dx+dw-88; mgy=dy
    mgc=(175,75,38) if fin_r>=3 else (135,95,58)
    draw.rectangle([mgx,mgy-32,mgx+24,mgy+2],fill=mgc)
    draw.rectangle([mgx+2,mgy-30,mgx+22,mgy-8],fill=tuple(int(c*.6) for c in mgc))
    draw.arc([mgx+24,mgy-24,mgx+34,mgy-10],270,90,fill=mgc,width=3)

    arr=np.array(canvas)
    bar_h=92; bar_region=arr[H-bar_h:]
    arr[H-bar_h:]=np.clip(bar_region*0.18+np.array([5,5,14])*0.82,0,255).astype(np.uint8)
    canvas=Image.fromarray(arr); draw=ImageDraw.Draw(canvas)

    try:
        fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
        fm=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",14)
        fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
    except:
        fb=fm=fs=ImageFont.load_default()

    sc=(80,200,120) if comp>=75 else (232,184,75) if comp>=55 else (251,146,60) if comp>=40 else (251,113,133)
    lbl_map={"5_year":"5 YEARS","10_year":"10 YEARS","25_year":"25 YEARS"}
    draw.text((18,H-bar_h+8),lbl_map.get(key,""),font=fb,fill=(232,184,75))
    draw.text((18,H-bar_h+34),f"{car_s} Career  ·  {fin_s}  ·  {lif_s} Lifestyle",font=fm,fill=(188,196,222))
    draw.text((18,H-bar_h+54),f"Age {age}  ·  Score {comp:.0f}/100  ·  ₹{income} LPA",font=fs,fill=(138,148,178))
    sbx,sby=W-135,H-bar_h+10
    draw.text((sbx,sby),"COMPOSITE",font=fs,fill=(98,108,145))
    draw.rectangle([sbx,sby+16,sbx+100,sby+26],fill=(18,20,34))
    draw.rectangle([sbx,sby+16,sbx+int(comp),sby+26],fill=sc)
    draw.text((sbx,sby+30),f"{comp:.0f}/100",font=fs,fill=sc)
    draw.rectangle([1,1,W-2,H-2],outline=(232,184,75),width=2)
    draw.rectangle([3,3,W-4,H-4],outline=(80,60,18),width=1)

    noise_arr=np.array(canvas).astype(np.float32)
    noise=np.random.normal(0,5,noise_arr.shape)
    return Image.fromarray(np.clip(noise_arr+noise,0,255).astype(np.uint8))

def generate_all_images(sim, scores, flux_prompts, user) -> dict:
    images = {}
    for key in ("5_year","10_year","25_year"):
        prompt = flux_prompts.get(key,"")
        img = generate_flux_image(prompt) if prompt else None
        if img is None:
            img = make_fallback_image(key, sim[key], scores, user.get("field","Engineering / Technology"))
        else:
            img = img.resize((800,520), Image.LANCZOS)
        images[key] = img
    return images

def save_outputs(images, sim, scenarios, flux_prompts):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    saved = {}
    for key, img in images.items():
        folder = OUTPUT_DIR / key
        img_path = folder / f"user_{ts}_{key}.png"
        img.save(img_path)
        meta = {"timestamp":ts,"stage":key,"age":sim[key]["age"],
                "composite":sim[key]["composite"],"income_lpa":sim[key]["income_lpa"],
                "flux_prompt":flux_prompts.get(key,""),"scenario":scenarios.get(key,"")}
        with open(folder/f"user_{ts}_{key}_meta.json","w") as f:
            json.dump(meta,f,indent=2)
        saved[key] = str(img_path)
    return saved

# ══════════════════════════════════════════════════════════════════════════════
#  GEMINI ANALYSIS + SCENARIOS
# ══════════════════════════════════════════════════════════════════════════════
def run_analysis(u, s, sim) -> str:
    prompt = f"""You are a behavioural scientist and life-trajectory expert.

STUDENT PROFILE:
Age {u['age']} | Country: {u.get('country','India')} | {u['edu_level']} in {u['field']} | {u['college_tier']}
CGPA: {u['cgpa']} | Study hrs/wk: {u['study_hours']} | Target: {u['target_career']}
Skill: {u['skill']} | Experience: {u['experience']} | Consistency: {u['consistency']}
Monthly spend: ₹{u['monthly_spend']} | Savings: {u['savings']} | Family: {u['family_bg']}
Discipline: {u['discipline']} | Screen: {u['screen_time']} | Health: {u['health']} | Sleep: {u['sleep']}

SCORES: Academic {s['academic']} | Financial {s['financial']} | Career {s['career']} | Lifestyle {s['lifestyle']}
Composite {s['composite']} | Risk: {s['risk']} | Trend: {s['trend']}

PROJECTIONS:
5yr  → {sim['5_year']['career_status']} | {sim['5_year']['fin_status']} | ₹{sim['5_year']['income_lpa']} LPA
10yr → {sim['10_year']['career_status']} | {sim['10_year']['fin_status']} | ₹{sim['10_year']['income_lpa']} LPA
25yr → {sim['25_year']['career_status']} | {sim['25_year']['fin_status']} | ₹{sim['25_year']['income_lpa']} LPA

Write a COMPREHENSIVE ANALYSIS:

**CURRENT STATE** — 3-4 honest direct sentences to the student.
**5-YEAR OUTLOOK** — Vivid paragraph: daily life, work, home, city in {u.get('country','India')}.
**10-YEAR OUTLOOK** — Vivid paragraph: career, lifestyle, relationships.
**25-YEAR OUTLOOK** — Vivid paragraph: retirement readiness, health, legacy.
**KEY RISKS** — 3-5 specific bullet points.
**TOP STRENGTHS** — 2-3 bullet points.
**PRIORITY ACTIONS** — 5 numbered concrete measurable steps.

Be brutally honest, compassionate, country-context-aware ({u.get('country','India')})."""
    return gemini_call(prompt, 0.72, 2048)

def run_scenarios(u, s, sim) -> dict:
    narratives = {}
    for key, label in [("5_year","5 years"),("10_year","10 years"),("25_year","25 years")]:
        d = sim[key]
        prompt = f"""Describe the DAILY LIFE of this person {label} from now in {u.get('country','India')}.

Scores → Academic:{s['academic']} Financial:{s['financial']} Career:{s['career']} Lifestyle:{s['lifestyle']}
Projection → Career:{d['career_status']} Finance:{d['fin_status']} Quality:{d['life_quality']}
Income:₹{d['income_lpa']} LPA | Age:{d['age']} | Field:{u['field']} | Country:{u.get('country','India')}

Write ONE vivid paragraph (5-7 sentences) describing:
• Their morning routine and home environment in {u.get('country','India')}
• Their work setup and what their desk looks like
• Their financial reality — what they can/cannot afford
• Their energy, health, and physical appearance
• The emotional tone of their life

Be sensory and specific. Reference the country. No generic advice."""
        narratives[key] = gemini_call(prompt, 0.85, 512)
    return narratives

# ══════════════════════════════════════════════════════════════════════════════
#  CHARTS
# ══════════════════════════════════════════════════════════════════════════════
_PT = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
           font=dict(family="DM Sans",color="#9aa0bc",size=12),
           margin=dict(l=10,r=10,t=40,b=10))

def _sc(v):
    return "#34d399" if v>=75 else "#e8b84b" if v>=55 else "#fb923c" if v>=40 else "#fb7185"

def bar_chart(s):
    cats=["Academic","Financial","Career","Lifestyle"]
    vals=[s[c.lower()] for c in cats]
    fig=go.Figure(go.Bar(x=cats,y=vals,marker_color=[_sc(v) for v in vals],
        text=[f"{v:.0f}" for v in vals],textposition="outside",marker_line_width=0))
    fig.update_layout(yaxis=dict(range=[0,112],gridcolor="rgba(255,255,255,.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,.05)"),
        title=dict(text="Domain Scores",font=dict(size=13,color="#e8b84b")),**_PT)
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

def trajectory_chart(s,sim):
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

def waterfall_chart(s,sim):
    domains=["Academic","Financial","Career","Lifestyle"]
    delta=[round(sim["25_year"][d.lower()]-s[d.lower()],1) for d in domains]
    fig=go.Figure(go.Bar(x=domains,y=delta,
        marker_color=["#34d399" if d>=0 else "#fb7185" for d in delta],
        text=[f"{'+' if d>=0 else ''}{d:.1f}" for d in delta],textposition="outside"))
    fig.update_layout(yaxis=dict(gridcolor="rgba(255,255,255,.05)"),
        title=dict(text="25-Year Change by Domain",font=dict(size=13,color="#e8b84b")),**_PT)
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  ACTION HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _act_academic(s,u):
    if s["academic"]>=75: return f"Strong profile. Target competitive exams or research publications to stand out from peers at {u['college_tier']} institutions."
    elif s["academic"]>=50: return f"CGPA {u['cgpa']} is recoverable. Increase to 35+ study hrs/week. Target +0.5 CGPA each semester using spaced repetition."
    else: return f"Critical: {u['cgpa']} CGPA from {u['college_tier']} limits early opportunities. Build strong projects to compensate immediately."

def _act_financial(s,u):
    if s["financial"]>=75: return "Excellent habits. Invest 20% of any income in index funds. Resist lifestyle inflation as income grows."
    elif s["financial"]>=50: return f"Start ₹{max(500,u['monthly_spend']//20)}/month SIP today. Track every rupee for 30 days — identify your single biggest spending leak."
    else: return "Immediate: freeze discretionary spending for 2 weeks. Map income vs. expenses honestly. Build 3-month emergency fund before investing."

def _act_career(s,u):
    t=u.get("target_career","your target role") or "your target role"
    if s["career"]>=75: return f"On track for {t}. Build personal brand on LinkedIn/GitHub/blog so opportunities come to you."
    elif s["career"]>=50: return f"Gap vs {t}: commit to one 12-week intensive course + one real project this quarter."
    else: return f"Skill deficit is the primary blocker. 2 hrs/day for 90 days on {t}-specific skills. Find a mentor now."

def _act_lifestyle(s,u):
    if s["lifestyle"]>=75: return "Healthy habits are your cognitive multiplier. Protect sleep above everything else."
    elif s["lifestyle"]>=50: return "Fix sleep schedule first: same time every night, 7.5 hrs minimum. Focus and discipline follow automatically."
    else: return "Poor health + poor sleep + high screen time is destroying your output capacity. Start: 10-min walk daily + phone off at 10 PM."

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
  <div class="hero-eye">⬡ AI-Powered Life Trajectory Engine · FLUX + Gemini</div>
  <div class="hero-title">Future <span>Life</span><br>Simulator</div>
  <div class="hero-sub">
    Your academic, financial, career, and lifestyle inputs are scored and projected 5, 10, and 25 years ahead.
    FLUX.1-schnell generates photorealistic images of exactly what your lifestyle environment will look like —
    based on your actual predicted income, career status, country, and quality of life.
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-logo">⬡ FLS · v4.0</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-sec">🌍 Country</div>', unsafe_allow_html=True)
    country = st.selectbox("Country / Region", COUNTRIES, index=0)

    st.markdown('<div class="sb-sec">👤 Basic Info</div>', unsafe_allow_html=True)
    age    = st.slider("Current Age", 15, 35, 20)
    gender = st.selectbox("Gender", ["Prefer not to say","Male","Female","Non-binary"])

    st.markdown('<div class="sb-sec">🎓 Academic</div>', unsafe_allow_html=True)
    edu_level    = st.selectbox("Education Level", ["High School","Undergraduate","Postgraduate","PhD"])
    cgpa         = st.number_input("CGPA / GPA", 0.0, 10.0, 7.5, 0.1, help="4.0 or 10.0 scale — auto-detected")
    field        = st.selectbox("Field of Study", ["Engineering / Technology","Science","Commerce / Business","Arts / Humanities","Medicine / Healthcare","Law","Other"])
    college_tier = st.selectbox("Institution Tier", ["Tier 1","Tier 2","Tier 3"], help="Tier 1 = top national/global institutions")
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

    st.markdown("---")
    run_btn = st.button(" Generate My Future", use_container_width=True)

user = dict(
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
#  WELCOME
# ══════════════════════════════════════════════════════════════════════════════
if not run_btn and not st.session_state.analysis_done:
    st.markdown("""
    <div class="welcome">
      <div style="font-size:4rem;margin-bottom:1.2rem;">🔮</div>
      <div class="welcome-title">See Your Future Lifestyle</div>
      <div class="welcome-body">
        Fill in your profile on the left and press <strong>Generate My Future</strong>.<br/>
        The scoring engine projects your life 5, 10, and 25 years ahead — then
        <strong>FLUX.1-schnell</strong> generates photorealistic images of your actual
        predicted lifestyle environment: your home, your desk, your city —
        shaped exactly by your scores.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    for col,icon,ttl,body in [
        (c1,"📊","Scoring Engine","Rule-based engine normalises your inputs into Academic (30%), Financial (25%), Career (25%), and Lifestyle (20%) scores — then projects 5, 10, 25-year outcomes."),
        (c2,"🖼️","FLUX Images","FLUX.1-schnell generates photorealistic interiors calibrated to your exact income, career status, country, and lifestyle quality — no faces, pure environment."),
        (c3,"🤖","Gemini Analysis","Gemini 2.0 Flash writes a brutally honest narrative of your projected life, personalised to your country and current trajectory."),
    ]:
        with col:
            st.markdown(f'<div class="card"><div style="font-size:1.8rem;margin-bottom:.5rem;">{icon}</div>'
                        f'<div style="font-family:JetBrains Mono,monospace;font-size:.65rem;letter-spacing:.14em;color:rgba(232,184,75,.6);text-transform:uppercase;margin-bottom:.4rem;">{ttl}</div>'
                        f'<div style="font-size:.86rem;color:rgba(226,230,243,.58);line-height:1.7;">{body}</div></div>',
                        unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    with st.status("⚙ Running simulation…", expanded=True) as status:
        st.write("📐 Computing scores…")
        s   = compute_scores(user)
        sim = simulate(user, s)
        st.session_state.scores = s; st.session_state.simulation = sim

        st.write("🤖 Gemini deep analysis…")
        st.session_state.llm_analysis = run_analysis(user, s, sim)

        st.write("🌍 Generating scenario narratives…")
        st.session_state.future_scenarios = run_scenarios(user, s, sim)

        st.write("✍️ Building FLUX prompts from your scores…")
        fp = {k: build_flux_prompt(k, sim[k], user, s) for k in ("5_year","10_year","25_year")}
        st.session_state.flux_prompts = fp

        st.write("🎨 FLUX.1-schnell generating lifestyle images…")
        imgs = generate_all_images(sim, s, fp, user)
        st.session_state.images = imgs

        st.write("💾 Saving to models/FSVE/…")
        save_outputs(imgs, sim, st.session_state.future_scenarios, fp)

        st.session_state.analysis_done = True
        status.update(label="✅ Done!", state="complete", expanded=False)

# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.analysis_done:
    st.stop()

s   = st.session_state.scores
sim = st.session_state.simulation

tab1,tab2,tab3,tab4 = st.tabs(["📊  Dashboard","🔮  Visual Future","🤖  AI Analysis","💡  Action Plan"])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### 📊 Behavioural Performance Dashboard")
    k1,k2,k3,k4 = st.columns(4)
    rb={"Low":"#34d399","Moderate":"#fbbf24","High":"#fb7185"}[s["risk"]]
    ti={"Improving":"📈","Stable":"➡️","Declining":""}[s["trend"]]
    tc={"Improving":"#34d399","Stable":"#e8b84b","Declining":"#fb7185"}[s["trend"]]
    with k1:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Composite Score</div><div class="kpi-value" style="color:{_sc(s["composite"])};">{s["composite"]:.0f}</div><div class="kpi-sub">out of 100</div></div>',unsafe_allow_html=True)
    with k2:
        bc={"Low":"b-low","Moderate":"b-mod","High":"b-high"}[s["risk"]]
        st.markdown(f'<div class="kpi"><div class="kpi-label">Risk Level</div><div style="margin-top:.5rem;"><span class="{bc}">{s["risk"]}</span></div><div class="kpi-sub" style="margin-top:.4rem;">{s["profile"]}</div></div>',unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Growth Trend</div><div class="kpi-value" style="color:{tc};font-size:1.5rem;">{ti} {s["trend"]}</div></div>',unsafe_allow_html=True)
    with k4:
        est=sim["25_year"]["income_lpa"]
        st.markdown(f'<div class="kpi"><div class="kpi-label">25-yr Est. Income</div><div class="kpi-value" style="color:#22d3ee;">₹{est}</div><div class="kpi-sub">LPA</div></div>',unsafe_allow_html=True)
    st.markdown("<br/>",unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca: st.plotly_chart(bar_chart(s),use_container_width=True)
    with cb: st.plotly_chart(radar_chart(s),use_container_width=True)
    st.plotly_chart(trajectory_chart(s,sim),use_container_width=True)
    st.plotly_chart(waterfall_chart(s,sim),use_container_width=True)
    st.markdown("#### Projected Outcomes by Horizon")
    t1,t2,t3=st.columns(3)
    for col,key,lbl in zip([t1,t2,t3],["5_year","10_year","25_year"],["5 Years","10 Years","25 Years"]):
        d=sim[key]; color=_sc(d["composite"])
        with col:
            st.markdown(f'''<div class="tl-card">
              <div class="tl-year">{lbl.upper()} · AGE {d["age"]} · {user.get("country","India").upper()}</div>
              <div class="tl-income" style="color:{color};">₹{d["income_lpa"]} LPA</div>
              <div class="tl-stat">Score {d["composite"]}/100</div>
              <div style="margin-top:.7rem;display:flex;flex-direction:column;gap:.22rem;">
                <div class="tl-stat">💼 {d["career_status"]}</div>
                <div class="tl-stat">💰 {d["fin_status"]}</div>
                <div class="tl-stat">🌱 {d["life_quality"]}</div>
              </div>
            </div>''',unsafe_allow_html=True)

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔮 FLUX-Generated Lifestyle Environment Projections")
    hf_token=os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        st.markdown('<div class="a-warn">⚠️ <b>HF_TOKEN not set</b> — showing data-driven PIL fallback. Add <code>HF_TOKEN=hf_...</code> to your .env for real FLUX images.</div>',unsafe_allow_html=True)
    else:
        st.markdown('<div class="a-ok">✅ <b>FLUX.1-schnell active</b> — images generated by Black Forest Labs FLUX, prompted directly by your computed scores.</div>',unsafe_allow_html=True)
    st.markdown(f'<div style="color:rgba(226,230,243,.42);font-size:.83rem;margin-bottom:1.5rem;">Each image prompt is built from your exact financial status, career tier, lifestyle quality, field, and country ({user.get("country","India")}) — not generic templates.</div>',unsafe_allow_html=True)

    for key,label in [("5_year","5 Years"),("10_year","10 Years"),("25_year","25 Years")]:
        img  = st.session_state.images.get(key)
        narr = st.session_state.future_scenarios.get(key,"")
        prmp = st.session_state.flux_prompts.get(key,"")
        d    = sim[key]
        st.markdown(f"#### {label} · Age {d['age']} · {user.get('country','India')}")
        ci,co=st.columns([3,2])
        with ci:
            if img:
                st.markdown('<div class="img-frame">',unsafe_allow_html=True)
                st.image(img,use_container_width=True)
                st.markdown('</div>',unsafe_allow_html=True)
                buf=io.BytesIO(); img.save(buf,format="PNG")
                st.download_button(f"⬇ Download {label}",buf.getvalue(),
                    file_name=f"fls_{key}.png",mime="image/png")
        with co:
            color=_sc(d["composite"])
            st.markdown(f'''<div class="card-gold">
              <div style="font-family:JetBrains Mono,monospace;font-size:.58rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(232,184,75,.45);">Projected Income</div>
              <div style="font-family:DM Serif Display,serif;font-size:1.8rem;color:{color};">₹{d["income_lpa"]} LPA</div>
              <div style="display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.6rem;">
                <span style="background:rgba(232,184,75,.08);border:1px solid rgba(232,184,75,.22);border-radius:6px;padding:.18rem .55rem;font-size:.7rem;font-family:JetBrains Mono,monospace;">{d["career_status"]}</span>
                <span style="background:rgba(34,211,238,.06);border:1px solid rgba(34,211,238,.2);border-radius:6px;padding:.18rem .55rem;font-size:.7rem;font-family:JetBrains Mono,monospace;">{d["fin_status"]}</span>
                <span style="background:rgba(52,211,153,.06);border:1px solid rgba(52,211,153,.18);border-radius:6px;padding:.18rem .55rem;font-size:.7rem;font-family:JetBrains Mono,monospace;">{d["life_quality"]}</span>
              </div>
            </div>''',unsafe_allow_html=True)
            st.markdown(f'''<div class="card" style="font-size:.82rem;">
              <div style="font-family:JetBrains Mono,monospace;font-size:.56rem;letter-spacing:.18em;text-transform:uppercase;color:rgba(232,184,75,.38);margin-bottom:.5rem;">Scores @ {label}</div>
              {"".join([
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin:.25rem 0;">'
                f'<span style="color:rgba(226,230,243,.5);font-size:.82rem;">{k}</span>'
                f'<div style="display:flex;align-items:center;gap:.5rem;">'
                f'<div style="width:55px;height:4px;background:rgba(255,255,255,.05);border-radius:2px;">'
                f'<div style="width:{d[k.lower()]:.0f}%;height:4px;background:{_sc(d[k.lower()])};border-radius:2px;"></div></div>'
                f'<span style="color:{_sc(d[k.lower()])};font-family:JetBrains Mono,monospace;font-size:.7rem;font-weight:600;">{d[k.lower()]:.0f}</span>'
                f'</div></div>'
                for k in ["Academic","Financial","Career","Lifestyle"]
              ])}
            </div>''',unsafe_allow_html=True)
            if narr:
                st.markdown(f'<div class="narrative">{narr}</div>',unsafe_allow_html=True)
            if prmp:
                with st.expander("🎨 FLUX Prompt"):
                    st.code(prmp,language=None)
        st.markdown("---")

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🤖 Gemini AI Deep Analysis")
    st.markdown(f'<div style="color:rgba(226,230,243,.42);font-size:.82rem;margin-bottom:1rem;">Gemini 2.0 Flash · {user.get("country","India")} context</div>',unsafe_allow_html=True)
    analysis=st.session_state.llm_analysis
    if analysis and not analysis.startswith("["):
        st.markdown('<div class="narrative">',unsafe_allow_html=True)
        st.markdown(analysis)
        st.markdown('</div>',unsafe_allow_html=True)
        report=f"""FUTURE LIFE SIMULATION REPORT
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Country: {user.get('country','India')}
SCORES — Academic:{s['academic']} Financial:{s['financial']} Career:{s['career']} Lifestyle:{s['lifestyle']}
Composite:{s['composite']} Risk:{s['risk']} Trend:{s['trend']}
PROJECTIONS
5yr:  ₹{sim['5_year']['income_lpa']} LPA | {sim['5_year']['career_status']} | {sim['5_year']['fin_status']}
10yr: ₹{sim['10_year']['income_lpa']} LPA | {sim['10_year']['career_status']} | {sim['10_year']['fin_status']}
25yr: ₹{sim['25_year']['income_lpa']} LPA | {sim['25_year']['career_status']} | {sim['25_year']['fin_status']}
{analysis}
---
Future Life Simulator v4.0"""
        st.download_button("📄 Download Report",report,
            file_name=f"fls_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",mime="text/plain")
    else:
        st.warning(analysis) if analysis.startswith("[") else None
        st.info("Add GEMINI_API_KEY to .env to enable analysis.")

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 💡 Personalised Action Plan")
    risk=s["risk"]
    if risk=="High": st.markdown('<div class="a-err">⚠️ <b>High Risk</b> — Immediate corrective action needed across multiple domains.</div>',unsafe_allow_html=True)
    elif risk=="Moderate": st.markdown('<div class="a-warn">⚡ <b>Moderate Risk</b> — Key improvements identified below.</div>',unsafe_allow_html=True)
    else: st.markdown('<div class="a-ok">✅ <b>Low Risk</b> — Solid trajectory. Amplify your strengths.</div>',unsafe_allow_html=True)
    st.markdown("<br/>",unsafe_allow_html=True)
    for icon,domain,score,action in [
        ("📚","Academic",s["academic"],_act_academic(s,user)),
        ("💰","Financial",s["financial"],_act_financial(s,user)),
        ("💼","Career",s["career"],_act_career(s,user)),
        ("🌱","Lifestyle",s["lifestyle"],_act_lifestyle(s,user)),
    ]:
        color=_sc(score)
        impact="HIGH IMPACT" if score<55 else "MEDIUM"
        st.markdown(f'''<div style="display:flex;gap:1rem;align-items:flex-start;
             background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
             border-radius:12px;padding:.95rem 1.2rem;margin:.5rem 0;">
          <div style="font-size:1.2rem;flex-shrink:0;padding-top:.1rem;">{icon}</div>
          <div style="flex:1;">
            <div style="display:flex;align-items:center;gap:.7rem;margin-bottom:.3rem;">
              <span style="font-family:JetBrains Mono,monospace;font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;color:#e8b84b;">{domain}</span>
              <div style="flex:1;height:3px;background:rgba(255,255,255,.05);border-radius:2px;">
                <div style="width:{int(score)}%;height:3px;background:{color};border-radius:2px;"></div>
              </div>
              <span style="font-family:JetBrains Mono,monospace;font-size:.68rem;color:{color};font-weight:600;">{score:.0f}/100</span>
            </div>
            <div style="font-size:.88rem;line-height:1.65;color:rgba(226,230,243,.8);">{action}</div>
          </div>
          <div style="font-family:JetBrains Mono,monospace;font-size:.6rem;color:{color};flex-shrink:0;letter-spacing:.1em;text-transform:uppercase;">{impact}</div>
        </div>''',unsafe_allow_html=True)

    analysis=st.session_state.llm_analysis
    if analysis and not analysis.startswith("["):
        with st.expander("📋 Gemini Priority Actions"):
            idx=analysis.lower().find("priority actions")
            st.markdown(analysis[idx:] if idx>=0 else analysis)

    st.markdown("---")
    st.markdown(f'''<div class="card" style="font-size:.87rem;color:rgba(226,230,243,.55);line-height:1.85;">
      <strong style="color:#e8b84b;">The Compound Effect</strong> — Every projection is based on your current trajectory.
      A 1% daily improvement in your weakest domain compounds to 37× over one year.
      <br/><br/>
      <span style="font-family:JetBrains Mono,monospace;font-size:.66rem;color:rgba(232,184,75,.4);">
      COMPOSITE {s["composite"]:.0f}/100 · RISK {s["risk"].upper()} · TREND {s["trend"].upper()} · {user.get("country","India").upper()}
      </span>
    </div>''',unsafe_allow_html=True)