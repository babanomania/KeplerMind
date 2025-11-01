"""Collate placeholder memory candidates."""

from __future__ import annotations

from datetime import datetime

from rich.console import Console

from ..state import S


CANDIDATE_TYPES = ("preference", "anchor_fact", "fix_recipe", "gap_signature")


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    now = datetime.utcnow().isoformat(timespec="seconds")
    explanations = hydrated.get("explanations", {})

    candidates = [
        {
            "type": candidate_type,
            "content": f"{candidate_type.title()} captured at {now} for session {hydrated.get('session_id', 'n/a')}.",
        }
        for candidate_type in CANDIDATE_TYPES
    ]

    for name, explanation in explanations.items():
        candidates.append(
            {
                "type": "anchor_fact",
                "content": f"Explanation for {name}: {explanation}",
            }
        )

    hydrated["mem_candidates"] = candidates
    console.log("Prepared %d memory candidates", len(candidates))
    return hydrated
