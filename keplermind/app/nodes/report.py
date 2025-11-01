"""Produce a minimal session report and register artifact paths."""

from __future__ import annotations

import json

from rich.console import Console

from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact


REPORT_TEMPLATE = """# KeplerMind Session Report

**Topic:** {topic}
**Goal:** {goal}
**Level Hint:** {level}
**Time Budget:** {time_budget}s

## Key Sources
{source_lines}

## Plan Summary
{plan_lines}

## Questions & Scores
{qa_lines}

## Explanations
{explanation_lines}

## References
{references}
"""


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    session_id = hydrated.get("session_id", "session")
    output_dir = ensure_session_output_dir(hydrated)

    source_lines = "\n".join(
        f"- {src.get('title', 'Source')} ({src.get('url', 'n/a')})" for src in hydrated.get("sources", [])
    ) or "- No sources captured"

    plan_lines = "\n".join(
        f"- {step.get('name', 'Step')} → {step.get('outcome', '')} ({step.get('duration', 0)}s)"
        for step in hydrated.get("plan", [])
    ) or "- No plan generated"

    qa_lines = "\n".join(
        f"- {qa.get('question', 'Q')} — score {qa.get('score', 0):.2f}"
        for qa in hydrated.get("qa", [])
    ) or "- No questions asked"

    explanation_lines = "\n".join(
        f"- {name}: {content}" for name, content in hydrated.get("explanations", {}).items()
    ) or "- No explanations"

    report_content = REPORT_TEMPLATE.format(
        topic=hydrated.get("topic", "Unknown"),
        goal=hydrated.get("goal", "Undefined"),
        level=hydrated.get("level_hint", "unspecified"),
        time_budget=hydrated.get("time_budget", 0),
        source_lines=source_lines,
        plan_lines=plan_lines,
        qa_lines=qa_lines,
        explanation_lines=explanation_lines,
        references=source_lines,
    )

    report_path = output_dir / "report.md"
    report_path.write_text(report_content, encoding="utf-8")

    register_artifact(
        hydrated,
        "report",
        path=report_path,
        description="Markdown session report.",
        kind="text",
    )

    questions_path = output_dir / "questions.jsonl"
    with questions_path.open("w", encoding="utf-8") as handle:
        for qa in hydrated.get("qa", []):
            handle.write(json.dumps(qa) + "\n")
    register_artifact(
        hydrated,
        "questions",
        path=questions_path,
        description="Q&A trace in JSONL format.",
        kind="json",
    )

    bibliography_path = output_dir / "bibliography.json"
    bibliography_path.write_text(json.dumps(hydrated.get("sources", []), indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "bibliography",
        path=bibliography_path,
        description="Source catalogue for the session.",
        kind="json",
    )

    console.log("Report saved to %s", report_path)
    return hydrated
