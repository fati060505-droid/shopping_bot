"""Step 1: turn free text (a product, specs, or a problem) into a structured search plan."""
from __future__ import annotations

import json
import re

import config

from . import llm

_BUDGET = re.compile(
    r"(?:under|below|less than|max(?:imum)?|budget(?: of| is)?|up to|within|around)\s*(?:rs\.?|usd|[$£€])?\s*(\d[\d,]*(?:\.\d+)?)\s*(k)?",
    re.I,
)
_SPEC = re.compile(r"\b\d+(?:\.\d+)?\s?(?:gb|tb|mah|hz|w|mp|l|inch|in|kg|h|hour)\b|\b[2345]g\b|\bi[3579]\b|\bryzen\s?\d\b", re.I)


def heuristic(text: str) -> dict:
    """Works with no API key. Pulls out a budget and obvious spec tokens."""
    budget = None
    m = _BUDGET.search(text)
    if m:
        budget = float(m.group(1).replace(",", ""))
        if m.group(2):
            budget *= 1000
    query = _BUDGET.sub("", text)
    query = re.sub(r"\s+", " ", query).strip(" ,.") or text
    must = [s.lower().replace("  ", " ") for s in _SPEC.findall(text)]
    return {
        "search_query": query,
        "product_type": "",
        "budget": budget,
        "must_have": must,
        "is_problem": False,
        "summary": "",
    }


def _extract_json(raw: str) -> dict | None:
    match = re.search(r"\{.*\}", raw, re.S)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def parse(text: str, history: list[str] | None = None) -> tuple[dict, str | None]:
    """Returns (intent, warning)."""
    base = heuristic(text)
    if not llm.available():
        return base, None
    context = "\n".join(f"- {h}" for h in (history or [])[-3:]) or "(none)"
    prompt = f"""Turn the shopper's message into a shopping search plan. Reply with JSON only, no prose.

Earlier messages from this shopper (for follow-ups like "make it cheaper"):
{context}

Current message: {text}

JSON keys:
- "search_query": short phrase for a shopping search engine (product + 1-3 key specs)
- "product_type": the product category in 1-3 words
- "budget": maximum price as a number, or null
- "must_have": list of up to 6 short required features or specs (e.g. "16gb ram", "noise cancelling")
- "is_problem": true if the shopper described a problem rather than a product
- "summary": one short sentence on what they need (include the problem if there is one)

If the message is a problem (e.g. "my phone dies by afternoon"), infer the product that would fix it."""
    try:
        raw = llm.run_agent(
            role="Shopping intent analyst",
            goal="Extract a precise product search plan from messy shopper input",
            backstory="You translate vague requests into exact product searches.",
            prompt=prompt,
            model=config.FAST_MODEL,
            max_tokens=350,
        )
        data = _extract_json(raw)
        if not data or not data.get("search_query"):
            return base, "Could not read the AI's plan, so basic parsing was used."
        budget = data.get("budget")
        try:
            budget = float(budget) if budget not in (None, "") else base["budget"]
        except (TypeError, ValueError):
            budget = base["budget"]
        return {
            "search_query": str(data["search_query"])[:120],
            "product_type": str(data.get("product_type", ""))[:60],
            "budget": budget,
            "must_have": [str(x)[:50] for x in (data.get("must_have") or [])][:6] or base["must_have"],
            "is_problem": bool(data.get("is_problem")),
            "summary": str(data.get("summary", ""))[:200],
        }, None
    except Exception as exc:
        return base, f"AI parsing unavailable ({type(exc).__name__}: {str(exc)[:140]}); used basic parsing."
