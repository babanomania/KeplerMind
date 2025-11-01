"""Generate lightweight explanations derived from the mock profile."""

from __future__ import annotations

from rich.console import Console

from ..state import S


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    explanations: dict[str, str] = {}
    profile = hydrated.get("profile", {})
    skills = profile.get("skills", [])

    for skill in skills:
        name = skill.get("name", "Skill")
        gap = skill.get("gap", 0.0)
        if gap < 0.3:
            style = "light"
            content = f"Quick recap for '{name}': consolidate strengths with spaced practice."
        else:
            style = "deep"
            content = f"Deep dive for '{name}': revisit fundamentals and apply them to new scenarios."
        explanations[name] = f"[{style}] {content}"

    hydrated["explanations"] = explanations
    console.log("Generated %d explanation snippets", len(explanations))
    return hydrated
