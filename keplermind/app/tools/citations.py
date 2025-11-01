"""Utility helpers for inline citation formatting."""

from __future__ import annotations

from typing import Iterable


def merge_citations(sources: Iterable[str]) -> str:
    """Return a consolidated citation string."""

    cleaned = [source.strip() for source in sources if source.strip()]
    if not cleaned:
        return "[citation needed]"
    if len(cleaned) == 1:
        return f"[{cleaned[0]}]"
    return "[" + "; ".join(cleaned) + "]"
