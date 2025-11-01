from __future__ import annotations

from rich.console import Console

from keplermind.app.config.settings import settings
from keplermind.app.nodes import intake, planner, research


def test_planner_uses_priors_and_sources(tmp_path) -> None:
    console = Console(quiet=True)
    state = {
        "session_id": "plan",
        "topic": "Graph Theory",
        "goal": "teach a workshop",
        "priors": {
            "Foundations": {"alpha": 5.0, "beta": 1.0},
            "Applications": {"alpha": 1.0, "beta": 4.0},
        },
        "artifacts": {"output_dir": {"path": str(tmp_path)}},
    }

    state = intake.run(state, console=console)
    state = research.run(state, console=console)
    state = planner.run(state, console=console)

    plan = state["plan"]
    assert len(plan) == settings.planning.max_questions

    skills = {entry["skill"] for entry in plan}
    assert len(skills) >= 4
    difficulties = {entry["skill"]: entry["difficulty"] for entry in plan}

    assert difficulties["Foundations"] == "advanced"
    assert difficulties["Applications"] == "beginner"

    durations = [entry["duration"] for entry in plan]
    assert all(duration >= 10 for duration in durations)
