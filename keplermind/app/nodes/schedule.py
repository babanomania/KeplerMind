"""Schedule node for generating spaced repetition follow-up."""

from __future__ import annotations

import json
from typing import Mapping

from rich.console import Console

from ..mcp.priors import spaced_repetition_schedule
from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact


def _stability_map(profile: Mapping[str, object]) -> dict[str, float]:
    """Infer a stability score for each skill in the profile."""

    skills = profile.get("skills", []) if isinstance(profile, Mapping) else []
    stability: dict[str, float] = {}
    for raw in skills:
        if not isinstance(raw, Mapping):
            continue
        name = str(raw.get("name", "Skill"))
        if not name:
            continue
        if "stability" in raw:
            try:
                score = float(raw["stability"])  # type: ignore[index]
            except (TypeError, ValueError):
                score = 0.5
        else:
            gap = float(raw.get("gap", 0.5) or 0.0)
            score = max(0.1, min(0.95, 1 - gap))
        stability[name] = max(0.0, min(1.0, score))
    return stability


def run(state: S, *, console: Console | None = None) -> S:
    """Create and persist the next review schedule."""

    console = console or Console()
    hydrated: S = dict(state)

    stability = _stability_map(hydrated.get("profile", {}))
    if not stability:
        console.log("No skills available for scheduling; skipping next review plan.")
        hydrated["next_review"] = []
        return hydrated

    schedule = spaced_repetition_schedule(stability)
    hydrated["next_review"] = schedule

    output_dir = ensure_session_output_dir(hydrated)
    schedule_path = output_dir / "next_review.json"
    schedule_path.write_text(json.dumps(schedule, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "next_review",
        path=schedule_path,
        description="Recommended spaced repetition follow-up schedule.",
        kind="json",
    )

    console.log("Generated spaced repetition schedule with %d entries", len(schedule))
    return hydrated

