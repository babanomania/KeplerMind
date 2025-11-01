"""Reflection node evaluating QA outcomes and planning repairs."""

from __future__ import annotations

from statistics import mean
from pathlib import Path

from rich.console import Console

from ..state import QAResult, S

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
REFLECTION_GUIDE = (PROMPTS_DIR / "reflection_critic.md").read_text(encoding="utf-8").strip()

TARGET_SCORE = 0.7
MIN_UNIQUE_SKILLS = 4


def _needs_repair(scores: list[float], skills: set[str], confidences: list[int]) -> tuple[bool, str]:
    avg_score = mean(scores) if scores else 0.0
    avg_confidence = mean(confidences) if confidences else 0.0
    coverage_ok = len(skills) >= MIN_UNIQUE_SKILLS
    score_ok = avg_score >= TARGET_SCORE and min(scores, default=1.0) >= 0.5
    confidence_ok = avg_confidence >= 2.5
    needs = not (coverage_ok and score_ok and confidence_ok)
    template = REFLECTION_GUIDE.splitlines()[0]
    message = template.format(
        average=avg_score,
        coverage=len(skills),
        confidence=avg_confidence,
        decision="repair" if needs else "proceed",
    )
    return needs, message


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    qa_pairs: list[QAResult] = hydrated.get("qa", [])
    scores = [float(entry.get("score", 0.0)) for entry in qa_pairs]
    confidences = [int(entry.get("confidence", 3)) for entry in qa_pairs]
    skills = {str(entry.get("skill", "")) for entry in qa_pairs if entry.get("skill")}

    needs_repair, notes = _needs_repair(scores, skills, confidences)
    hydrated["reflection"] = {"needs_repair": needs_repair, "notes": notes}

    if needs_repair:
        hydrated.setdefault("mem_candidates", []).append(
            {
                "type": "fix_recipe",
                "content": "Revisit low-scoring skills with targeted scaffolding.",
                "metadata": {"skills": sorted(skills)},
            }
        )

    console.log("Reflection outcome: coverage=%d avg=%.2f repair=%s", len(skills), mean(scores) if scores else 0.0, needs_repair)
    return hydrated
