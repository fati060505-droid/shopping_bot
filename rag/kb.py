"""Tiny RAG over markdown files in rag/kb/. No database: chunks are embedded in memory at startup.
Uses fastembed (ONNX, free, local) when installed, otherwise falls back to keyword scoring."""
from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from pathlib import Path

import config

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
KB_DIR = Path(__file__).parent / "kb"


def _chunks() -> list[dict]:
    out = []
    for path in sorted(KB_DIR.glob("*.md")):
        topic = path.stem.replace("_", " ")
        for block in re.split(r"\n(?=## )", path.read_text(encoding="utf-8")):
            block = block.strip()
            if len(block) > 40:
                out.append({"topic": topic, "text": block})
    return out


def _tok(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@lru_cache(maxsize=1)
def _index():
    chunks = _chunks()
    try:
        if config.RAG_MODE == "keyword":
            raise RuntimeError("keyword mode")
        import numpy as np
        from fastembed import TextEmbedding

        model = TextEmbedding("BAAI/bge-small-en-v1.5")
        vecs = np.array(list(model.embed([c["topic"] + " " + c["text"] for c in chunks])))
        vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
        return {"mode": "semantic", "chunks": chunks, "vecs": vecs, "model": model}
    except Exception:
        return {"mode": "keyword", "chunks": chunks}


def retrieve(query: str, k: int = 2) -> list[str]:
    """Return up to k relevant buying-guide snippets for the query."""
    idx = _index()
    chunks = idx["chunks"]
    if not chunks:
        return []
    if idx["mode"] == "semantic":
        import numpy as np

        q = np.array(list(idx["model"].embed([query])))[0]
        q = q / np.linalg.norm(q)
        sims = idx["vecs"] @ q
        order = np.argsort(-sims)[:k]
        return [chunks[i]["text"] for i in order if sims[i] > 0.35]
    qt = set(_tok(query))
    scored = []
    for c in chunks:
        ct = _tok(c["topic"] + " " + c["text"])
        overlap = sum(1 for t in ct if t in qt)
        scored.append((overlap / math.sqrt(len(ct) + 1), c["text"]))
    scored.sort(reverse=True)
    return [text for score, text in scored[:k] if score > 0.05]
