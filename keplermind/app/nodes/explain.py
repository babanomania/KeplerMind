"""Generate lightweight explanations derived from the mock profile."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact
from ..tools.citations import merge_citations

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
LIGHT_TEMPLATE = (PROMPTS_DIR / "explain_light.md").read_text(encoding="utf-8").strip()
DEEP_TEMPLATE = (PROMPTS_DIR / "explain_deep.md").read_text(encoding="utf-8").strip()


def _render_explanation(skill: dict[str, object], sources: list[dict[str, object]]) -> tuple[str, str]:
    name = str(skill.get("name", "Skill"))
    gap = float(skill.get("gap", 0.0))
    summary = str(skill.get("summary", "")).strip()
    template = LIGHT_TEMPLATE if gap < 0.3 else DEEP_TEMPLATE
    body = template.format(skill=name)
    if summary:
        body += f"\n\nReflection: {summary}"
    citation_tokens = [str(source.get("title", "source")) for source in sources][:3]
    citations = merge_citations(citation_tokens)
    return name, f"{body}\n\nSources {citations}"


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    explanations: dict[str, str] = {}
    profile = hydrated.get("profile", {})
    skills = profile.get("skills", [])
    sources = hydrated.get("sources", [])

    for skill in skills:
        name, message = _render_explanation(skill, sources)
        explanations[name] = message

    hydrated["explanations"] = explanations

    output_dir = ensure_session_output_dir(hydrated)
    explanations_path = output_dir / "explanations.json"
    explanations_path.write_text(json.dumps(explanations, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "explanations",
        path=explanations_path,
        description="Skill-specific explanation snippets.",
        kind="json",
    )

    console.log("Generated %d explanation snippets", len(explanations))
    return hydrated
