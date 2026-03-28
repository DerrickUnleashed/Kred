from __future__ import annotations
import os, io, datetime, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = Path("models/FSVE")
FOLDERS  = {"5_year": "5_year", "10_year": "10_year", "25_year": "25_year"}

# ── Color palettes per financial condition ────────────────────────────────────
PALETTE = {
    "Wealthy":    {"bg": [(8,20,40),(4,12,25)],   "accent": (100,200,255), "border": (80,160,220)},
    "Comfortable":{"bg": [(15,30,20),(8,18,12)],   "accent": (80,200,120), "border": (60,180,100)},
    "Moderate":   {"bg": [(25,25,35),(12,12,20)],  "accent": (160,130,255),"border": (140,110,240)},
    "Tight":      {"bg": [(35,28,15),(20,16,8)],   "accent": (220,170,60), "border": (200,150,40)},
    "Struggling": {"bg": [(35,15,15),(20,8,8)],    "accent": (220,80,80),  "border": (200,60,60)},
}

CAREER_ICONS = {
    "Elite":    "⬡",
    "Strong":   "◈",
    "Stable":   "◆",
    "Emerging": "◇",
    "Unstable": "○",
}

HORIZON_LABELS = {
    "5_year":  "5 YEARS",
    "10_year": "10 YEARS",
    "25_year": "25 YEARS",
}

SCENE_ELEMENTS = {
    "Wealthy": [
        "Panoramic glass penthouse office",
        "Minimalist marble desk, triple monitors",
        "Award plaques on brushed concrete wall",
        "Private meeting room with city skyline",
        "Executive ergonomic setup, warm ambient light",
    ],
    "Comfortable": [
        "Modern 2BHK home office corner",
        "Standing desk, clean cable management",
        "Plants, bookshelf, soft daylight from window",
        "Laptop + external monitor, noise-cancelling headphones",
        "Tidy kitchen visible in background",
    ],
    "Moderate": [
        "Compact urban apartment workspace",
        "Wooden desk with moderate clutter",
        "Single monitor, coffee mug, stacked papers",
        "City apartment balcony with distant skyline",
        "Shared co-working space, medium energy",
    ],
    "Tight": [
        "Small rented room, basic desk",
        "Aged laptop, fluorescent overhead light",
        "Motivational poster on peeling paint",
        "Crowded neighbourhood visible from window",
        "Shared flat common area, budget furniture",
    ],
    "Struggling": [
        "Dimly lit cluttered workspace",
        "Older desktop PC, worn keyboard",
        "Stacked bills on desk corner",
        "Mattress-on-floor visible in corner",
        "Bare walls, single bare-bulb light",
    ],
}


# ─── HF Image Generation ──────────────────────────────────────────────────────

def _try_hf_generation(prompt: str) -> Image.Image | None:
    try:
        from huggingface_hub import InferenceClient
        token  = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
        client = InferenceClient(token=token)
        result = client.text_to_image(
            prompt=prompt + ", photorealistic, 8k, no people, no faces",
            model="black-forest-labs/FLUX.1-schnell",
        )
        return result if isinstance(result, Image.Image) else Image.open(io.BytesIO(result))
    except Exception:
        return None


# ─── Rich Placeholder Generator ───────────────────────────────────────────────

