"""Simplified planning node that produces a fixed set of steps."""

from __future__ import annotations

from rich.console import Console

from ..config.settings import settings
from ..state import S


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "Unknown Topic")
    time_budget = hydrated.get("time_budget", settings.planning.default_time_budget)

    base_steps = [
        {
            "name": "Surface foundations",
            "duration": int(time_budget * 0.2),
            "outcome": "Summarize baseline concepts.",
        },
        {
            "name": "Investigate applications",
            "duration": int(time_budget * 0.3),
            "outcome": "Collect practical examples tied to the goal.",
        },
        {
            "name": "Reflect and question",
            "duration": int(time_budget * 0.2),
            "outcome": "Generate diagnostic questions.",
        },
        {
            "name": "Synthesize insights",
            "duration": int(time_budget * 0.2),
            "outcome": "Derive explanations and key takeaways.",
        },
    ]

    allocated = sum(step["duration"] for step in base_steps)
    final_step = {
        "name": "Plan retention",
        "duration": max(time_budget - allocated, 0),
        "outcome": "Capture follow-up memories.",
    }
    steps = [*base_steps, final_step]

    hydrated["plan"] = steps
    console.log("Generated %d planning steps for topic '%s'", len(steps), topic)
    return hydrated
