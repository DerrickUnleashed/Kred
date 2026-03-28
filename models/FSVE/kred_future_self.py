"""
KRED Future Self Visualization Engine
Generates realistic future lifestyle visualizations based on financial projections.

Usage:
    python kred_engine.py
    python kred_engine.py --name "Prannav" --age 20 --income 2000 --expenses 1000 --savings 0
    python kred_engine.py --ref-image "C:/path/to/dummy.jpeg"
    python kred_engine.py --help
"""

import os
import sys
import json
import math
import argparse
import io
import base64
import random
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

load_dotenv()

# ─── Constants ────────────────────────────────────────────────────────────────
ANNUAL_RETURN   = 0.10
INFLATION_RATE  = 0.06
TARGET_AGES     = [30, 40, 50, 60]
OUTPUT_DIR      = Path("kred_output")

# Models
IMG2IMG_MODEL   = "lllyasviel/control_v11p_sd15_openpose"   # ControlNet (pose-aware)
TXT2IMG_MODEL   = "black-forest-labs/FLUX.1-schnell"        # Fallback text-to-image
IP_ADAPTER_MODEL = "h94/IP-Adapter"                         # Face-preserving adapter

# Wealth thresholds (in INR) for lifestyle classification
THRESHOLDS = {
    "Comfortable": 5_000_000,   # 50 Lakhs+
    "Stable":      1_000_000,   # 10–50 Lakhs
    # Below Stable → At Risk
}


# ─── Reference Image Handling ─────────────────────────────────────────────────

def load_reference_image(ref_path: str | None) -> Image.Image | None:
    """
    Load the user's reference photo from disk.
    Resizes to 512x512 (standard diffusion input) and returns PIL Image.
    Returns None if path is not provided or file doesn't exist.
    """
    if not ref_path:
        return None

    path = Path(ref_path)
    if not path.exists():
        print(f"  [WARN] Reference image not found: {ref_path}")
        return None

    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((512, 512), Image.LANCZOS)
        print(f"  [REF] Loaded reference image: {path.name} → resized to 512×512")
        return img
    except Exception as e:
        print(f"  [WARN] Could not load reference image: {e}")
        return None


