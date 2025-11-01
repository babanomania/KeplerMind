"""Retention and scoring policies for memory candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

WEIGHTS = {
    "usefulness": 0.45,
    "generality": 0.25,
    "recency": 0.15,
    "stability": 0.15,
}

MAX_CONTENT_LENGTH = 240
SENSITIVE_TOKENS = {"password", "secret", "token"}


@dataclass
class MemoryCandidate:
    """Normalized representation of a candidate memory item."""

    type: str
    content: str
    metadata: dict[str, Any]
    scores: dict[str, float]

    def score(self) -> float:
        return score_candidate(self.scores)


def score_candidate(scores: dict[str, float]) -> float:
    """Compute weighted score, clamping each dimension to [0, 1]."""

    total = 0.0
    for key, weight in WEIGHTS.items():
        value = max(0.0, min(float(scores.get(key, 0.0)), 1.0))
        total += weight * value
    return round(total, 3)


def summarize_content(content: str) -> str:
    """Truncate overly long content for storage."""

    if len(content) <= MAX_CONTENT_LENGTH:
        return content
    return content[: MAX_CONTENT_LENGTH - 3] + "..."


def redact_sensitive(content: str) -> str:
    """Replace obvious sensitive tokens with placeholders."""

    sanitized = content
    for token in SENSITIVE_TOKENS:
        sanitized = sanitized.replace(token, "[redacted]")
    return sanitized


def normalize_candidate(candidate: dict[str, Any]) -> MemoryCandidate:
    text = summarize_content(redact_sensitive(candidate.get("content", "")))
    metadata = dict(candidate.get("metadata", {}))
    scores = {k: float(v) for k, v in candidate.get("scores", {}).items()}
    return MemoryCandidate(
        type=candidate.get("type", "unknown"),
        content=text,
        metadata=metadata,
        scores=scores,
    )


def select_top_candidates(candidates: Iterable[dict[str, Any]], limit: int = 5) -> list[MemoryCandidate]:
    """Return the best scoring candidates, preserving stable ordering."""

    normalized = [normalize_candidate(candidate) for candidate in candidates]
    ranked = sorted(normalized, key=lambda c: c.score(), reverse=True)
    return ranked[:limit]
