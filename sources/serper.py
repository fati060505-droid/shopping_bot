"""Serper.dev Google Shopping adapter (https://serper.dev)."""
import requests

from .models import Product, parse_price, to_float, to_int


def search(query: str, api_key: str, country: str = "us", language: str = "en", limit: int = 12) -> list[Product]:
    resp = requests.post(
        "https://google.serper.dev/shopping",
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json={"q": query, "gl": country, "hl": language, "num": limit},
        timeout=20,
    )
    resp.raise_for_status()
    items = resp.json().get("shopping", [])
    products = []
    for item in items:
        link = item.get("link") or ""
        if not link:
            continue
        products.append(
            Product(
                title=item.get("title", "").strip(),
                link=link,
                price=parse_price(item.get("price")),
                price_text=str(item.get("price", "")),
                store=item.get("source", ""),
                rating=to_float(item.get("rating")),
                reviews=to_int(item.get("ratingCount")),
                image=item.get("imageUrl", ""),
                snippet=item.get("delivery", "") or "",
            )
        )
    return products