def image_to_base64(img: Image.Image) -> str:
    """Encode a PIL Image to base64 string (PNG format)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ─── Financial Simulation ─────────────────────────────────────────────────────

def simulate_wealth(current_age: int, monthly_income: float, monthly_expenses: float,
                    current_savings: float, savings_rate: float = 0.02) -> dict:
    """
    Project wealth at each target age using compound interest.
    Returns dict: {age: {"wealth": float, "real_wealth": float, "monthly_savings": float}}
    """
    monthly_savings = monthly_income * savings_rate
    annual_savings  = monthly_savings * 12
    results = {}

    for target_age in TARGET_AGES:
        if target_age <= current_age:
            continue
        years = target_age - current_age

        fv_current       = current_savings * ((1 + ANNUAL_RETURN) ** years)
        fv_contributions = annual_savings * (
            ((1 + ANNUAL_RETURN) ** years - 1) / ANNUAL_RETURN
        )
        nominal_wealth = fv_current + fv_contributions
        real_wealth    = nominal_wealth / ((1 + INFLATION_RATE) ** years)

        results[target_age] = {
            "wealth":          nominal_wealth,
            "real_wealth":     real_wealth,
            "monthly_savings": monthly_savings,
            "years":           years,
        }

    return results


def simulate_improved(current_age: int, monthly_income: float, monthly_expenses: float,
                      current_savings: float, savings_rate: float = 0.02) -> dict:
    """Improved scenario: +15% savings rate, -10% expenses."""
    improved_savings_rate   = savings_rate + 0.15
    improved_expenses       = monthly_expenses * 0.90
    improved_monthly_savings = monthly_income * improved_savings_rate
    annual_savings          = improved_monthly_savings * 12
    results = {}

    for target_age in TARGET_AGES:
        if target_age <= current_age:
            continue
        years = target_age - current_age
        fv_current       = current_savings * ((1 + ANNUAL_RETURN) ** years)
        fv_contributions = annual_savings * (
            ((1 + ANNUAL_RETURN) ** years - 1) / ANNUAL_RETURN
        )
        nominal_wealth = fv_current + fv_contributions
        real_wealth    = nominal_wealth / ((1 + INFLATION_RATE) ** years)

        results[target_age] = {
            "wealth":          nominal_wealth,
            "real_wealth":     real_wealth,
            "monthly_savings": improved_monthly_savings,
            "years":           years,
            "saved_expenses":  monthly_expenses - improved_expenses,
        }

    return results


# ─── Lifestyle Classification ──────────────────────────────────────────────────

def classify_lifestyle(real_wealth: float) -> str:
    if real_wealth >= THRESHOLDS["Comfortable"]:
        return "Comfortable"
    elif real_wealth >= THRESHOLDS["Stable"]:
        return "Stable"
    else:
        return "At Risk"


# ─── Aging Feature Descriptions ───────────────────────────────────────────────

AGE_FEATURES = {
    30: "slight maturity, minimal forehead lines, fuller face, early confidence in eyes",
    40: "mild wrinkles around eyes and forehead, slight greying at temples, defined jaw",
    50: "visible wrinkles, salt-and-pepper hair, aged skin texture, deeper expression lines",
    60: "strong wrinkles, mostly grey or white hair, aged and weathered skin, deep life experience in eyes",
}


# ─── Visual Mapping ───────────────────────────────────────────────────────────

LIFESTYLE_VISUALS = {
    "Comfortable": {
        "clothing":    "premium tailored formal suit, luxury watch, polished shoes",
        "environment": "modern luxury penthouse interior with floor-to-ceiling windows, city skyline view, expensive minimalist furniture",
        "expression":  "confident, relaxed, successful smile, proud posture",
        "lighting":    "warm golden hour ambient lighting",
        "bg_color":    (180, 140, 60),
    },
    "Stable": {
        "clothing":    "clean pressed business casual shirt and trousers",
        "environment": "comfortable middle-class Indian home interior, tidy living room, family photos on wall",
        "expression":  "calm, content, gentle smile, composed demeanor",
        "lighting":    "soft natural daylight from windows",
        "bg_color":    (60, 120, 160),
    },
    "At Risk": {
        "clothing":    "simple plain shirt, slightly worn fabric, modest appearance",
        "environment": "modest home with bare walls, basic sparse furniture, aging paint",
        "expression":  "tired, stressed expression, worried eyes, tense posture",
        "lighting":    "dim harsh overhead lighting, shadows on face",
        "bg_color":    (80, 80, 90),
    },
}


# ─── Prompt Builder ───────────────────────────────────────────────────────────

def build_prompt(name: str, age: int, lifestyle: str) -> str:
    aging = AGE_FEATURES.get(age, "natural aging")
    v = LIFESTYLE_VISUALS[lifestyle]
    return (
        f"A realistic portrait of the same Indian man, now {age} years old, "
        f"showing clear natural aging with {aging}. "
        f"The person represents a {lifestyle} lifestyle, "
        f"wearing {v['clothing']}, "
        f"standing in a {v['environment']}, "
        f"with {v['expression']}, {v['lighting']}. "
        f"Photorealistic, ultra detailed, natural skin texture, "
        f"DSLR quality, 8k, no fantasy elements, grounded and believable. "
        f"Same face, same identity as the reference person, aged {age} years."
    )


def build_negative_prompt() -> str:
    return (
        "different person, wrong face, cartoon, anime, illustration, "
        "fantasy, extra limbs, deformed, blurry, low quality, watermark, "
        "text, logo, unrealistic, painting, drawing"
    )


# ─── Image Generation — with Reference Image (img2img / IP-Adapter) ───────────

def generate_image_with_reference(prompt: str, ref_image: Image.Image) -> Image.Image | None:
    """
    Generate an aged/styled image conditioned on the reference face.

    Strategy (tries in order):
      1. HuggingFace InferenceClient image-to-image  (img2img)
      2. Replicate API with face-preserving model    (if REPLICATE_API_TOKEN set)
    Returns PIL Image or None on failure.
    """

    # ── Attempt 1: HuggingFace img2img ──────────────────────────────────────
    try:
        from huggingface_hub import InferenceClient
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        client   = InferenceClient(token=hf_token)

        # Convert reference image to bytes for the API
        buf = io.BytesIO()
        ref_image.save(buf, format="PNG")
        buf.seek(0)
        ref_bytes = buf.read()

        print("    [HF img2img] Sending request...", end=" ", flush=True)
        result = client.image_to_image(
            image=ref_bytes,
            prompt=prompt,
            negative_prompt=build_negative_prompt(),
            model="stabilityai/stable-diffusion-xl-refiner-1.0",
            strength=0.65,          # 0 = identical to ref, 1 = fully reimagined
            guidance_scale=7.5,
        )

        if isinstance(result, Image.Image):
            print("✓")
            return result
        return Image.open(io.BytesIO(result))

    except Exception as e:
        print(f"✗ ({e})")

    # ── Attempt 2: Replicate face-swapping / aging model ────────────────────
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    if replicate_token:
        try:
            import replicate

            print("    [Replicate] Sending request...", end=" ", flush=True)
            ref_b64  = image_to_base64(ref_image)
            data_uri = f"data:image/png;base64,{ref_b64}"

            output = replicate.run(
                # Face-conditioned aging model on Replicate
                "fofr/face-to-many:a07f252abbbd832009640b27f063ea52d87d7a23ce5e2f94202a2b5f3b1f8b5",
                input={
                    "image":         data_uri,
                    "prompt":        prompt,
                    "negative_prompt": build_negative_prompt(),
                    "style":         "Photographic",
                    "guidance_scale": 7.5,
                    "ip_adapter_scale": 0.8,
                }
            )
            # output is typically a list of URLs
            if output:
                import urllib.request
                url = output[0] if isinstance(output, list) else output
                with urllib.request.urlopen(str(url)) as resp:
                    img_bytes = resp.read()
                print("✓")
                return Image.open(io.BytesIO(img_bytes))

        except Exception as e:
            print(f"✗ ({e})")

    return None


# ─── Image Generation — Text-Only Fallback ────────────────────────────────────

def generate_image_hf(prompt: str) -> Image.Image | None:
    """Text-to-image via HuggingFace Inference API (no reference). Returns PIL Image or None."""
    try:
        from huggingface_hub import InferenceClient
        hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        client   = InferenceClient(token=hf_token)

        print("    [HF txt2img] Sending request...", end=" ", flush=True)
        result = client.text_to_image(prompt=prompt, model=TXT2IMG_MODEL)
        print("✓")

        if isinstance(result, Image.Image):
            return result
        return Image.open(io.BytesIO(result))

    except Exception as e:
        print(f"✗ ({e})")
        return None


# ─── Placeholder Image Generator ─────────────────────────────────────────────

def generate_placeholder(name: str, age: int, lifestyle: str, wealth: float,
                          ref_image: Image.Image | None = None) -> Image.Image:
    """
    Styled placeholder image.
    If ref_image is provided, it is composited into the placeholder so the
    person's face is still visible even when API calls fail.
    """
    W, H = 1024, 1024
    img  = Image.new("RGB", (W, H), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)
    v    = LIFESTYLE_VISUALS[lifestyle]
    bg   = v["bg_color"]

    # Background gradient
    for i in range(H):
        t = i / H
        r = int(bg[0] * (1 - t) + 10 * t)
        g = int(bg[1] * (1 - t) + 10 * t)
        b = int(bg[2] * (1 - t) + 10 * t)
        draw.line([(0, i), (W, i)], fill=(r, g, b))

    # ── Embed reference image (circular crop) if available ──────────────────
    if ref_image is not None:
        face_size = 420
        face      = ref_image.resize((face_size, face_size), Image.LANCZOS)

        # Apply aging effect: desaturate + darken slightly per decade
        decade_factor = (age - 20) / 40.0  # 0.0 at 20, 1.0 at 60
        enhancer = ImageEnhance.Color(face)
        face = enhancer.enhance(1.0 - decade_factor * 0.4)  # reduce saturation
        enhancer = ImageEnhance.Brightness(face)
        face = enhancer.enhance(1.0 - decade_factor * 0.15)

        # Circular mask
        mask = Image.new("L", (face_size, face_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, face_size, face_size], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(4))  # soft edge

        # Paste centered, above text bar
        cx = (W - face_size) // 2
        cy = (H - 200 - face_size) // 2
        img.paste(face, (cx, cy), mask)

        # Age-wrinkle texture overlay (semi-transparent lines)
        overlay     = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        over_draw   = ImageDraw.Draw(overlay)
        line_count  = {30: 0, 40: 4, 50: 8, 60: 13}.get(age, 0)
        face_cx     = cx + face_size // 2
        face_cy     = cy + face_size // 2
        for i in range(line_count):
            y = face_cy - 60 + i * 14
            alpha = 60 + i * 8
            over_draw.arc(
                [face_cx - 90 + i * 2, y, face_cx + 90 - i * 2, y + 10],
                start=0, end=180, fill=(30, 20, 15, alpha), width=1,
            )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    else:
        # Original silhouette fallback (no reference image)
        cx, cy  = W // 2, H // 2 - 80
        face_r  = 160
        body_h  = 300
        draw.ellipse([cx - 120, cy + face_r - 20, cx + 120, cy + face_r + body_h],
                     fill=(40, 40, 50))
        draw.ellipse([cx - face_r, cy - face_r, cx + face_r, cy + face_r],
                     fill=(60, 45, 35))
        line_count = {30: 0, 40: 3, 50: 6, 60: 10}.get(age, 0)
        for i in range(line_count):
            y = cy - face_r + 60 + i * 12
            draw.arc([cx - 80 + i * 2, y, cx + 80 - i * 2, y + 8],
                     start=0, end=180, fill=(45, 32, 24), width=1)

    # Lifestyle accent border
    border_color = {
        "Comfortable": (212, 175, 55),
        "Stable":      (70, 160, 200),
        "At Risk":     (180, 60, 60),
    }[lifestyle]
    draw = ImageDraw.Draw(img)
    for t in range(6):
        draw.rectangle([t, t, W - t, H - t], outline=border_color)

    _draw_overlay(draw, name, age, wealth, lifestyle, W, H)
    img = _add_grain(img, intensity=18)
    return img


def _add_grain(img: Image.Image, intensity: int = 15) -> Image.Image:
    grain  = Image.new("L", img.size)
    pixels = grain.load()
    for x in range(img.width):
        for y in range(img.height):
            pixels[x, y] = random.randint(128 - intensity, 128 + intensity)
    grain_rgb = Image.merge("RGB", [grain, grain, grain])
    return Image.blend(img.convert("RGB"), grain_rgb, alpha=0.08)


# ─── Overlay Text ─────────────────────────────────────────────────────────────

def _draw_overlay(draw: ImageDraw.Draw, name: str, age: int,
                  wealth: float, lifestyle: str, W: int, H: int):
    status_colors = {
        "Comfortable": (212, 175, 55),
        "Stable":      (100, 200, 255),
        "At Risk":     (255, 90, 90),
    }
    color = status_colors[lifestyle]

    bar_h   = 180
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bar_draw = ImageDraw.Draw(overlay)
    bar_draw.rectangle([0, H - bar_h, W, H], fill=(0, 0, 0, 180))

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_mid   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except Exception:
        font_large = font_mid = font_small = ImageFont.load_default()

    if wealth >= 10_000_000:
        wealth_str = f"₹{wealth/10_000_000:.1f} Cr"
    elif wealth >= 100_000:
        wealth_str = f"₹{wealth/100_000:.1f} L"
    else:
        wealth_str = f"₹{wealth:,.0f}"

    y_base = H - bar_h + 18
    draw.text((40, y_base),        f"{name}, Age {age}",            font=font_large, fill=(255, 255, 255))
    draw.text((40, y_base + 62),   f"Projected Wealth: {wealth_str}", font=font_mid,   fill=(200, 200, 200))
    draw.text((40, y_base + 108),  f"● {lifestyle}",                 font=font_mid,   fill=color)
    draw.text((W - 160, 24),       "KRED",                           font=font_large, fill=color)
    draw.text((W - 230, 78),       "Future Self Engine",             font=font_small, fill=(180, 180, 180))


def add_overlay_to_image(img: Image.Image, name: str, age: int,
                          wealth: float, lifestyle: str) -> Image.Image:
    W, H = img.size
    draw = ImageDraw.Draw(img)
    _draw_overlay(draw, name, age, wealth, lifestyle, W, H)
    return img


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def run_engine(name: str, current_age: int, monthly_income: float,
               monthly_expenses: float, current_savings: float,
               savings_rate: float = 0.02, improved: bool = False,
               ref_image: Image.Image | None = None) -> dict:
    """
    Full pipeline:
      1. Simulate finances
      2. Classify lifestyle
      3. Generate images (reference-conditioned → text-only → placeholder)
      4. Save to output folder
    Returns summary dict.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    has_ref = ref_image is not None
    print(f"\n{'='*60}")
    print(f"  KRED Future Self Visualization Engine")
    print(f"  User: {name} | Age: {current_age}")
    print(f"  Mode: {'Improved Scenario' if improved else 'Current Trajectory'}")
    print(f"  Reference Image: {'✓ Loaded' if has_ref else '✗ Not provided (using generic)'}")
    print(f"{'='*60}\n")

    if improved:
        projections    = simulate_improved(current_age, monthly_income,
                                           monthly_expenses, current_savings, savings_rate)
        scenario_label = "improved"
    else:
        projections    = simulate_wealth(current_age, monthly_income,
                                          monthly_expenses, current_savings, savings_rate)
        scenario_label = "current"

    summary = {
        "user":         name,
        "current_age":  current_age,
        "scenario":     scenario_label,
        "has_reference_image": has_ref,
        "projections":  {},
        "generated_at": datetime.now().isoformat(),
    }

    for age, data in projections.items():
        real_wealth = data["real_wealth"]
        lifestyle   = classify_lifestyle(real_wealth)
        prompt      = build_prompt(name, age, lifestyle)

        print(f"  Age {age} → {lifestyle}")
        print(f"    Nominal Wealth : ₹{data['wealth']:>14,.0f}")
        print(f"    Real Wealth    : ₹{real_wealth:>14,.0f}")
        print(f"    Prompt         : {prompt[:80]}...")

        img        = None
        img_source = "placeholder"

        # ── Step 1: Reference-conditioned generation ─────────────────────────
        if ref_image is not None:
            print(f"    Generating (reference-conditioned)...", end=" ", flush=True)
            img = generate_image_with_reference(prompt, ref_image)
            if img is not None:
                img_source = "AI (img2img)"
                print(f"  ✓ ({img_source})")

        # ── Step 2: Text-only AI generation ──────────────────────────────────
        if img is None:
            if ref_image is not None:
                print(f"    Falling back to text-only generation...")
            else:
                print(f"    Generating (text-to-image)...", end=" ", flush=True)
            img = generate_image_hf(prompt)
            if img is not None:
                img_source = "AI (txt2img)"

        # ── Step 3: Styled placeholder ────────────────────────────────────────
        if img is None:
            print(f"    Using styled placeholder...")
            img        = generate_placeholder(name, age, lifestyle, real_wealth, ref_image)
            img_source = "placeholder" + (" (with reference face)" if ref_image else "")

        # Resize + overlay
        img = img.resize((1024, 1024), Image.LANCZOS)
        img = add_overlay_to_image(img, name, age, real_wealth, lifestyle)

        filename = (
            f"{name.lower()}_{scenario_label}_age{age}"
            f"_{lifestyle.lower().replace(' ', '_')}.png"
        )
        filepath = OUTPUT_DIR / filename
        img.save(filepath)
        print(f"    Saved [{img_source}] → {filepath}\n")

        summary["projections"][age] = {
            "nominal_wealth": data["wealth"],
            "real_wealth":    real_wealth,
            "lifestyle":      lifestyle,
            "image_path":     str(filepath),
            "image_source":   img_source,
        }

    summary_path = OUTPUT_DIR / f"{name.lower()}_{scenario_label}_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary saved → {summary_path}")

    return summary


