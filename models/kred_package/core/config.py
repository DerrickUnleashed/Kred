"""
core/config.py — Centralized configuration manager
Loads all environment variables via python-dotenv.
Single source of truth for all API keys, model names, and constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (or parent dirs)
load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=False)

# ── API Keys ───────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
HF_TOKEN: str = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN", "")

# ── Model Identifiers ──────────────────────────────────────────────────────────
GROQ_MODEL: str = "qwen/qwen3-32b"
FLUX_MODEL: str = "black-forest-labs/FLUX.1-schnell"

# ── LLM Generation Parameters ─────────────────────────────────────────────────
LLM_TEMPERATURE: float = 0.6
LLM_MAX_TOKENS: int = 2048

# ── Retry / Resilience ────────────────────────────────────────────────────────
MAX_RETRIES: int = 3
RETRY_DELAY_SECONDS: float = 1.5   # base delay; doubles each attempt

# ── Image Generation ──────────────────────────────────────────────────────────
IMAGE_WIDTH: int = 800
IMAGE_HEIGHT: int = 520

# ── Output Directories ────────────────────────────────────────────────────────
OUTPUT_DIR: Path = Path("models/FSVE")

# ── LifePath Regret Engine — Financial Constants ──────────────────────────────
ANNUAL_INFLATION_RATE: float = 0.06        # 6% annual inflation (India context)
ANNUAL_INVESTMENT_RETURN: float = 0.12     # 12% CAGR (Nifty 50 long-term avg)
OPPORTUNITY_COST_RATE: float = 0.10        # 10% opportunity cost rate

# ── Validation ────────────────────────────────────────────────────────────────
def validate() -> dict[str, bool]:
    """Returns which keys are configured."""
    return {
        "groq": bool(GROQ_API_KEY),
        "huggingface": bool(HF_TOKEN),
    }
