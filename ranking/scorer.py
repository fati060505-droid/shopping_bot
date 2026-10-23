"""Deterministic ranking: price, features and reviews, each scored 0-1, then weighted."""
from __future__ import annotations

import re
from statistics import mean

from sources.models import Product

REVIEW_PRIOR_WEIGHT = 50  # a product needs roughly this many reviews before its own rating dominates


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _price_scores(products: list[Product], budget: float | None) -> list[float]:
    prices = [p.price for p in products if p.price]
    if not prices:
        return [0.5] * len(products)
    lo, hi = min(prices), max(prices)
    scores = []
    for p in products:
        if not p.price:
            scores.append(0.3)  # unknown price is a mild penalty
            continue
        base = 1.0 if hi == lo else 1 - (p.price - lo) / (hi - lo)
        if budget and p.price > budget:
            base *= 0.4  # over budget is hit hard
        elif budget and p.price <= budget:
            base = 0.35 + 0.65 * base  # within budget never scores near zero
        scores.append(max(0.0, min(1.0, base)))
    return scores


def _review_scores(products: list[Product]) -> list[float]:
    rated = [p.rating for p in products if p.rating]
    prior = mean(rated) if rated else 4.0
    scores = []
    for p in products:
        if not p.rating:
            scores.append(0.4)
            continue
        v = max(p.reviews, 0)
        bayes = (v / (v + REVIEW_PRIOR_WEIGHT)) * p.rating + (REVIEW_PRIOR_WEIGHT / (v + REVIEW_PRIOR_WEIGHT)) * prior
        scores.append(max(0.0, min(1.0, (bayes - 1) / 4)))  # map 1-5 stars onto 0-1
    return scores


def _feature_scores(products: list[Product], wanted: list[str], product_type: str) -> list[float]:
    terms = [w.lower().strip() for w in wanted if w and w.strip()]
    if not terms:
        terms = [product_type.lower()] if product_type else []
    if not terms:
        return [0.5] * len(products)
    scores = []
    for p in products:
        text, toks = p.text, _tokens(p.text)
        hit = 0.0
        for term in terms:
            if term in text:
                hit += 1
            else:
                words = _tokens(term)
                if words:
                    hit += 0.6 * len(words & toks) / len(words)  # partial credit
        scores.append(min(1.0, hit / len(terms)))
    return scores


def rank(products: list[Product], weights: dict, must_have: list[str], product_type: str = "", budget: float | None = None) -> list[Product]:
    if not products:
        return []
    total_w = sum(max(v, 0) for v in weights.values()) or 1.0
    w = {k: max(v, 0) / total_w for k, v in weights.items()}
    price_s = _price_scores(products, budget)
    review_s = _review_scores(products)
    feat_s = _feature_scores(products, must_have, product_type)
    for p, ps, fs, rs in zip(products, price_s, feat_s, review_s):
        p.scores = {"price": ps, "features": fs, "reviews": rs}
        p.total = w["price"] * ps + w["features"] * fs + w["reviews"] * rs
    return sorted(products, key=lambda p: p.total, reverse=True)
