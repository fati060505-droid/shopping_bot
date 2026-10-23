"""Product source selection. All adapters return a list[Product]."""
from __future__ import annotations

import config

from . import mock, serper, serpapi
from .models import Product


def active_source() -> str:
    pref = config.PRODUCT_SOURCE
    if pref == "serper" and config.SERPER_API_KEY:
        return "serper"
    if pref == "serpapi" and config.SERPAPI_API_KEY:
        return "serpapi"
    if pref == "mock":
        return "mock"
    if config.SERPER_API_KEY:
        return "serper"
    if config.SERPAPI_API_KEY:
        return "serpapi"
    return "mock"


def fetch_products(query: str) -> tuple[list[Product], str, str | None]:
    """Returns (products, source_used, warning). Falls back to demo data if a live call fails."""
    source = active_source()
    limit = config.RESULTS_PER_SEARCH
    try:
        if source == "serper":
            items = serper.search(query, config.SERPER_API_KEY, config.SEARCH_COUNTRY, config.SEARCH_LANGUAGE, limit)
        elif source == "serpapi":
            items = serpapi.search(query, config.SERPAPI_API_KEY, config.SEARCH_COUNTRY, config.SEARCH_LANGUAGE, limit)
        else:
            return mock.search(query, limit), "mock", None
        if items:
            return items, source, None
        return mock.search(query, limit), "mock", f"{source} returned no results, showing demo data instead."
    except Exception as exc:  # network, quota, bad key
        return mock.search(query, limit), "mock", f"Live search failed ({type(exc).__name__}). Showing demo data instead."
