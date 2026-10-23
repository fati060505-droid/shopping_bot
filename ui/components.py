"""HTML pieces. Everything user- or web-supplied is escaped. Strings are built flat (no indentation)
so Streamlit's markdown never mistakes them for code blocks."""
from __future__ import annotations

import html

import config


def _stars(rating: float | None) -> str:
    if not rating:
        return ""
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


def _safe_link(url: str) -> str:
    return html.escape(url, quote=True) if url.startswith(("http://", "https://")) else "#"


def _bar(label: str, value: float, cls: str) -> str:
    pct = int(round(max(0, min(1, value)) * 100))
    return (
        f'<div class="bar"><div class="lab"><span>{label}</span><span>{pct}</span></div>'
        f'<div class="track"><div class="fill {cls}" style="width:{pct}%"></div></div></div>'
    )


def product_card(p: dict, rank: int) -> str:
    top = rank == 1
    price = html.escape(p.get("price_text") or (f"{config.CURRENCY}{p['price']:,.0f}" if p.get("price") else "Price not listed"))
    rating = p.get("rating")
    reviews = p.get("reviews") or 0
    review_txt = f'<span class="stars">{_stars(rating)}</span> {rating:.1f} ({reviews:,} reviews)' if rating else "No reviews yet"
    img = html.escape(p.get("image", ""), quote=True)
    thumb = f'<div class="thumb" style="background-image:url(\'{img}\')"></div>' if img.startswith("http") else ""
    s = p.get("scores", {})
    bars = (
        '<div class="bars">'
        + _bar("Price", s.get("price", 0), "f-price")
        + _bar("Features", s.get("features", 0), "f-features")
        + _bar("Reviews", s.get("reviews", 0), "f-reviews")
        + "</div>"
    )
    store = html.escape(p.get("store") or "Store")
    return (
        f'<div class="card{" top" if top else ""}">'
        + ('<span class="ribbon">Top pick</span>' if top else "")
        + f'<div class="rank">{rank}</div>{thumb}'
        + f'<div class="body"><div class="ttl">{html.escape(p.get("title", ""))}</div>'
        + f'<div class="meta">{store} · {review_txt}</div>'
        + f'<div class="price">{price}<span class="score">Match {p.get("total", 0) * 100:.0f}%</span></div>'
        + bars
        + f'<a class="cta" href="{_safe_link(p.get("link", ""))}" target="_blank" rel="noopener noreferrer">View at {store}</a>'
        + "</div></div>"
    )


def intent_chips(intent: dict) -> str:
    chips = []
    if intent.get("product_type"):
        chips.append(f"Looking for: {intent['product_type']}")
    if intent.get("budget"):
        chips.append(f"Budget: {config.CURRENCY}{intent['budget']:,.0f}")
    chips += [str(x) for x in intent.get("must_have", [])]
    if not chips:
        return ""
    return '<div class="intent">' + "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips) + "</div>"


def source_badge(source: str) -> str:
    if source == "mock":
        return '<span class="badge demo">Demo data</span>'
    return f'<span class="badge live">Live: {html.escape(source)}</span>'
