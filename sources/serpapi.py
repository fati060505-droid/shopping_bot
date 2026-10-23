"""SerpApi Google Shopping adapter (https://serpapi.com)."""
import requests

from .models import Product, parse_price, to_float, to_int


def search(query: str, api_key: str, country: str = "us", language: str = "en", limit: int = 12) -> list[Product]:
    resp = requests.get(
        "https://serpapi.com/search.json",
        params={"engine": "google_shopping", "q": query, "gl": country, "hl": language, "api_key": api_key},
        timeout=25,
    )
    resp.raise_for_status()
    items = resp.json().get("shopping_results", [])[:limit]
    products = []
    for item in items:
        link = item.get("product_link") or item.get("link") or ""
        if not link:
            continue
        products.append(
            Product(
                title=item.get("title", "").strip(),
                link=link,
                price=item.get("extracted_price") if item.get("extracted_price") is not None else parse_price(item.get("price")),
                price_text=str(item.get("price", "")),
                store=item.get("source", ""),
                rating=to_float(item.get("rating")),
                reviews=to_int(item.get("reviews")),
                image=item.get("thumbnail", ""),
                snippet=item.get("snippet", "") or item.get("delivery", "") or "",
                features=list(item.get("extensions", []) or []),
            )
        )
    return products
