"""Memorize node that prepares candidates for the memory controller."""

from __future__ import annotations

import json
from datetime import datetime

from rich.console import Console

from ..mcp.controller import MemoryController
from ..mcp.stores import EpisodicLog, PreferenceStore, SemanticStore
from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact


MEMORY_CONTROLLER = MemoryController(
    episodic_log=EpisodicLog(),
    semantic_store=SemanticStore(),
    preference_store=PreferenceStore(),
)


def _base_candidates(state: S, timestamp: str) -> list[dict[str, object]]:
    session_id = state.get("session_id", "n/a")
    return [
        {
            "type": "preference",
            "content": f"Preferred explanation style: {state.get('style', 'narrative')}",
            "metadata": {"key": "style", "session": session_id},
            "scores": {"usefulness": 0.7, "generality": 0.6, "recency": 0.8, "stability": 0.5},
        },
        {
            "type": "fix_recipe",
            "content": f"Reflection cadence established at {timestamp}.",
            "metadata": {"session": session_id},
            "scores": {"usefulness": 0.6, "generality": 0.5, "recency": 0.7, "stability": 0.4},
        },
    ]


def _skill_candidates(state: S) -> list[dict[str, object]]:
    explanations = state.get("explanations", {})
    profile = state.get("profile", {})
    skills = {entry.get("name"): entry for entry in profile.get("skills", [])}

    candidates: list[dict[str, object]] = []
    for name, explanation in explanations.items():
        skill = skills.get(name, {})
        gap = float(skill.get("gap", 0.5))
        candidates.append(
            {
                "type": "anchor_fact",
                "content": f"Explanation for {name}: {explanation}",
                "metadata": {"skill": name},
                "scores": {
                    "usefulness": max(0.4, 1 - gap),
                    "generality": 0.5,
                    "recency": 0.6,
                    "stability": max(0.3, 0.8 - gap / 2),
                },
            }
        )
        candidates.append(
            {
                "type": "gap_signature",
                "content": f"Gap for {name}: {gap:.2f}",
                "metadata": {"skill": name},
                "scores": {
                    "usefulness": 0.6 + gap / 2,
                    "generality": 0.4,
                    "recency": 0.7,
                    "stability": 0.3 + (1 - gap) / 2,
                },
            }
        )
    return candidates


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    candidates = _base_candidates(hydrated, timestamp) + _skill_candidates(hydrated)
    candidates.extend(hydrated.get("mem_candidates", []))

    MEMORY_CONTROLLER.propose(candidates)
    reviewed = MEMORY_CONTROLLER.review(limit=10)
    committed_ids = MEMORY_CONTROLLER.commit(hydrated.get("session_id", "session"))

    hydrated["mem_candidates"] = [
        {
            "type": candidate.type,
            "content": candidate.content,
            "metadata": candidate.metadata,
            "score": candidate.score(),
        }
        for candidate in reviewed
    ]
    output_dir = ensure_session_output_dir(hydrated)
    commit_path = output_dir / "memory_commits.json"
    commit_path.write_text(json.dumps(committed_ids, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "memory_commits",
        path=commit_path,
        description="Identifiers of committed memory items.",
        kind="json",
    )

    console.log("Committed %d memory candidates", len(committed_ids))
    return hydrated
