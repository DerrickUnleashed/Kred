"""
KRED Future Self Visualization Engine — Streamlit App
AI-based facial age progression with visual awareness insights.

Usage:
    streamlit run app.py

Requirements:
    pip install streamlit pillow anthropic requests python-dotenv
"""

import os
import io
import base64
import json
import random
import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import requests
from dotenv import load_dotenv

load_dotenv()

# ─── Constants ─────────────────────────────────────────────────────────────────
BASE_OUTPUT_DIR = Path("models/FSVE")
AGE_FOLDERS = {
    "original": "original",
    "aged_40":  "aged_40",
    "aged_60":  "aged_60",
    "aged_80":  "aged_80",
}
TARGET_AGES = [40, 60, 80]

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KRED · Future Self Engine",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0a0a0f;
    color: #e8e6f0;
}

/* ── Header ── */
.kred-header {
    background: linear-gradient(135deg, #0d0d1a 0%, #1a0a2e 50%, #0d1a1a 100%);
    border: 1px solid rgba(180,100,255,0.2);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.kred-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(120,60,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.kred-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(0,200,180,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.kred-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #b87fff, #00c8b0, #b87fff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s ease infinite;
    position: relative; z-index:1;
}
@keyframes shimmer { 0%,100%{background-position:0%} 50%{background-position:100%} }
.kred-sub {
    font-weight: 300;
    font-size: 1rem;
    color: rgba(220,215,240,0.65);
    margin-top: .4rem;
    position: relative; z-index:1;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}
.age-card {
    background: linear-gradient(145deg, rgba(20,10,40,0.9), rgba(10,20,30,0.9));
    border: 1px solid rgba(180,100,255,0.25);
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
    transition: transform .2s;
}
.age-card:hover { transform: translateY(-3px); }
.age-label {
    font-family: 'Syne', sans-serif;
    font-size: .75rem;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: #b87fff;
    margin-bottom: .4rem;
}

/* ── Risk badges ── */
.risk-low    { background:#0d2e1a; border:1px solid #22c55e; color:#22c55e; padding:.3rem .9rem; border-radius:999px; font-size:.85rem; font-weight:600; display:inline-block; }
.risk-moderate { background:#2e1f0d; border:1px solid #f59e0b; color:#f59e0b; padding:.3rem .9rem; border-radius:999px; font-size:.85rem; font-weight:600; display:inline-block; }
.risk-high   { background:#2e0d0d; border:1px solid #ef4444; color:#ef4444; padding:.3rem .9rem; border-radius:999px; font-size:.85rem; font-weight:600; display:inline-block; }

/* ── Warning banner ── */
.warning-banner {
    background: linear-gradient(90deg, rgba(239,68,68,0.15), rgba(251,146,60,0.12));
    border-left: 3px solid #ef4444;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    font-size: .95rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid rgba(180,100,255,0.15);
}
section[data-testid="stSidebar"] .block-container { padding-top: 2rem; }
.sidebar-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #b87fff;
    letter-spacing: .06em;
    margin-bottom: 1.2rem;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    padding: .6rem 1.4rem !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg, #7c3aed, #00c8b0) !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Insight box ── */
.insight-box {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: .6rem 0;
    font-size: .92rem;
    line-height: 1.65;
}
.insight-box h4 {
    font-family: 'Syne', sans-serif;
    font-size: .85rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #b87fff;
    margin: 0 0 .6rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def pil_to_b64(img: Image.Image, fmt: str = "PNG") -> str:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode()


def b64_to_pil(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


def ensure_output_dirs(username: str = "user") -> dict:
    dirs = {}
    for key, folder in AGE_FOLDERS.items():
        p = BASE_OUTPUT_DIR / folder
        p.mkdir(parents=True, exist_ok=True)
        dirs[key] = p
    return dirs


def save_outputs(images: dict, username: str = "user") -> dict:
    """Save {label: PIL.Image} dict. Returns {label: path}."""
    dirs   = ensure_output_dirs(username)
    ts     = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    saved  = {}
    label_map = {
        "original": "original",
        "aged_40":  "aged_40",
        "aged_60":  "aged_60",
        "aged_80":  "aged_80",
    }
    for key, img in images.items():
        folder = dirs.get(key)
        if folder and img is not None:
            fname = f"{username}_{ts}.png"
            path  = folder / fname
            img.save(path)
            saved[key] = str(path)
    return saved


# ─── Model / Image Generation ──────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_hf_client():
    """Lazy-load HuggingFace InferenceClient (cached across reruns)."""
    try:
        from huggingface_hub import InferenceClient
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        return InferenceClient(token=token)
    except Exception:
        return None


def preprocess_image(img: Image.Image, size: int = 512) -> Image.Image:
    """Resize + convert to RGB. Crops to square first."""
    img = img.convert("RGB")
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    return img.resize((size, size), Image.LANCZOS)


def build_age_prompt(target_age: int, gender: str, lifestyle: str,
                     screen_time: str, eye_care: str) -> str:
    """Build a rich conditioning prompt from user inputs."""
    gender_desc = {"Male": "man", "Female": "woman", "Prefer not to say": "person"}[gender]

    lifestyle_mods = {
        "Healthy":  "gracefully aged with healthy skin, minimal deep wrinkles, good posture, vibrant eyes",
        "Average":  "naturally aged with moderate wrinkles, some sun spots, normal skin laxity",
        "Risky":    "prematurely aged with deep wrinkles, dull sagging skin, tired hollowed face, weathered complexion",
    }
    screen_mods = {
        "Low":    "clear bright eyes, no under-eye bags",
        "Medium": "slight under-eye circles, mild eye strain visible",
        "High":   "pronounced under-eye bags, squinting lines, digital eye strain evident",
    }
    eye_care_mod = (
        "clear healthy eyes with good scleral whites"
        if eye_care == "Yes"
        else "yellowed sclera, slight drooping eyelids, visible eye fatigue"
    )

    return (
        f"Ultra-realistic portrait of a {target_age}-year-old Indian {gender_desc}, "
        f"same facial structure and bone proportions as the reference image, "
        f"aged naturally to {target_age} years old, "
        f"{lifestyle_mods[lifestyle]}, "
        f"{screen_mods[screen_time]}, "
        f"{eye_care_mod}. "
        f"DSLR photograph, 8k, photorealistic skin texture, natural studio lighting, "
        f"same identity and face shape, no cartoon, no fantasy, no makeup filters."
    )


def generate_aged_images(ref_img: Image.Image, current_age: int, gender: str,
                          lifestyle: str, screen_time: str, eye_care: str,
                          progress_bar=None) -> dict:
    """
    Generate aged versions. Tries HF img2img → styled placeholder fallback.
    Returns {label: PIL.Image}
    """
    results = {"original": ref_img.copy()}
    client  = load_hf_client()
    steps   = len(TARGET_AGES)

    age_labels = {40: "aged_40", 60: "aged_60", 80: "aged_80"}

    for i, target_age in enumerate(TARGET_AGES):
        label   = age_labels[target_age]
        prompt  = build_age_prompt(target_age, gender, lifestyle, screen_time, eye_care)
        neg     = ("cartoon, anime, illustration, painting, text, watermark, "
                   "different person, deformed, extra limbs, blurry, low quality")
        img = None

        # ── Try HF img2img ──────────────────────────────────────────────────
        if client:
            try:
                buf = io.BytesIO()
                ref_img.save(buf, format="PNG")
                buf.seek(0)
                result = client.image_to_image(
                    image=buf.read(),
                    prompt=prompt,
                    negative_prompt=neg,
                    model="stabilityai/stable-diffusion-xl-refiner-1.0",
                    strength=_aging_strength(current_age, target_age),
                    guidance_scale=7.5,
                )
                img = result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
            except Exception:
                pass

        # ── Try HF txt2img ──────────────────────────────────────────────────
        if img is None and client:
            try:
                result = client.text_to_image(
                    prompt=prompt,
                    model="black-forest-labs/FLUX.1-schnell",
                )
                img = result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
            except Exception:
                pass

        # ── Styled placeholder with face compositing ────────────────────────
        if img is None:
            img = _styled_placeholder(ref_img, target_age, lifestyle, screen_time, eye_care)

        results[label] = img.resize((512, 512), Image.LANCZOS)

        if progress_bar:
            progress_bar.progress((i + 1) / steps)

    return results


def _aging_strength(current_age: int, target_age: int) -> float:
    """Map age delta to img2img strength (0.4–0.78)."""
    delta = max(0, target_age - current_age)
    return min(0.78, 0.40 + delta * 0.006)


def _styled_placeholder(ref_img: Image.Image, target_age: int,
                         lifestyle: str, screen_time: str, eye_care: str) -> Image.Image:
    """
    High-quality fallback: composites the reference face with aging overlays
    when no AI API is available.
    """
    W = H = 512
    # Background gradient per lifestyle
    bg_colors = {
        "Healthy":  [(15, 30, 25), (5, 15, 12)],
        "Average":  [(20, 20, 35), (8, 8, 20)],
        "Risky":    [(30, 15, 15), (15, 5, 5)],
    }
    c1, c2 = bg_colors.get(lifestyle, [(20, 20, 30), (8, 8, 15)])
    canvas = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(canvas)
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Composite face (circular crop) with aging effects
    face_sz = 320
    face    = ref_img.resize((face_sz, face_sz), Image.LANCZOS)

    # Aging simulation
    age_factor = (target_age - 20) / 65.0
    # Desaturate
    face = ImageEnhance.Color(face).enhance(1.0 - age_factor * 0.55)
    # Darken slightly
    face = ImageEnhance.Brightness(face).enhance(1.0 - age_factor * 0.18)
    # Slight contrast boost (skin texture)
    face = ImageEnhance.Contrast(face).enhance(1.0 + age_factor * 0.2)

    # Screen time → eye area darkening
    if screen_time == "High":
        eye_overlay = Image.new("RGBA", (face_sz, face_sz), (0, 0, 0, 0))
        eye_draw    = ImageDraw.Draw(eye_overlay)
        eye_draw.ellipse([face_sz // 4, face_sz // 3,
                          3 * face_sz // 4, face_sz // 2 + 20],
                         fill=(0, 0, 30, int(60 * age_factor)))
        face = Image.alpha_composite(face.convert("RGBA"), eye_overlay).convert("RGB")

    # Circular mask
    mask = Image.new("L", (face_sz, face_sz), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, face_sz, face_sz], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))

    cx = (W - face_sz) // 2
    cy = (H - face_sz) // 2 - 20
    canvas.paste(face, (cx, cy), mask)

    # Wrinkle arcs overlay
    wrinkle_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd          = ImageDraw.Draw(wrinkle_img)
    n_wrinkles  = max(0, int((age_factor * 18)))
    face_cx = cx + face_sz // 2
    face_cy = cy + face_sz // 2
    for i in range(n_wrinkles):
        yy    = face_cy - 60 + i * 13
        alpha = min(255, 40 + i * 10)
        wd.arc([face_cx - 85 + i * 2, yy,
                face_cx + 85 - i * 2, yy + 9],
               start=0, end=180,
               fill=(35, 25, 20, alpha), width=1)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), wrinkle_img).convert("RGB")

    # Age label badge
    draw = ImageDraw.Draw(canvas)
    badge_color = {"Healthy": (34, 197, 94), "Average": (245, 158, 11), "Risky": (239, 68, 68)}[lifestyle]
    draw.rounded_rectangle([cx, cy + face_sz + 14, cx + face_sz, cy + face_sz + 44],
                            radius=8, fill=(*badge_color, 60))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except Exception:
        font = ImageFont.load_default()
    draw.text((W // 2, cy + face_sz + 29), f"Age {target_age} · {lifestyle}",
              font=font, fill=badge_color, anchor="mm")

    return canvas


# ─── Awareness Report via Claude API ──────────────────────────────────────────

def generate_awareness_report(current_age: int, gender: str, lifestyle: str,
                               screen_time: str, eye_care: str) -> dict:
    """
    Calls Claude to generate a structured awareness report.
    Returns {risk_level, risk_class, suggestions, summary}
    """
    prompt = f"""
You are a preventive health advisor specialising in facial aging and digital eye health.

User profile:
- Current age: {current_age}
- Gender: {gender}
- Lifestyle: {lifestyle}
- Daily screen time: {screen_time}
- Consistent eye care habits: {eye_care}

Respond ONLY with a valid JSON object (no markdown fences) with these exact keys:
{{
  "risk_level": "Low" | "Moderate" | "High",
  "summary": "2-sentence summary of overall aging trajectory",
  "suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "eye_health_note": "1-sentence specific note about eye health based on their habits"
}}
""".strip()

    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        raw  = resp.json()["content"][0]["text"].strip()
        raw  = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        risk = data.get("risk_level", "Moderate")
        data["risk_class"] = {"Low": "risk-low", "Moderate": "risk-moderate", "High": "risk-high"}.get(risk, "risk-moderate")
        return data
    except Exception as e:
        # Graceful deterministic fallback
        risk = _fallback_risk(lifestyle, screen_time, eye_care)
        return {
            "risk_level": risk,
            "risk_class": {"Low": "risk-low", "Moderate": "risk-moderate", "High": "risk-high"}[risk],
            "summary": "Based on your inputs, your aging trajectory has been estimated. Consistent healthy habits are the strongest predictor of graceful aging.",
            "suggestions": [
                "Adopt a consistent SPF 30+ sunscreen routine daily.",
                "Limit recreational screen exposure to under 4 hours per day.",
                "Schedule annual eye examinations and use blue-light filters.",
            ],
            "eye_health_note": "Your current screen habits may accelerate digital eye strain over time.",
        }


def _fallback_risk(lifestyle: str, screen_time: str, eye_care: str) -> str:
    score = {"Healthy": 0, "Average": 1, "Risky": 2}[lifestyle]
    score += {"Low": 0, "Medium": 1, "High": 2}[screen_time]
    score += 0 if eye_care == "Yes" else 1
    if score <= 1:   return "Low"
    if score <= 3:   return "Moderate"
    return "High"


# ─── Image Comparison Slider (HTML) ───────────────────────────────────────────

def render_comparison_slider(img_before: Image.Image, img_after: Image.Image,
                              label_before: str = "Now", label_after: str = "Future") -> None:
    b64_before = pil_to_b64(img_before.resize((480, 480)))
    b64_after  = pil_to_b64(img_after.resize((480, 480)))

    html = f"""
<div style="position:relative;width:480px;margin:0 auto;border-radius:14px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.6);">
  <img id="imgAfter" src="data:image/png;base64,{b64_after}"
       style="display:block;width:480px;height:480px;object-fit:cover;" />
  <div id="clipBefore" style="position:absolute;top:0;left:0;width:50%;height:100%;overflow:hidden;">
    <img src="data:image/png;base64,{b64_before}"
         style="display:block;width:480px;height:480px;object-fit:cover;" />
  </div>
  <div id="handle" style="position:absolute;top:0;left:50%;width:3px;height:100%;
       background:linear-gradient(180deg,#b87fff,#00c8b0);cursor:ew-resize;z-index:10;">
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
         width:32px;height:32px;border-radius:50%;background:#1a0a2e;
         border:2px solid #b87fff;display:flex;align-items:center;justify-content:center;
         color:#b87fff;font-size:14px;">⇔</div>
  </div>
  <span style="position:absolute;bottom:12px;left:14px;background:rgba(0,0,0,.65);
        color:#b87fff;font-size:12px;padding:3px 10px;border-radius:99px;
        font-family:monospace;">{label_before}</span>
  <span style="position:absolute;bottom:12px;right:14px;background:rgba(0,0,0,.65);
        color:#00c8b0;font-size:12px;padding:3px 10px;border-radius:99px;
        font-family:monospace;">{label_after}</span>
</div>
<script>
(function(){{
  var handle    = document.getElementById('handle');
  var clipDiv   = document.getElementById('clipBefore');
  var container = handle.parentElement;
  var dragging  = false;
  handle.addEventListener('mousedown',  function(e){{ dragging=true; e.preventDefault(); }});
  handle.addEventListener('touchstart', function(e){{ dragging=true; }}, {{passive:true}});
  document.addEventListener('mouseup',  function(){{ dragging=false; }});
  document.addEventListener('touchend', function(){{ dragging=false; }});
  document.addEventListener('mousemove', function(e){{
    if(!dragging) return;
    var rect = container.getBoundingClientRect();
    var pct  = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    handle.style.left = (pct*100)+'%';
    clipDiv.style.width = (pct*100)+'%';
  }});
  document.addEventListener('touchmove', function(e){{
    if(!dragging) return;
    var rect = container.getBoundingClientRect();
    var pct  = Math.max(0, Math.min(1, (e.touches[0].clientX - rect.left) / rect.width));
    handle.style.left = (pct*100)+'%';
    clipDiv.style.width = (pct*100)+'%';
  }}, {{passive:true}});
}})();
</script>
"""
    st.components.v1.html(html, height=500)


# ─── Main App ──────────────────────────────────────────────────────────────────

def main():
    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="kred-header">
      <div class="kred-title">KRED · Future Self Engine</div>
      <div class="kred-sub">AI-powered facial age progression &amp; wellness awareness platform</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar inputs ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙ YOUR PROFILE</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "📸 Upload your face photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="Clear, front-facing photo gives the best results.",
        )

        st.markdown("---")
        current_age  = st.number_input("Current Age", min_value=10, max_value=70, value=20, step=1)
        gender       = st.selectbox("Gender", ["Male", "Female", "Prefer not to say"])
        lifestyle    = st.selectbox("Lifestyle", ["Healthy", "Average", "Risky"],
                                    help="Healthy = regular exercise, balanced diet; Risky = smoking, poor diet, etc.")
        screen_time  = st.selectbox("Daily Screen Time", ["Low", "Medium", "High"],
                                    help="Low < 3 h · Medium 3–6 h · High > 6 h")
        eye_care     = st.selectbox("Consistent Eye Care Habits", ["Yes", "No"],
                                    help="Regular check-ups, blue-light glasses, eye drops, etc.")

        st.markdown("---")
        run_btn = st.button("🔮  Generate My Future Self", use_container_width=True)

    # ── Main panel ──────────────────────────────────────────────────────────
    if not uploaded:
        # Welcome state
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem 2rem;">
          <div style="font-size:3.5rem;margin-bottom:1rem;">🪞</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:700;margin-bottom:.6rem;">
            See your future self
          </div>
          <div style="color:rgba(220,215,240,.55);max-width:420px;margin:0 auto;line-height:1.7;">
            Upload a face photo and fill in your health profile on the left.
            The engine will project how your face may look at 40, 60 and 80 —
            shaped by the habits you build today.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Load & preprocess reference image
    ref_pil = preprocess_image(Image.open(uploaded))

    col_preview, col_info = st.columns([1, 2])
    with col_preview:
        st.markdown('<div class="age-card">', unsafe_allow_html=True)
        st.markdown('<div class="age-label">YOUR PHOTO</div>', unsafe_allow_html=True)
        st.image(ref_pil, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
        <div class="card">
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.8rem;">
            Projection Parameters
          </div>
          <table style="width:100%;font-size:.9rem;border-collapse:collapse;">
            <tr><td style="padding:.3rem 0;color:rgba(220,215,240,.55);">Age</td>
                <td style="font-weight:500;">{current_age}</td></tr>
            <tr><td style="padding:.3rem 0;color:rgba(220,215,240,.55);">Gender</td>
                <td style="font-weight:500;">{gender}</td></tr>
            <tr><td style="padding:.3rem 0;color:rgba(220,215,240,.55);">Lifestyle</td>
                <td style="font-weight:500;">{lifestyle}</td></tr>
            <tr><td style="padding:.3rem 0;color:rgba(220,215,240,.55);">Screen time</td>
                <td style="font-weight:500;">{screen_time}</td></tr>
            <tr><td style="padding:.3rem 0;color:rgba(220,215,240,.55);">Eye care</td>
                <td style="font-weight:500;">{eye_care}</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    if not run_btn:
        return

    # ── Generation ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.1rem;font-weight:700;margin-bottom:.8rem;">Generating your future projections…</div>', unsafe_allow_html=True)

    pbar   = st.progress(0)
    status = st.empty()

    with st.spinner(""):
        status.markdown("_Initialising age progression pipeline…_")
        images = generate_aged_images(
            ref_img=ref_pil,
            current_age=current_age,
            gender=gender,
            lifestyle=lifestyle,
            screen_time=screen_time,
            eye_care=eye_care,
            progress_bar=pbar,
        )

    pbar.progress(1.0)
    status.empty()

    # Save outputs
    username  = uploaded.name.rsplit(".", 1)[0][:20]
    saved_paths = save_outputs(images, username=username)

    # ── Display aged images ──────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.3rem;font-weight:700;margin-bottom:1rem;">📸 Age Projections</div>', unsafe_allow_html=True)

    labels = {
        "original": ("Current", "#b87fff"),
        "aged_40":  ("Age 40",  "#00c8b0"),
        "aged_60":  ("Age 60",  "#f59e0b"),
        "aged_80":  ("Age 80",  "#ef4444"),
    }

    cols = st.columns(4)
    for i, (key, (label, color)) in enumerate(labels.items()):
        img = images.get(key)
        if img is None:
            continue
        with cols[i]:
            st.markdown(f'<div class="age-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="age-label" style="color:{color};">{label}</div>', unsafe_allow_html=True)
            st.image(img, use_container_width=True)

            # Download button
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                label="⬇ Download",
                data=buf.getvalue(),
                file_name=f"{username}_{key}.png",
                mime="image/png",
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Comparison slider ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:1.3rem;font-weight:700;margin-bottom:1rem;">🔍 Before / After Comparison</div>', unsafe_allow_html=True)

    compare_with = st.radio("Compare current photo with:", ["Age 40", "Age 60", "Age 80"], horizontal=True)
    key_map = {"Age 40": "aged_40", "Age 60": "aged_60", "Age 80": "aged_80"}
    render_comparison_slider(
        images["original"],
        images[key_map[compare_with]],
        label_before="Now",
        label_after=compare_with,
    )

    # ── Warning banner ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="warning-banner">
      ⚠️  <strong>Your future vision health depends on your current habits.</strong>
      The projections above are illustrative — but the underlying science is real.
      Lifestyle, screen exposure and eye care choices made today compound over decades.
    </div>
    """, unsafe_allow_html=True)

    # ── AI Awareness Report ──────────────────────────────────────────────────
    with st.expander("🔬  See Future Insights & Personalised Recommendations", expanded=True):
        with st.spinner("Generating your personalised health insight…"):
            report = generate_awareness_report(current_age, gender, lifestyle, screen_time, eye_care)

        risk_label = report.get("risk_level", "Moderate")
        risk_class = report.get("risk_class",  "risk-moderate")

        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"""
            <div style="text-align:center;padding:1.5rem;">
              <div style="font-family:'Syne',sans-serif;font-size:.75rem;letter-spacing:.15em;
                   text-transform:uppercase;color:rgba(220,215,240,.5);margin-bottom:.5rem;">
                AGING RISK LEVEL
              </div>
              <span class="{risk_class}" style="font-size:1.1rem;">{risk_label}</span>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="insight-box">
              <h4>📋 Summary</h4>
              {report.get('summary','')}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="insight-box">
              <h4>👁 Eye Health Note</h4>
              {report.get('eye_health_note','')}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div style="font-family:\'Syne\',sans-serif;font-size:.9rem;font-weight:700;margin:.8rem 0 .4rem;letter-spacing:.06em;color:#b87fff;">ACTIONABLE SUGGESTIONS</div>', unsafe_allow_html=True)
        for sug in report.get("suggestions", []):
            st.markdown(f"""
            <div style="display:flex;gap:.7rem;align-items:flex-start;
                 background:rgba(0,200,176,0.06);border:1px solid rgba(0,200,176,0.2);
                 border-radius:10px;padding:.8rem 1rem;margin:.4rem 0;font-size:.92rem;line-height:1.6;">
              <span style="color:#00c8b0;font-size:1rem;flex-shrink:0;">✦</span>
              <span>{sug}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Output paths ─────────────────────────────────────────────────────────
    if saved_paths:
        with st.expander("📁 Saved Output Paths"):
            for key, path in saved_paths.items():
                st.code(path, language="bash")


if __name__ == "__main__":
    main()