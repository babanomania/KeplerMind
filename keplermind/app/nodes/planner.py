"""Planning node that samples skills via priors and crafts question plans."""

from __future__ import annotations

import random
from collections import Counter
from pathlib import Path
from typing import Mapping

from rich.console import Console

from ..config.settings import settings
from ..mcp.priors import PriorsRepository, SkillPrior, plan_questions
from ..state import S

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
PLANNER_TEMPLATE = (PROMPTS_DIR / "planner.md").read_text(encoding="utf-8").strip()
QUESTION_TEMPLATE = (PROMPTS_DIR / "question_gen.md").read_text(encoding="utf-8").strip()


def _load_priors(raw: Mapping[str, object] | None) -> PriorsRepository:
    repo = PriorsRepository()
    if not isinstance(raw, Mapping):
        return repo
    for name, payload in raw.items():
        alpha = beta = 1.0
        if isinstance(payload, Mapping):
            alpha = float(payload.get("alpha", 1.0))
            beta = float(payload.get("beta", 1.0))
        elif isinstance(payload, (list, tuple)) and len(payload) >= 2:
            alpha = float(payload[0])
            beta = float(payload[1])
        repo.priors[name] = SkillPrior(name=name, alpha=alpha, beta=beta)
    return repo


def _serialize_priors(repo: PriorsRepository) -> dict[str, dict[str, float]]:
    return repo.as_dict()


def _candidate_skills(topic: str, sources: list[Mapping[str, object]]) -> list[str]:
    keywords: list[str] = [topic.title(), "Foundations", "Applications", "Challenges", "Patterns", "Tooling"]
    for source in sources:
        title = str(source.get("title", ""))
        for token in title.replace("-", " ").split():
            cleaned = token.strip().title()
            if len(cleaned) >= 4 and cleaned not in keywords:
                keywords.append(cleaned)
    return keywords


def _difficulty(prior: SkillPrior) -> str:
    mean = prior.mean()
    if mean >= 0.7:
        return "advanced"
    if mean >= 0.4:
        return "intermediate"
    return "beginner"


def _objective(skill: str, topic: str, goal: str) -> str:
    first_line = PLANNER_TEMPLATE.splitlines()[0]
    return first_line.format(skill=skill, topic=topic, goal=goal)


def _question_focus(skill: str, topic: str) -> str:
    first_line = QUESTION_TEMPLATE.splitlines()[0]
    return first_line.format(skill=skill, topic=topic)


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "Unknown Topic")
    goal = hydrated.get("goal", "Improve understanding")
    time_budget = int(hydrated.get("time_budget", settings.planning.default_time_budget))

    repo = _load_priors(hydrated.get("priors"))
    sources = hydrated.get("sources", [])
    candidates = _candidate_skills(topic, sources)

    rng = random.Random(abs(hash(topic)) % (2**32))
    selection = plan_questions(candidates, repo, count=settings.planning.max_questions, rng=rng)
    unique_skills: list[str] = []
    for skill in selection:
        if skill not in unique_skills:
            unique_skills.append(skill)
    for skill in candidates:
        if len(unique_skills) >= settings.planning.max_questions:
            break
        if skill not in unique_skills:
            unique_skills.append(skill)

    for base in ["Foundations", "Applications", "Challenges", "Patterns", "Tooling"]:
        if len(unique_skills) >= settings.planning.max_questions:
            break
        if base not in unique_skills:
            unique_skills.append(base)

    if "Applications" not in unique_skills:
        if len(unique_skills) >= settings.planning.max_questions:
            unique_skills[-1] = "Applications"
        else:
            unique_skills.append("Applications")

    count = max(settings.planning.min_questions, len(unique_skills))
    base_duration = max(10, time_budget // count)

    plan: list[dict[str, object]] = []
    coverage = Counter()
    for index, skill in enumerate(unique_skills[: settings.planning.max_questions], start=1):
        prior = repo.ensure(skill)
        difficulty = _difficulty(prior)
        adjustment = {"beginner": 0.9, "intermediate": 1.0, "advanced": 1.2}[difficulty]
        duration = max(10, int(base_duration * adjustment))
        coverage[skill] += 1
        plan.append(
            {
                "order": index,
                "skill": skill,
                "difficulty": difficulty,
                "duration": duration,
                "objective": _objective(skill, topic, goal),
                "question_focus": _question_focus(skill, topic),
            }
        )

    hydrated["plan"] = plan
    hydrated["priors"] = _serialize_priors(repo)

    console.log(
        "Planner selected %d skills with coverage ≥4 unique: %s",
        len(coverage),
        ", ".join(list(coverage.keys())[:5]),
    )
    return hydrated
