"""Central configuration. Secrets come from .env, plain settings from settings.env.
On Streamlit Cloud, put the same keys in the app's Secrets panel instead of a .env file."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / "settings.env")
load_dotenv(ROOT / ".env", override=True)


def _secret(name: str) -> str:
    """Read a key from the environment, falling back to Streamlit secrets (cloud deploys)."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


GROQ_API_KEY = _secret("GROQ_API_KEY")
SERPER_API_KEY = _secret("SERPER_API_KEY")
SERPAPI_API_KEY = _secret("SERPAPI_API_KEY")

PRODUCT_SOURCE = os.getenv("PRODUCT_SOURCE", "auto").lower()
SEARCH_COUNTRY = os.getenv("SEARCH_COUNTRY", "us").lower()
SEARCH_LANGUAGE = os.getenv("SEARCH_LANGUAGE", "en").lower()
CURRENCY = os.getenv("CURRENCY_SYMBOL", "$")

FAST_MODEL = os.getenv("FAST_MODEL", "openai/gpt-oss-20b")
SMART_MODEL = os.getenv("SMART_MODEL", "openai/gpt-oss-120b")
FALLBACK_MODELS = [m.strip() for m in os.getenv("FALLBACK_MODELS", "openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3.6-27b").split(",") if m.strip()]
RAG_MODE = os.getenv("RAG_MODE", "semantic").lower()
USE_CREWAI = os.getenv("USE_CREWAI", "false").lower() == "true"

MAX_SEARCHES_PER_SESSION = _int("MAX_SEARCHES_PER_SESSION", 8)
CACHE_TTL_SECONDS = _int("CACHE_TTL_SECONDS", 3600)
RESULTS_PER_SEARCH = _int("RESULTS_PER_SEARCH", 12)
