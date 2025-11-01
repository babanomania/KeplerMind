"""Profile node aggregating QA scores into a structured summary."""

from __future__ import annotations

import json
from statistics import mean

from rich.console import Console

from ..state import QAResult, S
from ..tools.artifacts import ensure_session_output_dir, register_artifact


LEVELS = [
    (0.0, 0.4, "beginner"),
    (0.4, 0.7, "intermediate"),
    (0.7, 1.1, "advanced"),
]


def _gap_from_score(score: float) -> float:
    return max(0.0, round(1.0 - min(score, 1.0), 2))


def _infer_level(scores: list[float]) -> str:
    if not scores:
        return "unknown"
    avg = mean(scores)
    for lower, upper, label in LEVELS:
        if lower <= avg < upper:
            return label
    return LEVELS[-1][2]


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    qa_pairs: list[QAResult] = hydrated.get("qa", [])
    scores = [entry.get("score", 0.0) for entry in qa_pairs]

    skill_entries = []
    for index, pair in enumerate(qa_pairs, start=1):
        score = pair.get("score", 0.0)
        gap = _gap_from_score(score)
        skill_entries.append(
            {
                "name": pair.get("question", f"Skill {index}"),
                "gap": gap,
                "level": "advanced" if gap < 0.3 else ("intermediate" if gap < 0.6 else "beginner"),
                "summary": pair.get("rationale", ""),
            }
        )

    profile = {
        "inferred_level": _infer_level(scores),
        "skills": skill_entries,
    }

    hydrated["profile"] = profile

    output_dir = ensure_session_output_dir(hydrated)
    profile_path = output_dir / "profile.json"
    profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "profile",
        path=profile_path,
        description="Structured knowledge profile.",
        kind="json",
    )

    console.log("Profile inferred level: %s", profile["inferred_level"])
    return hydrated
