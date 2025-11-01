"""Bootstrap the execution state for a KeplerMind session."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from rich.console import Console

from ..state import S


def _default(value: Any, fallback: Any) -> Any:
    return value if value not in (None, "") else fallback


def run(state: S, *, console: Console | None = None) -> S:
    """Populate baseline state fields and derive identifiers."""

    console = console or Console()
    hydrated: S = dict(state)

    session_id = hydrated.get("session_id") or uuid4().hex[:8]
    hydrated["session_id"] = session_id

    hydrated["topic"] = _default(hydrated.get("topic"), "Untitled Topic")
    hydrated["goal"] = _default(hydrated.get("goal"), "Explore and learn")
    hydrated["level_hint"] = _default(hydrated.get("level_hint"), "unspecified")
    hydrated["style"] = _default(hydrated.get("style"), "narrative")
    hydrated["time_budget"] = int(_default(hydrated.get("time_budget"), 300))

    hydrated.setdefault("priors", {})
    hydrated.setdefault("sources", [])
    hydrated.setdefault("notes", [])
    hydrated.setdefault("plan", [])
    hydrated.setdefault("questions", [])
    hydrated.setdefault("qa", [])
    hydrated.setdefault("profile", {"inferred_level": "unknown", "skills": []})
    hydrated.setdefault("explanations", {})
    hydrated.setdefault("mem_candidates", [])
    hydrated.setdefault("artifacts", {})
    hydrated.setdefault("reflection", {"needs_repair": False})

    console.log(
        "Initialized session [bold]%s[/bold] for topic '[cyan]%s[/cyan]'", session_id, hydrated["topic"]
    )
    console.log(
        "Goal: %s · Level hint: %s · Time budget: %ss",
        hydrated["goal"],
        hydrated["level_hint"],
        hydrated["time_budget"],
    )
    console.log("Style preference: %s", hydrated["style"])

    hydrated["artifacts"]["session_log"] = {
        "path": f"assets/outputs/{datetime.utcnow().strftime('%Y%m%d')}/{session_id}_log.txt",
        "description": "Placeholder log path for future persistence.",
        "kind": "log",
    }

    return hydrated
