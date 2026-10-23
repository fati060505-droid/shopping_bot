"""Demo data so the whole app runs with zero API keys."""
import json
import re

import config

from .models import Product

_STOP = {"the", "a", "an", "for", "with", "and", "or", "best", "good", "under", "below", "my", "i", "need", "want", "to", "of", "in"}


def search(query: str, limit: int = 12) -> list[Product]:
    data = json.loads((config.ROOT / "data" / "mock_products.json").read_text(encoding="utf-8"))
    words = {w for w in re.findall(r"[a-z0-9]+", query.lower()) if w not in _STOP and len(w) > 1}
    scored = []
    for item in data:
        haystack = " ".join([item["title"], item["category"], " ".join(item.get("tags", []))]).lower()
        hits = sum(1 for w in words if w in haystack)
        scored.append((hits, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    best = scored[0][0] if scored else 0
    if best == 0:
        return []  # nothing in the demo catalog matches
    chosen = [i for h, i in scored if h > 0 and h >= max(1, best - 1)]
    out = []
    for item in chosen[:limit]:
        out.append(
            Product(
                title=item["title"],
                link=item["link"],
                price=item["price"],
                price_text=f"{config.CURRENCY}{item['price']:,.2f}",
                store=item["store"],
                rating=item["rating"],
                reviews=item["reviews"],
                image=item.get("image", ""),
                snippet=item.get("snippet", ""),
                features=item.get("tags", []),
            )
        )
    return out
