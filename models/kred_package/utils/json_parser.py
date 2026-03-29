"""
utils/json_parser.py — Safe JSON extraction from LLM outputs.

LLMs often wrap JSON in markdown fences or add preamble text.
This module strips all of that and returns clean parsed dicts.
"""

import json
import re
from typing import Any, Optional

from .logger import get_logger

log = get_logger("kred.json_parser")


def extract_json(raw: str, fallback: Optional[dict] = None) -> Any:
    """
    Robustly extract a JSON object or array from an LLM response string.

    Strategy:
      1. Try direct parse first (fast path — model was well-behaved)
      2. Strip ```json ... ``` or ``` ... ``` code fences
      3. Extract first {...} or [...] balanced block via regex
      4. Return `fallback` if all strategies fail

    Args:
        raw:      Raw string from LLM / API response.
        fallback: Value to return if parsing fails entirely.

    Returns:
        Parsed Python object (dict / list) or `fallback`.
    """
    if not raw or not isinstance(raw, str):
        log.warning("extract_json received empty or non-string input.")
        return fallback

    # ── 1. Direct parse ───────────────────────────────────────────────────────
    cleaned = raw.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # ── 2. Strip markdown code fences ─────────────────────────────────────────
    fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
    match = fence_pattern.search(cleaned)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # ── 3. Extract first balanced JSON block ──────────────────────────────────
    for opener, closer in [('{', '}'), ('[', ']')]:
        start = cleaned.find(opener)
        if start == -1:
            continue
        depth = 0
        for i, ch in enumerate(cleaned[start:], start=start):
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start:i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

    # ── 4. Fallback ───────────────────────────────────────────────────────────
    log.error("extract_json: all parsing strategies failed. Raw preview: %s…", cleaned[:200])
    return fallback


def safe_dumps(obj: Any, indent: int = 2) -> str:
    """Serialize to JSON string, handling non-serializable types gracefully."""
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    except Exception as exc:
        log.error("safe_dumps failed: %s", exc)
        return "{}"
