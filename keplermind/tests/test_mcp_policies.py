from __future__ import annotations

import math

from keplermind.app.mcp import policies


def test_score_candidate_clamps_values() -> None:
    raw_scores = {"usefulness": 2, "generality": -1, "recency": 0.5, "stability": 0.75}
    score = policies.score_candidate(raw_scores)
    expected = round(0.45 * 1.0 + 0.25 * 0.0 + 0.15 * 0.5 + 0.15 * 0.75, 3)
    assert math.isclose(score, expected)


def test_summarize_and_redact() -> None:
    content = "secret token password" + "x" * 260
    summarized = policies.summarize_content(content)
    assert len(summarized) <= policies.MAX_CONTENT_LENGTH
    redacted = policies.redact_sensitive(content)
    assert "secret" not in redacted and "token" not in redacted and "password" not in redacted


def test_select_top_candidates_orders_by_score() -> None:
    candidates = [
        {"type": "anchor_fact", "content": "A", "scores": {"usefulness": 0.9, "generality": 0.2, "recency": 0.2, "stability": 0.2}},
        {"type": "anchor_fact", "content": "B", "scores": {"usefulness": 0.4, "generality": 0.9, "recency": 0.9, "stability": 0.9}},
        {"type": "anchor_fact", "content": "C", "scores": {"usefulness": 0.5, "generality": 0.5, "recency": 0.5, "stability": 0.5}},
    ]

    ranked = policies.select_top_candidates(candidates, limit=2)
    assert [candidate.content for candidate in ranked] == ["B", "A"]