def print_financial_report(base: dict, improved: dict):
    print(f"\n{'='*60}")
    print(" FINANCIAL PROJECTION COMPARISON")
    print(f"{'='*60}")
    print(f" {'Age':<6} {'Current Trajectory':<28} {'Improved Scenario'}")
    print(f" {'-'*56}")
    ages = sorted(base["projections"].keys())
    for age in ages:
        b     = base["projections"][age]
        i     = improved["projections"][age]
        b_str = f"₹{b['real_wealth']/100000:.1f}L ({b['lifestyle']})"
        i_str = f"₹{i['real_wealth']/100000:.1f}L ({i['lifestyle']})"
        print(f" {age:<6} {b_str:<28} {i_str}")
    print(f"{'='*60}\n")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="KRED Future Self Visualization Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--name",      default="Prannav", help="User's name")
    parser.add_argument("--age",       type=int,   default=20,   help="Current age")
    parser.add_argument("--income",    type=float, default=2000, help="Monthly income (₹)")
    parser.add_argument("--expenses",  type=float, default=1000, help="Monthly expenses (₹)")
    parser.add_argument("--savings",   type=float, default=0,    help="Current savings (₹)")
    parser.add_argument("--rate",      type=float, default=0.02, help="Savings rate (0.02 = 2%%)")
    parser.add_argument("--ref-image", default=None,
                        help="Path to reference photo of the user (e.g. dummy.jpeg). "
                             "Used to condition AI generation on the user's actual face.")
    parser.add_argument("--no-improved", action="store_true", help="Skip improved scenario")
    args = parser.parse_args()

    # Load reference image once; reuse across both scenarios
    ref_image = load_reference_image(args.ref_image)

    base_summary = run_engine(
        name=args.name,
        current_age=args.age,
        monthly_income=args.income,
        monthly_expenses=args.expenses,
        current_savings=args.savings,
        savings_rate=args.rate,
        improved=False,
        ref_image=ref_image,
    )

    if not args.no_improved:
        improved_summary = run_engine(
            name=args.name,
            current_age=args.age,
            monthly_income=args.income,
            monthly_expenses=args.expenses,
            current_savings=args.savings,
            savings_rate=args.rate,
            improved=True,
            ref_image=ref_image,
        )
        print_financial_report(base_summary, improved_summary)

    print(f"  ✅ All images saved to: {OUTPUT_DIR.resolve()}")
    print(f"  Open the folder to view your future self visualizations.\n")


if __name__ == "__main__":
    main()