"""
engines/future_self_engine.py — Future Self Visualization Engine
================================================================
Orchestrates:
  1. Score computation   (pure Python, deterministic)
  2. Simulation          (compound growth projections)
  3. FLUX image gen      (HuggingFace Inference API, with fallback)
  4. LLM narrative       (ChatGroq / qwen3-32b via LangChain)

All logic from kred_future_self.py is preserved exactly.
Only the LLM layer (Gemini → ChatGroq) and structure are upgraded.
"""

from __future__ import annotations

import io
import random
import time
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..core.config import (
    GROQ_API_KEY, HF_TOKEN, GROQ_MODEL, FLUX_MODEL,
    LLM_TEMPERATURE, LLM_MAX_TOKENS,
    MAX_RETRIES, RETRY_DELAY_SECONDS,
    IMAGE_WIDTH, IMAGE_HEIGHT,
)
from ..utils.logger import get_logger
from ..utils.json_parser import extract_json
from ..utils.prompt_builder import (
    future_self_scenario_prompt,
    future_self_analysis_prompt,
)

log = get_logger("kred.engine.future_self")


# ══════════════════════════════════════════════════════════════════════════════
#  LLM CLIENT — ChatGroq via LangChain
# ══════════════════════════════════════════════════════════════════════════════

def _build_groq_llm():
    """Lazy-initialise ChatGroq. Returns None if key is missing."""
    if not GROQ_API_KEY:
        log.warning("GROQ_API_KEY not set — LLM features disabled.")
        return None
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model=GROQ_MODEL,
            api_key=GROQ_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        log.info("ChatGroq initialised with model: %s", GROQ_MODEL)
        return llm
    except Exception as exc:
        log.error("Failed to initialise ChatGroq: %s", exc)
        return None


def _build_hf_client():
    """Lazy-initialise HuggingFace InferenceClient. Returns None if unavailable."""
    if not HF_TOKEN:
        log.warning("HF_TOKEN not set — FLUX image generation disabled.")
        return None
    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=HF_TOKEN)
        log.info("HuggingFace InferenceClient initialised.")
        return client
    except Exception as exc:
        log.error("Failed to initialise HF InferenceClient: %s", exc)
        return None


