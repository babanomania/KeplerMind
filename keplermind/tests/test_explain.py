from __future__ import annotations

import json

from rich.console import Console

from keplermind.app.nodes import explain


def test_explain_generates_adaptive_messages(tmp_path) -> None:
    state = {
        "session_id": "test",
        "profile": {
            "skills": [
                {"name": "Foundations", "gap": 0.2, "summary": "solid performance"},
                {"name": "Patterns", "gap": 0.65, "summary": "needs practice"},
            ]
        },
        "sources": [
            {"title": "Paper A"},
            {"title": "Paper B"},
            {"title": "Paper C"},
        ],
        "artifacts": {"output_dir": {"path": str(tmp_path)}},
    }

    result = explain.run(state, console=Console(quiet=True))

    explanations = result["explanations"]
    assert "Foundations" in explanations
    assert "Patterns" in explanations

    light_text = explanations["Foundations"]
    deep_text = explanations["Patterns"]

    assert "Summarize the user's strength" in light_text
    assert "Provide a three-step mini lesson" in deep_text

    path = tmp_path / "explanations.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == explanations
