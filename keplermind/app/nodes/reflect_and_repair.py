"""Simulated reflection loop for the placeholder workflow."""

from __future__ import annotations

from statistics import mean

from rich.console import Console

from ..state import QAResult, S


THRESHOLD = 0.75


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    qa_pairs: list[QAResult] = hydrated.get("qa", [])
    scores = [entry.get("score", 0.0) for entry in qa_pairs]
    avg_score = mean(scores) if scores else 0.0

    needs_repair = avg_score < THRESHOLD
    notes = (
        "Average score below threshold; consider revisiting questions."
        if needs_repair
        else "Scores look healthy; proceed to profiling."
    )

    hydrated["reflection"] = {"needs_repair": needs_repair, "notes": notes}
    console.log("Reflection outcome: avg=%.2f repair=%s", avg_score, needs_repair)
    return hydrated