def _styled_placeholder(
    horizon: str,
    sim_data: dict,
    scores: dict,
    behavior: dict,
    prompt: str,
) -> Image.Image:
    W, H = 768, 512
    fin  = sim_data["fin_condition"]
    pal  = PALETTE.get(fin, PALETTE["Moderate"])
    c1, c2 = pal["bg"]

    canvas = Image.new("RGB", (W, H))
    draw   = ImageDraw.Draw(canvas)

    # ── Background gradient ────────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * t)
        g = int(c1[1] + (c2[1] - c1[1]) * t)
        b = int(c1[2] + (c2[2] - c1[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── Geometric shapes for architectural feel ────────────────────────────
    accent = pal["accent"]
    border = pal["border"]

    # Window-like grid element (top right)
    wx, wy, ww, wh = W - 280, 30, 240, 160
    for row in range(3):
        for col in range(4):
            bx = wx + col * (ww // 4)
            by = wy + row * (wh // 3)
            alpha = 25 + row * 10 + col * 5
            draw.rectangle([bx+3, by+3, bx + ww//4 - 3, by + wh//3 - 3],
                           fill=(*accent, alpha), outline=(*border, 60), width=1)

    # Desk surface suggestion
    desk_y = H - 160
    draw.rectangle([40, desk_y, W - 40, desk_y + 6],
                   fill=(*border, 120))

    # Monitor outline
    mx, mw, mh = W//2 - 120, 240, 150
    draw.rectangle([mx, desk_y - mh - 10, mx + mw, desk_y - 10],
                   outline=(*accent, 180), width=2)
    draw.rectangle([mx + 8, desk_y - mh - 2, mx + mw - 8, desk_y - 18],
                   fill=(*accent, 15))
    draw.rectangle([mx + mw//2 - 20, desk_y - 10, mx + mw//2 + 20, desk_y],
                   fill=(*border, 100))

    # Lamp (Wealthy / Comfortable only)
    if fin in ("Wealthy", "Comfortable"):
        lx, ly = W - 150, desk_y - 120
        draw.line([(lx, desk_y), (lx, ly), (lx + 60, ly - 20)], fill=(*accent, 160), width=2)
        draw.ellipse([lx + 55, ly - 35, lx + 95, ly - 5],
                     fill=(*accent, 40), outline=(*accent, 200))

    # Books / clutter for lower tiers
    if fin in ("Tight", "Struggling"):
        for i in range(6):
            bx = 80 + i * 28
            bh = random.randint(50, 90)
            col = tuple(max(0, c + random.randint(-20, 20)) for c in border)
            draw.rectangle([bx, desk_y - bh, bx + 18, desk_y], fill=col)

    # Plants for healthy tiers
    if fin in ("Wealthy", "Comfortable", "Moderate"):
        px, py = 60, desk_y - 60
        draw.rectangle([px - 15, py + 40, px + 15, py + 65], fill=(60, 40, 20))
        for i in range(7):
            lx = px + random.randint(-30, 30)
            ly = py + random.randint(-10, 40)
            draw.ellipse([lx-8, ly-8, lx+8, ly+8], fill=(20, 120 + i*8, 40))

    # Noise grain overlay
    _add_grain(canvas, 12)

    # ── Text overlay ───────────────────────────────────────────────────────
    draw = ImageDraw.Draw(canvas)  # refresh after grain

    # Bottom info bar
    bar_h = 110
    bar   = Image.new("RGBA", (W, bar_h), (0, 0, 0, 0))
    bar_d = ImageDraw.Draw(bar)
    bar_d.rectangle([0, 0, W, bar_h], fill=(0, 0, 0, 190))
    canvas.paste(Image.fromarray(
        __import__("numpy", fromlist=["array"]).array(bar.convert("RGB"))
    ), (0, H - bar_h))

    try:
        fn_title  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        fn_body   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        fn_small  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        fn_title = fn_body = fn_small = ImageFont.load_default()

    draw.text((24, H - bar_h + 14), HORIZON_LABELS[horizon],
              font=fn_title, fill=pal["accent"])
    draw.text((24, H - bar_h + 44),
              f"{sim_data['career_stability']} Career  ·  {fin} Finances  ·  {sim_data['lifestyle_qual']} Lifestyle",
              font=fn_body, fill=(200, 200, 200))
    draw.text((24, H - bar_h + 68),
              f"Score: {sim_data['composite']}/100  ·  Est. ₹{sim_data['income_lpa']} LPA",
              font=fn_body, fill=(160, 160, 180))

    # Scene label top-left
    scene_el = random.choice(SCENE_ELEMENTS.get(fin, SCENE_ELEMENTS["Moderate"]))
    draw.text((16, 16), f"◈  {scene_el}", font=fn_small, fill=(*pal["accent"], 200))

    # Horizon badge
    icon = CAREER_ICONS.get(sim_data["career_stability"], "○")
    draw.text((W - 60, 16), icon, font=fn_title, fill=pal["accent"])

    # Border
    for t in range(3):
        draw.rectangle([t, t, W - t, H - t], outline=(*pal["border"], 100 - t*20))

    return canvas


def _add_grain(img: Image.Image, intensity: int = 12):
    """In-place grain overlay."""
    try:
        import numpy as np
        arr   = __import__("numpy").array(img).astype("float32")
        noise = __import__("numpy").random.normal(0, intensity, arr.shape)
        arr   = __import__("numpy").clip(arr + noise, 0, 255).astype("uint8")
        img.paste(Image.fromarray(arr))
    except ImportError:
        pass


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_images(
    image_prompts: dict[str, str],
    processed: dict,
    scores: dict,
    behavior: dict,
) -> dict[str, Image.Image | None]:
    """Generate lifestyle environment images for each horizon."""

    from scoring import simulate_future
    simulation = simulate_future(processed, scores, behavior)

    results = {}
    for horizon, prompt in image_prompts.items():
        sim_data = simulation[horizon]

        # Try HF first
        img = _try_hf_generation(prompt)

        # Fallback to placeholder
        if img is None:
            img = _styled_placeholder(horizon, sim_data, scores, behavior, prompt)
        else:
            img = img.resize((768, 512), Image.LANCZOS)

        results[horizon] = img

    return results


def save_outputs(images: dict[str, Image.Image], username: str = "user") -> dict[str, str]:
    """Save images to models/FSVE/<folder>/ with timestamp filenames."""
    saved = {}
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for horizon, img in images.items():
        if img is None:
            continue
        folder = BASE_DIR / FOLDERS[horizon]
        folder.mkdir(parents=True, exist_ok=True)
        fname = f"{username}_{ts}_{horizon}.png"
        path  = folder / fname
        img.save(path)
        saved[horizon] = str(path)
    return saved
