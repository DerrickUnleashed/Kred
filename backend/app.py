import os, io, json, datetime, random, base64, logging
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from stock_service import (
    get_market_summary,
    get_movers,
    get_sector_performance,
    get_stock_info,
    get_historical_data,
    calculate_indicators,
    cache,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
log = logging.getLogger("kred")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="KRED API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════════
#  STOCK API MODELS
# ══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    risk_profile: str = "Moderate"


SYSTEM_PROMPT = """You are KRED AI, a friendly Indian stock market expert who explains finance 
in super simple language that even a complete beginner can understand.

CORE RULES:
1. Always use simple analogies — compare market trends to WEATHER (sunny/stormy),
   RSI to a CAR SPEEDOMETER (going too fast = overbought), volatility to ROAD CONDITIONS 
   (bumpy road = high risk), MACD to a TRAIN (momentum/direction).
2. Use ₹ for prices. Reference Indian context (NSE, BSE, SEBI, FD rates, SIP).
3. Never recommend "buy/sell" — say "worth watching", "looks interesting", "be cautious".
4. Tailor advice to the user's risk profile: conservative (FD mindset), moderate, aggressive.
5. End every market insight with one actionable suggestion.
6. Keep responses under 250 words unless asked for detail.
7. Use emojis sparingly to highlight key points.

Risk profiles:
- Conservative: prioritise capital safety, dividends, blue chips
- Moderate: balanced growth + safety, diversified sectors  
- Aggressive: growth stocks, momentum plays, higher tolerance for dips"""


def get_groq_llm():
    try:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        return Groq(api_key=api_key)
    except ImportError:
        return None


# ══════════════════════════════════════════════════════════════════════════════
#  FSVE - FUTURE STATE VARIABLE ENGINE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class UserProfile(BaseModel):
    name:          str             = Field("", json_schema_extra={"example": "Priya Sharma"})
    occupation:    str             = Field("", json_schema_extra={"example": "2nd Year B.Tech Student"})
    bio:           str             = Field("", json_schema_extra={"example": "Aspiring ML engineer from Chennai"})
    country:       str             = Field("India", json_schema_extra={"example": "India"})
    age:           int             = Field(20, ge=10, le=70)
    gender:        str             = Field("Prefer not to say")

    edu_level:     str             = Field("Undergraduate")
    cgpa:          float           = Field(7.5, ge=0.0, le=10.0)
    field:         str             = Field("Engineering / Technology")
    college_tier:  str             = Field("Tier 2")
    study_hours:   int             = Field(20, ge=0, le=80)

    target_career: str             = Field("Software Engineer")
    skill:         str             = Field("Intermediate")
    experience:    bool            = Field(False)
    consistency:   str             = Field("Medium")

    monthly_spend: float           = Field(8000.0, ge=0)
    savings:       str             = Field("Medium")
    family_bg:     str             = Field("Middle")
    discipline:    str             = Field("Balanced")

    screen_time:   str             = Field("Medium (4–8 h)")
    health:        str             = Field("Average")
    sleep:         str             = Field("Average")


class ScoresResponse(BaseModel):
    academic:   float
    financial:  float
    career:     float
    lifestyle:  float
    composite:  float
    risk:       str
    profile:    str
    trend:      str


class HorizonProjection(BaseModel):
    years:          int
    age:            int
    academic:       float
    financial:      float
    career:         float
    lifestyle:      float
    composite:      float
    career_status:  str
    fin_status:     str
    life_quality:   str
    income_lpa:     float


class SimulationResponse(BaseModel):
    scores:      ScoresResponse
    projections: dict[str, HorizonProjection]


class AnalysisRequest(BaseModel):
    profile:    UserProfile
    simulation: SimulationResponse


class NarrativeResponse(BaseModel):
    narrative: str


class AnalysisResponse(BaseModel):
    analysis: str


class ImageResponse(BaseModel):
    image_b64:   str
    flux_prompt: str
    saved_path:  Optional[str] = None
    source:      str


class FullRunResponse(BaseModel):
    simulation:  SimulationResponse
    analysis:    str
    narrative:   str
    image_b64:   str
    flux_prompt: str
    saved_path:  Optional[str] = None
    image_source: str


# ══════════════════════════════════════════════════════════════════════════════
#  FSVE SCORING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def _score_academic(u: UserProfile) -> float:
    cgpa_n  = (u.cgpa / 4.0 if u.cgpa <= 4.0 else u.cgpa / 10.0) * 100
    study_s = min(u.study_hours / 42.0 * 100, 100)
    tier_s  = {"Tier 1": 95, "Tier 2": 65, "Tier 3": 38}[u.college_tier]
    lvl_m   = {"High School": .80, "Undergraduate": 1.0,
               "Postgraduate": 1.15, "PhD": 1.25}[u.edu_level]
    return round(min((cgpa_n * .50 + study_s * .30 + tier_s * .20) * lvl_m, 100), 1)


def _score_financial(u: UserProfile) -> float:
    sv = {"Low": 28, "Medium": 62, "High": 92}[u.savings]
    di = {"Impulsive": 22, "Balanced": 58, "Disciplined": 94}[u.discipline]
    fa = {"Low": 38, "Middle": 65, "High": 88}[u.family_bg]
    sp = max(0, 100 - u.monthly_spend / 500.0)
    return round(min(sv * .35 + di * .35 + fa * .20 + sp * .10, 100), 1)


def _score_career(u: UserProfile) -> float:
    sk = {"Beginner": 38, "Intermediate": 68, "Advanced": 94}[u.skill]
    ex = 88 if u.experience else 48
    co = {"Low": 32, "Medium": 62, "High": 92}[u.consistency]
    return round(min(sk * .40 + ex * .35 + co * .25, 100), 1)


def _score_lifestyle(u: UserProfile) -> float:
    sk = u.screen_time.split()[0]
    sc = {"Low": 88, "Medium": 58, "High": 28}.get(sk, 55)
    hc = {"Poor": 28, "Average": 58, "Good": 92}[u.health]
    sl = {"Poor": 32, "Average": 62, "Good": 92}[u.sleep]
    return round(min(hc * .38 + sl * .38 + sc * .24, 100), 1)


def compute_scores(u: UserProfile) -> ScoresResponse:
    ac = _score_academic(u)
    fi = _score_financial(u)
    ca = _score_career(u)
    li = _score_lifestyle(u)
    co = round(ac * .30 + fi * .25 + ca * .25 + li * .20, 1)
    risk    = "Low"    if co > 74 else ("Moderate" if co >= 50 else "High")
    profile = "Disciplined" if co > 74 else ("Balanced" if co >= 50 else "At Risk")
    trend   = ("Improving" if ac > 68 and ca > 68 else
               "Declining" if ac < 48 or ca < 48 else "Stable")
    return ScoresResponse(
        academic=ac, financial=fi, career=ca, lifestyle=li,
        composite=co, risk=risk, profile=profile, trend=trend,
    )


def run_simulation(u: UserProfile, s: ScoresResponse) -> dict[str, HorizonProjection]:
    r_map = {"Improving": .026, "Stable": .005, "Declining": -.022}
    r = r_map[s.trend]
    income_base = {
        "Engineering / Technology": 7, "Science": 5, "Commerce / Business": 5.5,
        "Arts / Humanities": 3,         "Medicine / Healthcare": 8,
        "Law": 5.5,                     "Other": 4,
    }.get(u.field, 4.5)
    sm = {"Beginner": .7, "Intermediate": 1.0, "Advanced": 1.35}[u.skill]
    tm = {"Tier 1": 1.3,  "Tier 2": 1.0,       "Tier 3": .75}[u.college_tier]

    def lbl(v: float, ls: list) -> str:
        return ls[min(int(v / 20), len(ls) - 1)]

    out: dict[str, HorizonProjection] = {}
    for yrs, key in [(5, "5_year"), (10, "10_year"), (25, "25_year")]:
        proj = {
            d: round(min(100, max(0, getattr(s, d) * ((1 + r) ** yrs))), 1)
            for d in ("academic", "financial", "career", "lifestyle")
        }
        co     = round(proj["academic"]*.30 + proj["financial"]*.25 +
                       proj["career"]*.25   + proj["lifestyle"]*.20, 1)
        income = round(income_base * sm * tm * (1.085 ** yrs) * (co / 65.0), 1)
        out[key] = HorizonProjection(
            years=yrs, age=u.age + yrs, **proj, composite=co,
            career_status=lbl(proj["career"],   ["Unstable","Emerging","Stable","Strong","Elite"]),
            fin_status   =lbl(proj["financial"], ["Struggling","Tight","Moderate","Comfortable","Wealthy"]),
            life_quality =lbl(proj["lifestyle"], ["Poor","Below Avg","Average","Good","Excellent"]),
            income_lpa=income,
        )
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  FSVE LLM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

def _build_analysis_prompt(u: UserProfile, s: ScoresResponse,
                            sim: dict[str, HorizonProjection]) -> str:
    name = u.name or "the student"
    p5   = sim["5_year"];  p10 = sim["10_year"];  p25 = sim["25_year"]
    return f"""You are a behavioural scientist and life-trajectory expert.

PERSONAL PROFILE:
Name: {name} | Age: {u.age} | Gender: {u.gender}
Country: {u.country} | Role: {u.occupation} | Bio: {u.bio}

ACADEMIC: {u.edu_level} in {u.field} | {u.college_tier} | CGPA {u.cgpa} | {u.study_hours} hrs/wk
CAREER: Target: {u.target_career} | Skill: {u.skill} | Experience: {u.experience} | Consistency: {u.consistency}
FINANCIAL: ₹{u.monthly_spend}/mo | Savings: {u.savings} | Family: {u.family_bg} | Discipline: {u.discipline}
LIFESTYLE: Screen: {u.screen_time} | Health: {u.health} | Sleep: {u.sleep}

SCORES: Academic {s.academic} | Financial {s.financial} | Career {s.career} | Lifestyle {s.lifestyle}
Composite {s.composite} | Risk: {s.risk} | Trend: {s.trend}

PROJECTIONS:
5yr  → {p5.career_status} | {p5.fin_status} | ₹{p5.income_lpa} LPA (Age {p5.age})
10yr → {p10.career_status} | {p10.fin_status} | ₹{p10.income_lpa} LPA (Age {p10.age})
25yr → {p25.career_status} | {p25.fin_status} | ₹{p25.income_lpa} LPA (Age {p25.age})

Address {name} directly. Be honest, warm, and precise.

**CURRENT STATE**
3–4 sentences addressing {name} directly. Honest, specific, compassionate.

**10-YEAR VISION**
Vivid paragraph: {name}'s life in {u.country} at age {p10.age}. Home, desk, morning, city, emotions.

**25-YEAR OUTLOOK**
One paragraph: retirement readiness, health, legacy, life satisfaction.

**KEY RISKS**
3–5 specific, data-referenced bullet points.

**TOP STRENGTHS**
2–3 bullet points with genuine competitive advantages.

**PRIORITY ACTIONS — 5 Steps for {name}**
5 numbered, concrete, measurable, personalised steps.

Be brutally honest yet kind. Country context: {u.country}."""


def _build_narrative_prompt(u: UserProfile, s: ScoresResponse,
                             d: HorizonProjection) -> str:
    name = u.name or "this person"
    return f"""Describe the PHYSICAL ENVIRONMENT and DAILY LIFE of {name} 10 years from now in {u.country}.

Scores → Academic:{s.academic} Financial:{s.financial} Career:{s.career} Lifestyle:{s.lifestyle}
Outcome → Career:{d.career_status} Finance:{d.fin_status} Quality:{d.life_quality}
Income: ₹{d.income_lpa} LPA | Age: {d.age} | Field: {u.field} | Country: {u.country}

Write ONE vivid, sensory paragraph (6–8 sentences):
• Their home/room — specific objects, lighting, city visible outside
• Their desk and work setup — screen content, equipment quality
• Clothing and physical appearance — energy, posture, well-dressed or dishevelled
• One specific activity they are doing at this moment
• The emotional atmosphere — confidence, stress, contentment, struggle

No advice. Cinematic, grounded in the scores."""


def build_flux_prompt(u: UserProfile, s: ScoresResponse,
                      sim: dict[str, HorizonProjection]) -> str:
    d   = sim["10_year"]
    fin = d.fin_status;  car = d.career_status;  lif = d.life_quality

    wealth_env = {
        "Wealthy":     "ultra-luxury penthouse interior, floor-to-ceiling windows with panoramic city skyline, polished marble floors, designer furniture, minimalist luxury",
        "Comfortable": "modern apartment interior, large windows with city view, hardwood floors, quality contemporary furniture, well-lit",
        "Moderate":    "standard apartment interior, laminate flooring, functional furniture, typical urban living space",
        "Tight":       "small room interior, basic furniture, simple desk, modest living space",
        "Struggling":  "sparse room interior, worn furniture, minimal possessions, humble living environment",
    }.get(fin, "apartment interior with standard furniture")

    career_ctx = {
        "Elite":    "high-end professional workspace with multiple large displays",
        "Strong":   "professional workspace with dual monitors, organized desk",
        "Stable":   "standard workspace with monitor, typical office setup",
        "Emerging": "simple workspace with laptop, basic setup",
        "Unstable": "makeshift workspace with laptop",
    }.get(car, "desk workspace")

    life_ctx = {
        "Excellent": "bright natural light, healthy plants, organized and serene space",
        "Good":      "clean organized space, natural lighting",
        "Average":   "lived-in space, moderate tidiness",
        "Below Avg": "slightly cluttered, dim lighting",
        "Poor":      "disorganized, poor lighting",
    }.get(lif, "functional space")

    country_ctx = {
        "India":          "Indian apartment interior, typical Indian urban setting",
        "United States":  "American apartment interior, US urban view",
        "United Kingdom": "UK flat interior, British architecture",
        "Canada":         "Canadian apartment interior, North American style",
        "Australia":      "Australian apartment interior, coastal bright light",
        "Germany":        "German apartment interior, Bauhaus European style",
        "Singapore":      "Singapore apartment interior, tropical city skyline",
        "UAE":            "Dubai apartment interior, modern Arabic contemporary design",
        "France":         "French apartment interior, Haussmann-style architecture",
        "Japan":          "Japanese apartment interior, minimalist Zen design",
        "South Korea":    "Korean apartment interior, modern Seoul city view",
        "Netherlands":    "Dutch apartment interior, canal-side European setting",
        "Sweden":         "Swedish apartment interior, Scandinavian minimalist design",
    }.get(u.country, f"{u.country} apartment interior")

    light = {
        "Excellent": "golden hour sunlight streaming through windows",
        "Good":      "bright morning natural light",
        "Average":   "neutral afternoon daylight",
        "Below Avg": "evening lamp light, curtains partially drawn",
        "Poor":      "harsh artificial overhead light, windows dark",
    }.get(lif, "natural ambient daylight")

    return (
        f"REAL PHOTOGRAPH. Interior lifestyle scene. {wealth_env}. "
        f"{career_ctx}. {country_ctx}. {light}. {life_ctx}. "
        f"Style: Editorial interior photography. Shot on Hasselblad medium format camera. "
        f"50mm lens. Natural ambient light. Shallow depth of field. "
        f"Architectural Digest magazine quality. Photorealistic. "
        f"Hyper-detailed textures. Realistic materials. Natural reflections. "
        f"Cinematic composition. Professional real estate photography. "
        f"CRITICAL: NO text. NO words. NO letters. NO numbers. NO people. "
        f"NO human figures. NO faces. NO watermarks. NO logos. NO signs. "
        f"NO labels. NO CGI. NO 3D render. NO illustration. NO cartoon. "
        f"NO animation. NO stylized elements. NO AI artifacts. NO pixelation."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FLUX IMAGE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

_hf_client = None

def get_hf_client():
    global _hf_client
    if _hf_client is None:
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        if token:
            try:
                from huggingface_hub import InferenceClient
                _hf_client = InferenceClient(token=token)
                log.info("HuggingFace InferenceClient initialised")
            except Exception as e:
                log.warning(f"HF client init failed: {e}")
    return _hf_client


def generate_flux_image(prompt: str):
    from PIL import Image
    client = get_hf_client()
    if not client:
        return None, "no_hf_token"
    enhanced = (
        prompt
        + " IMPORTANT: This is a REAL PHOTOGRAPH taken with a professional camera. "
          "The image must look exactly like a high-end architectural photography spread. "
          "No text anywhere. No artificial elements. Pure realism."
    )
    try:
        result = client.text_to_image(
            prompt=enhanced,
            model="black-forest-labs/FLUX.1-schnell",
            width=1024,
            height=768,
        )
        img = result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
        w, h = img.size
        img  = img.crop((0, 0, w, int(h * 0.92)))
        img  = img.resize((1024, 768), Image.Resampling.LANCZOS)
        log.info("FLUX image generated successfully")
        return img, "flux"
    except Exception as e:
        log.error(f"FLUX generation error: {e}")
        return None, f"flux_error:{e}"


# ══════════════════════════════════════════════════════════════════════════════
#  PIL FALLBACK SCENE
# ══════════════════════════════════════════════════════════════════════════════

def make_fallback_image(u: UserProfile, s: ScoresResponse,
                        sim: dict[str, HorizonProjection]):
    from PIL import Image, ImageDraw
    import numpy as np
    
    W, H  = 1024, 768
    d     = sim["10_year"]
    fin_r = {"Struggling":0,"Tight":1,"Moderate":2,"Comfortable":3,"Wealthy":4}.get(d.fin_status, 2)
    car_r = {"Unstable":0,"Emerging":1,"Stable":2,"Strong":3,"Elite":4}.get(d.career_status, 2)
    lif_r = {"Poor":0,"Below Avg":1,"Average":2,"Good":3,"Excellent":4}.get(d.life_quality, 2)
    rng   = random.Random(int(d.composite * 100 + d.age * 333))

    skies = {
        4:[(4,7,20),(12,18,46)],  3:[(7,13,30),(17,25,52)],
        2:[(13,17,36),(23,29,50)], 1:[(17,17,28),(27,25,38)],
        0:[(19,13,13),(29,19,17)],
    }
    c1, c2 = skies.get(fin_r, skies[2])

    canvas = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(canvas)

    for y in range(H):
        t = y / H
        draw.line([(0,y),(W,y)], fill=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3)))

    if fin_r >= 3:
        for _ in range(rng.randint(28, 52)):
            sx, sy = rng.randint(0,W), rng.randint(0,int(H*.36))
            br = rng.randint(120, 228)
            draw.ellipse([sx-1,sy-1,sx+1,sy+1], fill=(br,br,min(255,br+28)))

    sky_y = int(H * .52)
    if fin_r >= 1:
        for _ in range(4 + fin_r*3):
            bx = rng.randint(-40, W+40)
            bh = rng.randint(int(50+fin_r*26), int(105+fin_r*52))
            bw = rng.randint(20, 42+fin_r*8)
            bc = tuple(int(c1[i]+rng.randint(5,22)) for i in range(3))
            draw.rectangle([bx, sky_y-bh, bx+bw, sky_y+3], fill=bc)

    floor_y = int(H * .62)
    wc_map  = {4:(26,22,42),3:(34,38,52),2:(42,42,56),1:(50,46,44),0:(56,48,40)}
    wc = wc_map.get(fin_r,(42,42,56))
    for y in range(int(H*.30), floor_y+5):
        t = (y-int(H*.30))/(floor_y-int(H*.30))
        draw.line([(0,y),(W,y)], fill=tuple(max(0,int(wc[i]-11*t)) for i in range(3)))

    fc_map = {4:(50,42,32),3:(56,48,38),2:(63,56,46),1:(70,62,52),0:(76,68,58)}
    fc = fc_map.get(fin_r, (63,56,46))
    for y in range(floor_y, H):
        t = (y-floor_y)/(H-floor_y)
        draw.line([(0,y),(W,y)], fill=tuple(max(0,int(fc[i]-16*t)) for i in range(3)))

    n_win = max(1, fin_r+1); win_w=85+fin_r*22; win_h=82+fin_r*18
    win_y = int(H*.33); spacing=W//(n_win+1)
    for wi in range(n_win):
        wx = spacing*(wi+1)-win_w//2
        fr = (170,150,115) if fin_r>=3 else (98,90,78) if fin_r>=2 else (64,58,50)
        draw.rectangle([wx-4,win_y-4,wx+win_w+4,win_y+win_h+4], fill=fr)
        for wy2 in range(win_h):
            t = wy2/win_h
            sc = tuple(int(c1[i]*(1-t)+max(0,c1[i]-14)*t) for i in range(3))
            draw.line([(wx,win_y+wy2),(wx+win_w,win_y+wy2)], fill=sc)
        draw.line([(wx+win_w//2,win_y),(wx+win_w//2,win_y+win_h)], fill=fr, width=2)

    dx=int(W*.06); dy=floor_y-15; dw=int(W*.88); dd=18
    desk_c = {4:(66,48,26),3:(56,42,25),2:(72,62,44),1:(78,68,52),0:(86,76,60)}.get(fin_r,(72,62,44))
    draw.rectangle([dx,dy,dx+dw,dy+dd], fill=desk_c)

    mon_n = 1 if car_r<=1 else 2 if car_r<=3 else 3
    if mon_n==1:   mon_xs=[dx+dw//2-70]
    elif mon_n==2: mon_xs=[dx+50, dx+dw//2+22]
    else:          mon_xs=[dx+16, dx+dw//2-68, dx+dw-192]
    mw=128+car_r*13; mh=86+car_r*10; my=int(H*.23)-mh
    for mpx in mon_xs:
        bez=(10,10,16) if car_r>=3 else (20,18,14)
        draw.rectangle([mpx-6,my-6,mpx+mw+6,my+mh+6], fill=bez)
        draw.rectangle([mpx,my,mpx+mw,my+mh], fill=(4,8,22) if car_r>=3 else (9,13,26))
        acc=(125,170,250) if fin_r>=2 else (90,120,190)
        for li in range(7):
            lw=rng.randint(int(mw*.2),int(mw*.8))
            draw.line([(mpx+5,my+8+li*11),(mpx+5+lw,my+8+li*11)], fill=acc, width=1)

    arr = np.array(canvas)
    bar_h = 85
    arr[H-bar_h:] = np.clip(arr[H-bar_h:]*0.2+np.array([4,4,12])*0.8,0,255).astype(np.uint8)
    canvas = Image.fromarray(arr)

    noise_arr = np.array(canvas).astype(np.float32)
    canvas = Image.fromarray(
        np.clip(noise_arr + np.random.normal(0,4,noise_arr.shape),0,255).astype(np.uint8)
    )
    return canvas


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def pil_to_b64(img) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def save_outputs(img, u: UserProfile, s: ScoresResponse,
                 sim: dict[str, HorizonProjection],
                 flux_prompt: str, analysis: str) -> str:
    from PIL import Image
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = (u.name or "user").replace(" ","_").lower()[:20]
    img_path = OUTPUT_DIR / f"{slug}_{ts}.png"
    img.save(img_path)
    meta = {
        "timestamp": ts,
        "name": u.name, "age": u.age, "country": u.country,
        "scores": s.model_dump(),
        "10yr": sim["10_year"].model_dump(),
        "flux_prompt": flux_prompt,
        "analysis_excerpt": analysis[:400] if analysis else "",
    }
    with open(OUTPUT_DIR / f"{slug}_{ts}_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    log.info(f"Saved output → {img_path}")
    return str(img_path)


COUNTRIES = [
    "India","United States","United Kingdom","Canada","Australia",
    "Germany","France","Singapore","UAE","Netherlands","Sweden",
    "Japan","South Korea","New Zealand","Ireland","Switzerland",
    "Malaysia","Bangladesh","Sri Lanka","Nepal","Pakistan",
    "South Africa","Nigeria","Kenya","Brazil","Mexico",
    "Italy","Spain","Portugal","Poland","Other",
]


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES - STOCK API
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {"status": "ok", "message": "KRED API is running", "version": "2.0.0"}


@app.get("/api/market/summary")
def market_summary():
    return get_market_summary()


@app.get("/api/market/movers")
def market_movers():
    return get_movers()


@app.get("/api/market/sectors")
def sector_performance():
    return get_sector_performance()


@app.get("/api/stock/{symbol}")
def stock_info(symbol: str):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    info = get_stock_info(symbol)
    if not info:
        raise HTTPException(status_code=404, detail="Stock not found")
    return info


@app.get("/api/stock/{symbol}/history")
def stock_history(symbol: str, period: str = "1mo"):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    return get_historical_data(symbol, period)


@app.get("/api/stock/{symbol}/indicators")
def stock_indicators(symbol: str):
    if not symbol.endswith(".NS"):
        symbol = f"{symbol}.NS"
    return calculate_indicators(symbol)


@app.post("/api/chat")
def chat(request: ChatRequest):
    client = get_groq_llm()
    
    if not client:
        return {
            "response": "AI chat is currently unavailable. Please ensure GROQ_API_KEY is configured.",
            "error": "API_KEY_MISSING"
        }
    
    try:
        market_summary_data = get_market_summary()
        sector_data = get_sector_performance()
        movers_data = get_movers()
        
        market_context = f"""
Current Market Data:
- NIFTY 50: {market_summary_data.get('NIFTY 50', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY 50', {}).get('pct', 0):+.2f}%)
- BSE SENSEX: {market_summary_data.get('BSE SENSEX', {}).get('value', 'N/A')} ({market_summary_data.get('BSE SENSEX', {}).get('pct', 0):+.2f}%)
- NIFTY BANK: {market_summary_data.get('NIFTY BANK', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY BANK', {}).get('pct', 0):+.2f}%)

Sector Performance: {', '.join([f'{k}: {v:+.2f}%' for k, v in sector_data.items()])}

Top Gainers: {', '.join([f"{g['symbol']}: +{g['change']}%" for g in movers_data.get('gainers', [])[:3]])}
Top Losers: {', '.join([f"{l['symbol']}: {l['change']}%" for l in movers_data.get('losers', [])[:3]])}
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + f"\n\nCurrent market context:\n{market_context}\nUser risk profile: {request.risk_profile}"}
        ]
        
        for msg in request.history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=500,
        )
        
        return {"response": response.choices[0].message.content}
    
    except Exception as e:
        return {"response": f"I encountered an error: {str(e)}", "error": "CHAT_ERROR"}


@app.post("/api/chat/insight")
def market_insight(risk_profile: str = "Moderate"):
    client = get_groq_llm()
    
    if not client:
        return {
            "response": "AI insights are currently unavailable. Please ensure GROQ_API_KEY is configured.",
            "error": "API_KEY_MISSING"
        }
    
    try:
        market_summary_data = get_market_summary()
        sector_data = get_sector_performance()
        movers_data = get_movers()
        
        market_context = f"""
Current Market Data:
- NIFTY 50: {market_summary_data.get('NIFTY 50', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY 50', {}).get('pct', 0):+.2f}%)
- BSE SENSEX: {market_summary_data.get('BSE SENSEX', {}).get('value', 'N/A')} ({market_summary_data.get('BSE SENSEX', {}).get('pct', 0):+.2f}%)
- NIFTY BANK: {market_summary_data.get('NIFTY BANK', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY BANK', {}).get('pct', 0):+.2f}%)
- NIFTY IT: {market_summary_data.get('NIFTY IT', {}).get('value', 'N/A')} ({market_summary_data.get('NIFTY IT', {}).get('pct', 0):+.2f}%)

Sector Performance: {', '.join([f'{k}: {v:+.2f}%' for k, v in sector_data.items()])}

Top Gainers: {', '.join([f"{g['symbol']}: +{g['change']}%" for g in movers_data.get('gainers', [])[:5]])}
Top Losers: {', '.join([f"{l['symbol']}: {l['change']}%" for l in movers_data.get('losers', [])[:5]])}
"""
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"User's risk profile: {risk_profile}\n\nCurrent market snapshot:\n{market_context}\n\nGive a clear, beginner-friendly market overview using simple analogies. Highlight 2-3 sectors worth watching and end with one actionable tip."}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
            max_tokens=600,
        )
        
        return {"response": response.choices[0].message.content}
    
    except Exception as e:
        return {"response": f"I encountered an error: {str(e)}", "error": "INSIGHT_ERROR"}


@app.post("/api/cache/clear")
def clear_cache():
    cache.clear()
    return {"message": "Cache cleared successfully"}


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES - FSVE (Future State Variable Engine)
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/fls/health", tags=["FSVE"])
async def fls_health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
        "flux_configured": bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")),
        "output_dir": str(OUTPUT_DIR.resolve()),
    }


@app.get("/api/fls/countries", tags=["FSVE"])
async def get_countries():
    return {"countries": COUNTRIES}


@app.post("/api/fls/simulate", response_model=SimulationResponse, tags=["FSVE"])
async def simulate_endpoint(profile: UserProfile):
    try:
        s   = compute_scores(profile)
        sim = run_simulation(profile, s)
        log.info(f"Simulate: {profile.name or 'anon'} composite={s.composite} risk={s.risk}")
        return SimulationResponse(scores=s, projections=sim)
    except Exception as e:
        log.error(f"Simulate error: {e}")
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/fls/analyze", response_model=AnalysisResponse, tags=["FSVE"])
async def analyze_endpoint(req: AnalysisRequest):
    try:
        s   = req.simulation.scores
        sim = req.simulation.projections
        
        client = get_groq_llm()
        if not client:
            return AnalysisResponse(analysis="AI analysis unavailable. GROQ_API_KEY not configured.")
        
        prompt = _build_analysis_prompt(req.profile, s, sim)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.72,
            max_tokens=2048,
        )
        analysis = completion.choices[0].message.content or "[Empty response]"
        log.info(f"Analysis done for: {req.profile.name or 'anon'}")
        return AnalysisResponse(analysis=analysis)
    except Exception as e:
        log.error(f"Analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fls/narrative", response_model=NarrativeResponse, tags=["FSVE"])
async def narrative_endpoint(req: AnalysisRequest):
    try:
        s   = req.simulation.scores
        sim = req.simulation.projections
        
        client = get_groq_llm()
        if not client:
            return NarrativeResponse(narrative="AI narrative unavailable. GROQ_API_KEY not configured.")
        
        prompt = _build_narrative_prompt(req.profile, s, sim["10_year"])
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.88,
            max_tokens=512,
        )
        narrative = completion.choices[0].message.content or "[Empty response]"
        return NarrativeResponse(narrative=narrative)
    except Exception as e:
        log.error(f"Narrative error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fls/generate-image", response_model=ImageResponse, tags=["FSVE"])
async def generate_image_endpoint(req: AnalysisRequest, background_tasks: BackgroundTasks):
    try:
        from PIL import Image
        s   = req.simulation.scores
        sim = req.simulation.projections
        flux_prompt = build_flux_prompt(req.profile, s, sim)

        img, source = generate_flux_image(flux_prompt)
        if img is None:
            img    = make_fallback_image(req.profile, s, sim)
            source = "fallback"

        b64  = pil_to_b64(img)
        path = None

        def _save():
            nonlocal path
            path = save_outputs(img, req.profile, s, sim, flux_prompt, "")
        background_tasks.add_task(_save)

        log.info(f"Image generated via {source} for {req.profile.name or 'anon'}")
        return ImageResponse(image_b64=b64, flux_prompt=flux_prompt,
                             saved_path=path, source=source)
    except Exception as e:
        log.error(f"Generate-image error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fls/full-run", response_model=FullRunResponse, tags=["FSVE"])
async def full_run_endpoint(profile: UserProfile):
    from PIL import Image
    try:
        s   = compute_scores(profile)
        sim = run_simulation(profile, s)
        log.info(f"Full run: {profile.name or 'anon'} composite={s.composite}")

        client = get_groq_llm()
        
        analysis = "AI analysis unavailable."
        narrative = "AI narrative unavailable."
        
        if client:
            try:
                analysis_prompt = _build_analysis_prompt(profile, s, sim)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.72,
                    max_tokens=2048,
                )
                analysis = completion.choices[0].message.content or "[Empty response]"
            except Exception as e:
                log.error(f"Analysis error: {e}")

            try:
                narrative_prompt = _build_narrative_prompt(profile, s, sim["10_year"])
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": narrative_prompt}],
                    temperature=0.88,
                    max_tokens=512,
                )
                narrative = completion.choices[0].message.content or "[Empty response]"
            except Exception as e:
                log.error(f"Narrative error: {e}")

        flux_prompt = build_flux_prompt(profile, s, sim)
        img, source = generate_flux_image(flux_prompt)
        if img is None:
            img    = make_fallback_image(profile, s, sim)
            source = "fallback"

        saved_path = save_outputs(img, profile, s, sim, flux_prompt, analysis)
        b64 = pil_to_b64(img)

        return FullRunResponse(
            simulation=SimulationResponse(scores=s, projections=sim),
            analysis=analysis,
            narrative=narrative,
            image_b64=b64,
            flux_prompt=flux_prompt,
            saved_path=saved_path,
            image_source=source,
        )

    except Exception as e:
        log.error(f"Full-run error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def on_startup():
    log.info("=== KRED API v2.0 starting ===")
    log.info(f"Output dir : {OUTPUT_DIR.resolve()}")
    log.info(f"Groq       : {'✓' if os.environ.get('GROQ_API_KEY') else '✗ (GROQ_API_KEY missing)'}")
    log.info(f"FLUX/HF    : {'✓' if (os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_TOKEN')) else '✗ (HF_TOKEN missing)'}")
    log.info("Docs available at http://0.0.0.0:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
