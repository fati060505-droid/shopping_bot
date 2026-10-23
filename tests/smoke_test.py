"""Runs offline on demo data: python -m tests.smoke_test"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402

config.PRODUCT_SOURCE = "mock"
config.GROQ_API_KEY = ""

from agents import advisor, intent  # noqa: E402
from ranking.scorer import rank  # noqa: E402
from sources import fetch_products  # noqa: E402
from sources.models import parse_price  # noqa: E402

assert parse_price("$1,299.00") == 1299.0 and parse_price("Rs. 12,999") == 12999.0 and parse_price("n/a") is None

plan, _ = intent.parse("noise cancelling wireless headphones under $150 with 30 hour battery")
assert plan["budget"] == 150.0, plan
products, source, warn = fetch_products(plan["search_query"])
assert source == "mock" and products, (source, warn)

for weights in ({"price": 1, "features": 1, "reviews": 1}, {"price": 5, "features": 1, "reviews": 1}, {"price": 1, "features": 1, "reviews": 5}):
    ranked = rank(list(fetch_products(plan["search_query"])[0]), weights, plan["must_have"], plan["product_type"], plan["budget"])
    print(weights, "->", ranked[0].title, round(ranked[0].total, 3))

text, _ = advisor.advise(ranked, plan, weights, "headphones")
assert "Best match" in text
print("\nAll smoke tests passed.")

# --- model fallback: a retired model must not break the app ---
from agents import llm  # noqa: E402


class _Gone(Exception):
    status_code = 404


calls = []


def fake_call(system, prompt, model, max_tokens):
    calls.append(model)
    if model.startswith("llama"):
        raise _Gone("The model `llama-3.1-8b-instant` does not exist")
    return "ok"


llm._call = fake_call
config.FALLBACK_MODELS = ["openai/gpt-oss-120b"]
assert llm._direct("s", "p", "llama-3.1-8b-instant", 100) == "ok"
assert calls == ["llama-3.1-8b-instant", "openai/gpt-oss-120b"], calls
from sources import mock  # noqa: E402

assert mock.search("scientific calculator") == []
print("Model fallback and empty-demo checks passed.")
