"""Step 3: the advisor writes its own opinion from the ranked data."""
from __future__ import annotations

import config
from rag import kb
from sources.models import Product

from . import llm


def _fmt(p: Product, i: int) -> str:
    rating = f"{p.rating:.1f} stars from {p.reviews} reviews" if p.rating else "no rating"
    price = f"{config.CURRENCY}{p.price:,.0f}" if p.price else "price unknown"
    s = p.scores
    return (
        f"{i}. {p.title} | {price} | {rating} | store: {p.store or 'n/a'} | "
        f"scores price {s.get('price', 0):.2f}, features {s.get('features', 0):.2f}, reviews {s.get('reviews', 0):.2f}"
    )


def fallback(ranked: list[Product], intent: dict, has_key: bool = False) -> str:
    top = ranked[0]
    price = f"{config.CURRENCY}{top.price:,.0f}" if top.price else "an unlisted price"
    rating = f"{top.rating:.1f} stars across {top.reviews:,} reviews" if top.rating else "no rating data"
    text = f"**Best match: {top.title}.** It scored highest on your priorities at {price}, with {rating}."
    if len(ranked) > 1:
        text += f" Runner-up: {ranked[1].title}."
    return text + ("" if has_key else "\n\n*Add a Groq key in `.env` to get the AI advisor's full opinion.*")


def advise(ranked: list[Product], intent: dict, weights: dict, user_text: str) -> tuple[str, str | None]:
    """Returns (markdown, warning)."""
    if not ranked:
        return "I could not find matching products. Try a broader description.", None
    if not llm.available():
        return fallback(ranked, intent), None
    top = ranked[:5]
    tips = "\n\n".join(kb.retrieve(f"{intent.get('product_type', '')} {user_text}", k=2)) or "(none)"
    total = sum(weights.values()) or 1
    w_text = ", ".join(f"{k} {v / total:.0%}" for k, v in weights.items())
    budget = f"Budget: {config.CURRENCY}{intent['budget']:,.0f}." if intent.get("budget") else "No stated budget."
    prompt = f"""A shopper asked: "{user_text}"
Need: {intent.get('summary') or intent.get('search_query')}. {budget}
Their priority weights: {w_text}.

Candidates, already ranked by a formula using those weights:
{chr(10).join(_fmt(p, i) for i, p in enumerate(top, 1))}

Buying-guide notes:
{tips}

Write your own recommendation in Markdown, under 170 words, with this shape:
**My pick: <exact product title>** then 2 sentences on why, citing price, rating and review count.
**Runner-up:** one sentence.
**Watch out:** one honest caveat (for example low review count, over budget, or missing a requested feature).
If your pick differs from the formula's #1, say so and explain why.
Use ONLY the facts above. Never invent specs, prices or reviews."""
    try:
        text = llm.run_agent(
            role="Independent product advisor",
            goal="Give an honest, evidence-based recommendation",
            backstory="You are a candid consumer advocate who trusts data over hype.",
            prompt=prompt,
            model=config.SMART_MODEL,
            max_tokens=450,
        )
        return text.strip(), None
    except Exception as exc:
        msg = f"AI advisor unavailable ({type(exc).__name__}: {str(exc)[:140]}). Showing the formula's pick."
        return fallback(ranked, intent, has_key=True), msg
