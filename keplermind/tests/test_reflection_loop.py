from __future__ import annotations

from rich.console import Console

from keplermind.app.nodes import ask_and_score, intake, planner, reflect_and_repair, research


def test_reflection_requests_repair_when_scores_low(tmp_path) -> None:
    console = Console(quiet=True)
    state = {
        "session_id": "reflect",
        "topic": "Neural Networks",
        "goal": "prepare a lecture",
        "artifacts": {"output_dir": {"path": str(tmp_path)}},
    }

    state = intake.run(state, console=console)
    state = research.run(state, console=console)
    state = planner.run(state, console=console)
    state = ask_and_score.run(state, console=console)

    for entry in state["qa"]:
        entry["score"] = 0.45
        entry["confidence"] = 2

    state = reflect_and_repair.run(state, console=console)

    reflection = state["reflection"]
    assert reflection["needs_repair"] is True
    assert "repair" in reflection["notes"]

    candidates = state["mem_candidates"]
    assert any(item.get("type") == "fix_recipe" for item in candidates)
