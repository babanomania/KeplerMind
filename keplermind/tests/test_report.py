from __future__ import annotations

import json

from rich.console import Console

from keplermind.app.nodes import report


def test_report_creates_expected_artifacts(tmp_path) -> None:
    state = {
        "session_id": "test",
        "topic": "Graph Theory",
        "goal": "prepare for interview",
        "level_hint": "intermediate",
        "time_budget": 300,
        "sources": [
            {"title": "Intro to Graphs", "url": "https://example.com/graphs"},
        ],
        "plan": [
            {"name": "Review basics", "outcome": "cover fundamentals", "duration": 120},
        ],
        "qa": [
            {"question": "What is a tree?", "score": 0.8},
        ],
        "explanations": {"Foundations": "Sample explanation."},
        "next_review": [
            {"skill": "Foundations", "stability": 0.6, "review_at": "2024-01-01T00:00:00"},
        ],
        "artifacts": {"output_dir": {"path": str(tmp_path)}},
    }

    result = report.run(state, console=Console(quiet=True))

    artifacts = result["artifacts"]
    report_path = tmp_path / "report.md"
    bibliography_path = tmp_path / "bibliography.json"
    questions_path = tmp_path / "questions.jsonl"

    assert report_path.exists()
    assert bibliography_path.exists()
    assert questions_path.exists()

    content = report_path.read_text(encoding="utf-8")
    assert "## Next Review Plan" in content
    assert "review at" in content

    bibliography = json.loads(bibliography_path.read_text(encoding="utf-8"))
    assert bibliography[0]["title"] == "Intro to Graphs"

    lines = questions_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    assert "report" in artifacts
    assert "bibliography" in artifacts
    assert "questions" in artifacts