def _llm_call_with_retry(llm: Any, prompt: str) -> str:
    """
    Calls the LangChain LLM with exponential back-off retry logic.
    Returns raw response text, or empty string on total failure.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            log.debug("LLM call succeeded on attempt %d", attempt)
            return text
        except Exception as exc:
            wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
            log.warning("LLM attempt %d/%d failed: %s — retrying in %.1fs",
                        attempt, MAX_RETRIES, exc, wait)
            if attempt < MAX_RETRIES:
                time.sleep(wait)
    log.error("LLM call failed after %d attempts.", MAX_RETRIES)
    return ""


# ══════════════════════════════════════════════════════════════════════════════
#  SCORING ENGINE  (preserved exactly from kred_future_self.py)
# ══════════════════════════════════════════════════════════════════════════════

def _score_academic(cgpa: float, study_hours: float, college_tier: str, edu_level: str) -> float:
    cgpa_n  = (cgpa / 4.0 if cgpa <= 4.0 else cgpa / 10.0) * 100
    study_s = min(study_hours / 42.0 * 100, 100)
    tier_s  = {"Tier 1": 95, "Tier 2": 65, "Tier 3": 38}[college_tier]
    lvl_m   = {"High School": .80, "Undergraduate": 1.0, "Postgraduate": 1.15, "PhD": 1.25}[edu_level]
    return round(min((cgpa_n * .50 + study_s * .30 + tier_s * .20) * lvl_m, 100), 1)


def _score_financial(monthly_spend: float, savings: str, family_bg: str, discipline: str) -> float:
    sv = {"Low": 28, "Medium": 62, "High": 92}[savings]
    di = {"Impulsive": 22, "Balanced": 58, "Disciplined": 94}[discipline]
    fa = {"Low": 38, "Middle": 65, "High": 88}[family_bg]
    sp = max(0, 100 - monthly_spend / 500.0)
    return round(min(sv * .35 + di * .35 + fa * .20 + sp * .10, 100), 1)


def _score_career(skill: str, experience: bool, consistency: str) -> float:
    sk = {"Beginner": 38, "Intermediate": 68, "Advanced": 94}[skill]
    ex = 88 if experience else 48
    co = {"Low": 32, "Medium": 62, "High": 92}[consistency]
    return round(min(sk * .40 + ex * .35 + co * .25, 100), 1)


def _score_lifestyle(screen_time: str, health: str, sleep: str) -> float:
    sk = screen_time.split()[0]
    sc = {"Low": 88, "Medium": 58, "High": 28}.get(sk, 55)
    hc = {"Poor": 28, "Average": 58, "Good": 92}[health]
    sl = {"Poor": 32, "Average": 62, "Good": 92}[sleep]
    return round(min(hc * .38 + sl * .38 + sc * .24, 100), 1)


def compute_scores(user: dict[str, Any]) -> dict[str, Any]:
    """Compute all domain scores + composite. Preserves original logic exactly."""
    ac = _score_academic(user["cgpa"], user["study_hours"], user["college_tier"], user["edu_level"])
    fi = _score_financial(user["monthly_spend"], user["savings"], user["family_bg"], user["discipline"])
    ca = _score_career(user["skill"], user["experience"], user["consistency"])
    li = _score_lifestyle(user["screen_time"], user["health"], user["sleep"])
    co = round(ac * .30 + fi * .25 + ca * .25 + li * .20, 1)
    risk    = "Low" if co > 74 else ("Moderate" if co >= 50 else "High")
    profile = "Disciplined" if co > 74 else ("Balanced" if co >= 50 else "At Risk")
    trend   = ("Improving" if ac > 68 and ca > 68 else
               "Declining" if ac < 48 or ca < 48 else "Stable")
    return dict(academic=ac, financial=fi, career=ca, lifestyle=li,
                composite=co, risk=risk, profile=profile, trend=trend)


def simulate(user: dict[str, Any], scores: dict[str, Any]) -> dict[str, Any]:
    """Project 5/10/25-year outcomes. Preserves original logic exactly."""
    r_map = {"Improving": .026, "Stable": .005, "Declining": -.022}
    r = r_map[scores["trend"]]
    income_base = {
        "Engineering / Technology": 7, "Science": 5, "Commerce / Business": 5.5,
        "Arts / Humanities": 3, "Medicine / Healthcare": 8, "Law": 5.5, "Other": 4,
    }.get(user["field"], 4.5)
    sm = {"Beginner": .7, "Intermediate": 1.0, "Advanced": 1.35}[user["skill"]]
    tm = {"Tier 1": 1.3, "Tier 2": 1.0, "Tier 3": .75}[user["college_tier"]]

    def _label(v: float, ls: list[str]) -> str:
        return ls[min(int(v / 20), len(ls) - 1)]

    out: dict[str, Any] = {}
    for yrs, key in [(5, "5_year"), (10, "10_year"), (25, "25_year")]:
        proj = {d: round(min(100, max(0, scores[d] * ((1 + r) ** yrs))), 1)
                for d in ("academic", "financial", "career", "lifestyle")}
        co     = round(proj["academic"]*.30 + proj["financial"]*.25 +
                       proj["career"]*.25 + proj["lifestyle"]*.20, 1)
        income = round(income_base * sm * tm * (1.085 ** yrs) * (co / 65.0), 1)
        out[key] = {
            "years": yrs, "age": user["age"] + yrs, **proj, "composite": co,
            "career_status": _label(proj["career"],   ["Unstable","Emerging","Stable","Strong","Elite"]),
            "fin_status":    _label(proj["financial"], ["Struggling","Tight","Moderate","Comfortable","Wealthy"]),
            "life_quality":  _label(proj["lifestyle"], ["Poor","Below Avg","Average","Good","Excellent"]),
            "income_lpa":    income,
        }
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  FLUX PROMPT BUILDER (preserved + enhanced)
# ══════════════════════════════════════════════════════════════════════════════

_WEALTH_DESC: dict[str, str] = {
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
        "basic bookshelf, one small plant, neat but modest"
    ),
    "Tight": (
        "small rented room or shared apartment, bare walls, compact desk near a window, "
        "single small monitor, minimal possessions, functional but sparse"
    ),
    "Struggling": (
        "cramped basic room, single dim window, old desk with aging laptop, "
        "cluttered and worn surfaces, few personal items"
    ),
}

_CAREER_DESC: dict[str, str] = {
    "Elite":    "evidence of senior leadership—executive reports, awards plaques, premium headphones",
    "Strong":   "a productive professional setup with industry publications and project documents visible",
    "Stable":   "a tidy organised mid-level workspace, notebooks and task lists on desk",
    "Emerging": "an entry-level setup with learning materials, tutorial windows open on screen",
    "Unstable": "a cluttered disorganised workspace, job listings visible on screen",
}

_LIFE_DESC: dict[str, str] = {
    "Excellent": "visible gym equipment nearby, fresh fruit bowl, green smoothie, premium water bottle, yoga mat",
    "Good":      "healthy snacks on desk, reusable water bottle, a few exercise items in background",
    "Average":   "standard desk snacks, regular water glass, no visible exercise items",
    "Below Avg": "junk food wrappers, energy drink cans, no health items visible",
    "Poor":      "junk food, overflowing bin, no healthy items, signs of sedentary lifestyle",
}

_COUNTRY_MAP: dict[str, dict[str, str]] = {
    "India": {
        "Wealthy":     "ultra-luxury apartment in Bandra West Mumbai or Koramangala Bangalore, floor-to-ceiling windows, Indian city skyline, premium imported furniture",
        "Comfortable": "modern flat in a Tier-1 Indian city — HSR Layout, Powai, or Gurgaon — stylish yet practical decor",
        "Moderate":    "standard Indian mid-range apartment in an urban locality, practical and functional interior",
        "Tight":       "small rented PG or 1BHK flat in an Indian city outskirts",
        "Struggling":  "basic shared accommodation in an Indian city",
    },
    "USA": {
        "Wealthy":     "luxury New York or San Francisco penthouse with skyline view, minimalist American luxury",
        "Comfortable": "spacious US apartment or suburban home office, American contemporary decor",
        "Moderate":    "standard US apartment, functional American interior",
        "Tight":       "small studio apartment in a US city",
        "Struggling":  "sparse basic room in an American city",
    },
    "UK": {
        "Wealthy":     "elegant London Kensington or Chelsea flat, classic British luxury interior",
        "Comfortable": "comfortable London zone-2 flat or house, British contemporary decor",
        "Moderate":    "standard UK flat, practical British interior",
        "Tight":       "small rented room in London or a UK city",
        "Struggling":  "sparse basic room in the UK",
    },
}

_TIME_LIGHT: dict[str, str] = {
    "Excellent": "warm golden morning light streaming through windows",
    "Good":      "bright morning natural light",
    "Average":   "neutral afternoon daylight",
    "Below Avg": "late evening with artificial lamp light, curtains closed",
    "Poor":      "harsh artificial overhead light at night, windows dark",
}


def build_flux_prompt(key: str, sim_data: dict[str, Any], user: dict[str, Any]) -> str:
    """
    Builds a rich, data-driven FLUX.1 prompt.
    All visual elements map to computed scores — nothing generic.
    Preserves original logic; enriched with stronger photography keywords.
    """
    fin_s   = sim_data["fin_status"]
    car_s   = sim_data["career_status"]
    lif_s   = sim_data["life_quality"]
    age     = sim_data["age"]
    income  = sim_data["income_lpa"]
    comp    = sim_data["composite"]
    country = user.get("country", "India")
    field   = user.get("field", "Engineering / Technology")

    wealth_desc  = _WEALTH_DESC.get(fin_s, _WEALTH_DESC["Moderate"])
    career_desc  = _CAREER_DESC.get(car_s, _CAREER_DESC["Stable"])
    life_desc    = _LIFE_DESC.get(lif_s, _LIFE_DESC["Average"])
    time_light   = _TIME_LIGHT.get(lif_s, "natural daylight")
    country_detail = (_COUNTRY_MAP.get(country, {}).get(fin_s)
                      or f"urban setting in {country} at a {fin_s.lower()} financial level")
    horizon_label = {"5_year": "5 years", "10_year": "10 years", "25_year": "25 years"}.get(key, "")

    return (
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


# ══════════════════════════════════════════════════════════════════════════════
#  FLUX IMAGE GENERATION
# ══════════════════════════════════════════════════════════════════════════════

def generate_flux_image(prompt: str, hf_client: Any) -> Image.Image | None:
    """
    Calls FLUX.1-schnell via HuggingFace InferenceClient.
    Returns PIL Image or None on failure. Includes retry logic.
    """
    if not hf_client:
        return None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info("FLUX generation attempt %d/%d", attempt, MAX_RETRIES)
            result = hf_client.text_to_image(prompt=prompt, model=FLUX_MODEL)
            img = result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
            log.info("FLUX image generated successfully.")
            return img
        except Exception as exc:
            wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
            log.warning("FLUX attempt %d failed: %s — retrying in %.1fs", attempt, exc, wait)
            if attempt < MAX_RETRIES:
                time.sleep(wait)
    log.error("FLUX generation failed after %d attempts — using fallback.", MAX_RETRIES)
    return None


def make_fallback_image(key: str, sim_data: dict[str, Any], scores: dict[str, Any], field: str) -> Image.Image:
    """
    PIL-based deterministic fallback image when FLUX is unavailable.
    Preserves all original pixel-art logic from kred_future_self.py exactly.
    """
    W, H = IMAGE_WIDTH, IMAGE_HEIGHT
    fin_s  = sim_data["fin_status"]
    car_s  = sim_data["career_status"]
    lif_s  = sim_data["life_quality"]
    comp   = sim_data["composite"]
    income = sim_data["income_lpa"]
    age    = sim_data["age"]

    fin_r = {"Struggling": 0, "Tight": 1, "Moderate": 2, "Comfortable": 3, "Wealthy": 4}.get(fin_s, 2)
    car_r = {"Unstable": 0, "Emerging": 1, "Stable": 2, "Strong": 3, "Elite": 4}.get(car_s, 2)
    lif_r = {"Poor": 0, "Below Avg": 1, "Average": 2, "Good": 3, "Excellent": 4}.get(lif_s, 2)
    rng   = random.Random(int(comp * 100 + sim_data["years"] * 777))

    skies = {
        4: [(5, 8, 22), (14, 20, 48)], 3: [(8, 14, 32), (18, 26, 54)],
        2: [(14, 18, 38), (24, 30, 52)], 1: [(18, 18, 30), (28, 26, 40)],
        0: [(20, 14, 14), (30, 20, 18)],
    }
    c1, c2 = skies.get(fin_r, skies[2])
    canvas = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(canvas)

    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    if fin_r >= 3:
        for _ in range(rng.randint(30, 55)):
            sx, sy = rng.randint(0, W), rng.randint(0, int(H * .38))
            br = rng.randint(130, 235)
            draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(br, br, min(255, br + 30)))

    sky_y = int(H * .50)
    if fin_r >= 1:
        for _ in range(4 + fin_r * 3):
            bx  = rng.randint(-40, W + 40)
            bh  = rng.randint(int(55 + fin_r * 28), int(110 + fin_r * 55))
            bw  = rng.randint(22, 44 + fin_r * 8)
            bc  = (int(c1[0] + rng.randint(5, 25)), int(c1[1] + rng.randint(5, 22)),
                   int(c1[2] + rng.randint(10, 35)))
            draw.rectangle([bx, sky_y - bh, bx + bw, sky_y + 3], fill=bc)
            for wr in range(max(1, bh // 16)):
                for wc in range(max(1, bw // 10)):
                    if rng.random() < .5:
                        wx = bx + 3 + wc * 10; wy = sky_y - bh + 5 + wr * 16
                        wb = rng.randint(155, 240)
                        draw.rectangle([wx, wy, wx + 6, wy + 10], fill=(wb, int(wb * .82), int(wb * .48)))

    floor_y = int(H * .60)
    wc_map  = {4: (28, 24, 44), 3: (36, 40, 54), 2: (44, 44, 58), 1: (52, 48, 46), 0: (58, 50, 42)}
    wc = wc_map.get(fin_r, (44, 44, 58))
    for y in range(int(H * .30), floor_y + 5):
        t  = (y - int(H * .30)) / (floor_y - int(H * .30))
        cc = tuple(max(0, int(wc[i] - 12 * t)) for i in range(3))
        draw.line([(0, y), (W, y)], fill=cc)

    fc_map = {4: (52, 44, 34), 3: (58, 50, 40), 2: (65, 58, 48), 1: (72, 64, 54), 0: (78, 70, 60)}
    fc = fc_map.get(fin_r, (65, 58, 48))
    for y in range(floor_y, H):
        t  = (y - floor_y) / (H - floor_y)
        cc = tuple(max(0, int(fc[i] - 18 * t)) for i in range(3))
        draw.line([(0, y), (W, y)], fill=cc)

    if fin_r >= 3:
        for rx in range(0, W, 3):
            sh = int(rng.uniform(.04, .14) * 255)
            draw.line([(rx, floor_y), (rx, floor_y + 5)], fill=(sh, sh, sh))

    n_win = max(1, fin_r + 1); win_w = 88 + fin_r * 22; win_h = 84 + fin_r * 18
    win_y = int(H * .33); spacing = W // (n_win + 1)
    for wi in range(n_win):
        wx = spacing * (wi + 1) - win_w // 2
        fr = (175, 155, 118) if fin_r >= 3 else (100, 92, 80) if fin_r >= 2 else (66, 60, 52)
        draw.rectangle([wx - 4, win_y - 4, wx + win_w + 4, win_y + win_h + 4], fill=fr)
        for wy2 in range(win_h):
            t  = wy2 / win_h
            sc = tuple(int(c1[i] * (1 - t) + max(0, c1[i] - 15) * t) for i in range(3))
            draw.line([(wx, win_y + wy2), (wx + win_w, win_y + wy2)], fill=sc)
        draw.line([(wx + win_w // 2, win_y), (wx + win_w // 2, win_y + win_h)], fill=fr, width=2)
        draw.line([(wx, win_y + win_h // 2), (wx + win_w, win_y + win_h // 2)], fill=fr, width=2)

    dx = int(W * .07); dy = floor_y - 14; dw = int(W * .86); dd = 18
    desk_c = {4: (68, 50, 28), 3: (58, 44, 26), 2: (74, 64, 46), 1: (80, 70, 54), 0: (88, 78, 62)}.get(fin_r, (74, 64, 46))
    draw.rectangle([dx, dy, dx + dw, dy + dd], fill=desk_c)
    draw.line([(dx, dy), (dx + dw, dy)], fill=tuple(min(255, c + 45) for c in desk_c), width=1)
    for lx in [dx + 12, dx + dw - 18]:
        draw.rectangle([lx, dy + dd, lx + 10, floor_y + 5], fill=tuple(max(0, c - 22) for c in desk_c))

    mon_n = 1 if car_r <= 1 else 2 if car_r <= 3 else 3
    if mon_n == 1:   mon_xs = [dx + dw // 2 - 75]
    elif mon_n == 2: mon_xs = [dx + 55, dx + dw // 2 + 25]
    else:            mon_xs = [dx + 18, dx + dw // 2 - 72, dx + dw - 198]

    mw = 130 + car_r * 14; mh = 88 + car_r * 10; my = int(H * .24) - mh
    for mpx in mon_xs:
        bez = (12, 12, 18) if car_r >= 3 else (22, 20, 16)
        draw.rectangle([mpx - 6, my - 6, mpx + mw + 6, my + mh + 6], fill=bez)
        draw.rectangle([mpx, my, mpx + mw, my + mh], fill=(5, 9, 24) if car_r >= 3 else (10, 14, 28))
        acc = (130, 175, 255) if fin_r >= 2 else (95, 125, 195)
        is_tech = any(x in field for x in ["Tech", "Eng", "Sci"])
        is_biz  = any(x in field for x in ["Comm", "Bus", "Law", "Med"])
        if is_tech:
            for li in range(7):
                lw = rng.randint(int(mw * .2), int(mw * .82))
                draw.line([(mpx + 5, my + 8 + li * 11), (mpx + 5 + lw, my + 8 + li * 11)],
                          fill=acc if rng.random() > .35 else (75, 98, 128), width=1)
        elif is_biz:
            bvs = [rng.randint(18, 68) for _ in range(5)]; bmax = max(bvs); bsp = (mw - 14) // 5
            for bi, bv in enumerate(bvs):
                bh2 = int(bv / bmax * (mh - 20)); bx2 = mpx + 7 + bi * bsp
                draw.rectangle([bx2, my + mh - 5 - bh2, bx2 + bsp - 3, my + mh - 5], fill=acc)
        else:
            for _ in range(14):
                ddx = mpx + rng.randint(4, mw - 4); ddy = my + rng.randint(4, mh - 4)
                draw.ellipse([ddx - 2, ddy - 2, ddx + 2, ddy + 2], fill=acc)
        sbx = mpx + mw // 2 - 7
        draw.rectangle([sbx, my + mh + 4, sbx + 14, dy + 2], fill=tuple(max(0, c - 30) for c in bez))
        draw.rectangle([sbx - 14, dy - 2, sbx + 28, dy + 3], fill=tuple(max(0, c - 22) for c in bez))

    # keyboard
    kbx = mon_xs[0] + (mw - 105) // 2; kby = dy - 20
    kbc = (28, 26, 22) if fin_r >= 3 else (48, 44, 38)
    draw.rectangle([kbx, kby, kbx + 105, kby + 14], fill=kbc, outline=(75, 72, 65), width=1)
    for kr in range(2):
        for kc2 in range(11):
            draw.rectangle([kbx + 3 + kc2 * 9, kby + 3 + kr * 5, kbx + 9 + kc2 * 9, kby + 6 + kr * 5],
                           fill=tuple(min(255, c + 22) for c in kbc))
    draw.ellipse([kbx + 116, kby - 1, kbx + 132, kby + 18], fill=kbc, outline=(85, 82, 75))

    if fin_r >= 2:
        plx = dx + 20; ply = dy
        draw.rectangle([plx, ply - 30, plx + 24, ply + 2], fill=(68, 42, 18))
        for _ in range(rng.randint(5, 8)):
            lx2 = plx + 12 + rng.randint(-34, 34); ly2 = ply - 30 + rng.randint(-38, 12)
            draw.ellipse([lx2 - 9, ly2 - 9, lx2 + 9, ly2 + 9], fill=(18, rng.randint(85, 138), 32))

    if fin_r >= 1:
        bkx = dx + dw - 165
        for _ in range(rng.randint(2, 4 + fin_r)):
            bw2 = rng.randint(13, 24); bh2 = rng.randint(38, 65 + fin_r * 8)
            draw.rectangle([bkx, dy - bh2, bkx + bw2, dy + 1],
                           fill=(rng.randint(80, 200), rng.randint(40, 120), rng.randint(40, 88)))
            bkx += bw2 + 3

    if fin_r >= 2:
        lpx = dx + dw - 48; lpc = (185, 170, 148) if fin_r >= 3 else (115, 108, 98)
        draw.rectangle([lpx, dy - 4, lpx + 16, dy + 2], fill=lpc)
        draw.line([(lpx + 8, dy - 4), (lpx + 8, dy - 50)], fill=lpc, width=3)
        shc = (255, 218, 95) if fin_r >= 3 else (215, 178, 78)
        draw.ellipse([lpx - 10, dy - 64, lpx + 26, dy - 44], fill=shc)

    if fin_r >= 3:
        rc = (65, 48, 95) if fin_r == 4 else (78, 58, 42)
        draw.rectangle([dx + 8, floor_y + 6, dx + dw - 8, floor_y + 38], fill=rc)
        draw.rectangle([dx + 14, floor_y + 10, dx + dw - 14, floor_y + 34],
                       outline=tuple(min(255, c + 44) for c in rc), width=1)

    mgx = dx + dw - 88; mgy = dy
    mgc = (175, 75, 38) if fin_r >= 3 else (135, 95, 58)
    draw.rectangle([mgx, mgy - 32, mgx + 24, mgy + 2], fill=mgc)
    draw.rectangle([mgx + 2, mgy - 30, mgx + 22, mgy - 8], fill=tuple(int(c * .6) for c in mgc))
    draw.arc([mgx + 24, mgy - 24, mgx + 34, mgy - 10], 270, 90, fill=mgc, width=3)

    arr     = np.array(canvas)
    bar_h   = 92; bar_region = arr[H - bar_h:]
    arr[H - bar_h:] = np.clip(bar_region * 0.18 + np.array([5, 5, 14]) * 0.82, 0, 255).astype(np.uint8)
    canvas  = Image.fromarray(arr); draw = ImageDraw.Draw(canvas)

    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        fb = fm = fs = ImageFont.load_default()

    sc      = (80, 200, 120) if comp >= 75 else (232, 184, 75) if comp >= 55 else (251, 146, 60) if comp >= 40 else (251, 113, 133)
    lbl_map = {"5_year": "5 YEARS", "10_year": "10 YEARS", "25_year": "25 YEARS"}
    draw.text((18, H - bar_h + 8),  lbl_map.get(key, ""), font=fb, fill=(232, 184, 75))
    draw.text((18, H - bar_h + 34), f"{car_s} Career  ·  {fin_s}  ·  {lif_s} Lifestyle", font=fm, fill=(188, 196, 222))
    draw.text((18, H - bar_h + 54), f"Age {age}  ·  Score {comp:.0f}/100  ·  ₹{income} LPA", font=fs, fill=(138, 148, 178))
    sbx, sby = W - 135, H - bar_h + 10
    draw.text((sbx, sby),     "COMPOSITE", font=fs, fill=(98, 108, 145))
    draw.rectangle([sbx, sby + 16, sbx + 100, sby + 26], fill=(18, 20, 34))
    draw.rectangle([sbx, sby + 16, sbx + int(comp), sby + 26], fill=sc)
    draw.text((sbx, sby + 30), f"{comp:.0f}/100", font=fs, fill=sc)
    draw.rectangle([1, 1, W - 2, H - 2], outline=(232, 184, 75), width=2)
    draw.rectangle([3, 3, W - 4, H - 4], outline=(80, 60, 18), width=1)

    noise_arr = np.array(canvas).astype(np.float32)
    noise     = np.random.normal(0, 5, noise_arr.shape)
    return Image.fromarray(np.clip(noise_arr + noise, 0, 255).astype(np.uint8))


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE CLASS
# ══════════════════════════════════════════════════════════════════════════════

class FutureSelfEngine:
    """
    Orchestrates scoring → simulation → image generation → LLM narrative
    for the Future Self Visualization pipeline.
    """

    def __init__(self) -> None:
        self._llm       = _build_groq_llm()
        self._hf_client = _build_hf_client()
        log.info("FutureSelfEngine ready.")

    def run(
        self,
        *,
        user_profile: dict[str, Any],
        generate_images: bool = True,
    ) -> dict[str, Any]:
        """
        Execute the full FutureSelf pipeline for one user.

        Returns:
            {
              "scores":     { academic, financial, career, lifestyle, composite, risk, profile, trend },
              "simulation": { 5_year: {...}, 10_year: {...}, 25_year: {...} },
              "images":     { 5_year: PIL.Image, ... }  # PIL Images
              "flux_prompts": { 5_year: str, ... },
              "scenarios":  { 5_year: str narrative, ... },
              "analysis":   { current_state, five_year_outlook, ... }
            }
        """
        log.info("FutureSelfEngine.run() started for user age=%s country=%s",
                 user_profile.get("age"), user_profile.get("country"))

        # ── 1. Deterministic scoring ──────────────────────────────────────────
        scores = compute_scores(user_profile)
        log.debug("Scores: %s", scores)

        # ── 2. Simulation ─────────────────────────────────────────────────────
        simulation = simulate(user_profile, scores)
        log.debug("Simulation keys: %s", list(simulation.keys()))

        # ── 3. Build FLUX prompts ─────────────────────────────────────────────
        flux_prompts: dict[str, str] = {}
        for key in ("5_year", "10_year", "25_year"):
            flux_prompts[key] = build_flux_prompt(key, simulation[key], user_profile)

        # ── 4. Image generation (FLUX → fallback) ────────────────────────────
        images: dict[str, Image.Image] = {}
        if generate_images:
            for key in ("5_year", "10_year", "25_year"):
                log.info("Generating image for %s …", key)
                img = generate_flux_image(flux_prompts[key], self._hf_client)
                if img is None:
                    log.warning("FLUX unavailable for %s — using PIL fallback.", key)
                    img = make_fallback_image(key, simulation[key], scores,
                                             user_profile.get("field", "Engineering / Technology"))
                else:
                    img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)
                images[key] = img

        # ── 5. LLM scenario narratives (per horizon) ──────────────────────────
        scenarios: dict[str, str] = {}
        if self._llm:
            for key, label in [("5_year", "5 years"), ("10_year", "10 years"), ("25_year", "25 years")]:
                prompt = future_self_scenario_prompt(
                    horizon_label=label,
                    age=simulation[key]["age"],
                    country=user_profile.get("country", "India"),
                    field=user_profile.get("field", "Engineering / Technology"),
                    career_status=simulation[key]["career_status"],
                    fin_status=simulation[key]["fin_status"],
                    life_quality=simulation[key]["life_quality"],
                    income_lpa=simulation[key]["income_lpa"],
                    scores=simulation[key],
                )
                raw = _llm_call_with_retry(self._llm, prompt)
                parsed = extract_json(raw, fallback={"narrative": raw})
                scenarios[key] = parsed.get("narrative", raw)
                log.debug("Scenario [%s]: %s…", key, scenarios[key][:80])
        else:
            for key in ("5_year", "10_year", "25_year"):
                scenarios[key] = "[LLM unavailable — add GROQ_API_KEY to .env]"

        # ── 6. Deep analysis ──────────────────────────────────────────────────
        analysis: dict[str, Any] = {}
        if self._llm:
            prompt = future_self_analysis_prompt(
                user=user_profile, scores=scores, sim=simulation
            )
            raw     = _llm_call_with_retry(self._llm, prompt)
            analysis = extract_json(raw, fallback={"current_state": raw})
            log.debug("Analysis keys: %s", list(analysis.keys()))
        else:
            analysis = {"current_state": "[LLM unavailable — add GROQ_API_KEY to .env]"}

        return {
            "scores":       scores,
            "simulation":   simulation,
            "images":       images,
            "flux_prompts": flux_prompts,
            "scenarios":    scenarios,
            "analysis":     analysis,
        }
