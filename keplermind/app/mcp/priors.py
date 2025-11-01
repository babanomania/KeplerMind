"""Planning priors and sampling utilities."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable, Mapping


@dataclass
class SkillPrior:
    """Beta prior tracking knowledge about a particular skill."""

    name: str
    alpha: float = 1.0
    beta: float = 1.0

    def mean(self) -> float:
        total = self.alpha + self.beta
        return self.alpha / total if total else 0.0

    def update(self, success: float) -> None:
        self.alpha += success
        self.beta += max(0.0, 1 - success)

    def sample(self, rng: random.Random | None = None) -> float:
        rng = rng or random
        return rng.betavariate(self.alpha, self.beta)


@dataclass
class PriorsRepository:
    """Container mapping skills to their priors."""

    priors: dict[str, SkillPrior] = field(default_factory=dict)

    def ensure(self, name: str) -> SkillPrior:
        if name not in self.priors:
            self.priors[name] = SkillPrior(name=name)
        return self.priors[name]

    def update_from_scores(self, scores: Mapping[str, float]) -> None:
        for skill, score in scores.items():
            self.ensure(skill).update(score)

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {
            name: {"alpha": prior.alpha, "beta": prior.beta}
            for name, prior in self.priors.items()
        }


def thompson_sample(
    skills: Iterable[str],
    priors: PriorsRepository,
    *,
    rng: random.Random | None = None,
) -> list[str]:
    rng = rng or random
    scored = []
    for skill in skills:
        prior = priors.ensure(skill)
        scored.append((prior.sample(rng), skill))
    scored.sort(reverse=True)
    return [skill for _, skill in scored]


def plan_questions(
    skills: Iterable[str],
    priors: PriorsRepository,
    *,
    count: int = 5,
    rng: random.Random | None = None,
) -> list[str]:
    """Select up to ``count`` skills using Thompson sampling."""

    ranked = thompson_sample(skills, priors, rng=rng)
    return ranked[:count]


def spaced_repetition_schedule(
    skills: Mapping[str, float],
    *,
    base: datetime | None = None,
) -> list[dict[str, str]]:
    """Generate a simple spaced repetition plan based on stability."""

    base_time = base or datetime.utcnow()
    schedule = []
    for index, (skill, stability) in enumerate(skills.items(), start=1):
        days = max(1, math.ceil((1 - stability) * 5) + index - 1)
        schedule.append(
            {
                "skill": skill,
                "stability": round(stability, 2),
                "review_at": (base_time + timedelta(days=days)).isoformat(timespec="seconds"),
            }
        )
    return schedule
