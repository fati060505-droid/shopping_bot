from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict


@dataclass
class Product:
    title: str
    link: str
    price: float | None = None
    price_text: str = ""
    store: str = ""
    rating: float | None = None
    reviews: int = 0
    image: str = ""
    snippet: str = ""
    features: list[str] = field(default_factory=list)
    # filled in by the ranking step
    scores: dict = field(default_factory=dict)
    total: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def text(self) -> str:
        return " ".join([self.title, self.snippet, " ".join(self.features)]).lower()


_NUM = re.compile(r"\d[\d,]*\.?\d*")


def parse_price(raw) -> float | None:
    """'$1,299.00', 'Rs. 12,999', '1299' -> float. Returns None when no number is found."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    match = _NUM.search(str(raw))
    if not match:
        return None
    try:
        return float(match.group().replace(",", ""))
    except ValueError:
        return None


def to_int(raw) -> int:
    if raw is None:
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    digits = re.sub(r"[^\d]", "", str(raw))
    return int(digits) if digits else 0


def to_float(raw) -> float | None:
    try:
        return float(raw) if raw not in (None, "") else None
    except (TypeError, ValueError):
        return None
