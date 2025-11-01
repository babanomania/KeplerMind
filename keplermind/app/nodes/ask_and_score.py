"""Questioning node that samples skills and scores learner responses."""

from __future__ import annotations

import random
from collections.abc import Mapping
from pathlib import Path

from rich.console import Console

from ..config.settings import settings
from ..mcp.priors import PriorsRepository, SkillPrior, plan_questions
from ..state import QAResult, S

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
SCORING_GUIDE = (PROMPTS_DIR / "scoring_critic.md").read_text(encoding="utf-8").strip()

QUESTION_PATTERNS = [
    "What core principle defines {skill} when studying {topic}?",
    "How would you apply {skill} for {topic} to reach the goal '{goal}'?",
]


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


def _difficulty(value: object) -> str:
    difficulty = str(value).lower()
    if difficulty not in {"beginner", "intermediate", "advanced"}:
        return "intermediate"
    return difficulty


def _candidate_questions(plan: list[Mapping[str, object]], topic: str, goal: str) -> dict[str, list[str]]:
    pool: dict[str, list[str]] = {}
    for entry in plan:
        skill = str(entry.get("skill", topic))
        for pattern in QUESTION_PATTERNS:
            pool.setdefault(skill, []).append(pattern.format(skill=skill, topic=topic, goal=goal))
    return pool


def _score_answer(answer: str, prior: SkillPrior, difficulty: str, confidence: int) -> tuple[float, str]:
    completeness = min(1.0, len(answer.split()) / 80)
    base = prior.mean()
    difficulty_adjust = {"beginner": 0.1, "intermediate": 0.0, "advanced": -0.05}[difficulty]
    confidence_adjust = (confidence - 3) * 0.05
    score = max(0.1, min(0.95, 0.4 * completeness + 0.4 * base + 0.2 + difficulty_adjust + confidence_adjust))
    rationale = SCORING_GUIDE.splitlines()[0].format(score=f"{score:.2f}")
    return score, rationale


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "the topic")
    goal = hydrated.get("goal", "apply the insights")
    plan = hydrated.get("plan", [])

    repo = _load_priors(hydrated.get("priors"))
    candidates = _candidate_questions(plan, topic, goal)

    rng = random.Random(abs(hash(topic + goal)) % (2**32))
    chosen_skills = plan_questions(candidates.keys(), repo, count=settings.planning.max_questions, rng=rng)
    unique_skills: list[str] = []
    for skill in chosen_skills:
        if skill not in unique_skills:
            unique_skills.append(skill)
    for skill in candidates:
        if len(unique_skills) >= settings.planning.max_questions:
            break
        if skill not in unique_skills:
            unique_skills.append(skill)

    responses = hydrated.get("responses", {})
    confidences = hydrated.get("confidence", {})

    questions: list[str] = []
    qa_pairs: list[QAResult] = []
    skill_scores: dict[str, float] = {}

    for skill in unique_skills[: settings.planning.max_questions]:
        question_bank = candidates.get(skill, [])
        if not question_bank:
            question_bank = [pattern.format(skill=skill, topic=topic, goal=goal) for pattern in QUESTION_PATTERNS]
        question = question_bank.pop(0)
        answer = str(responses.get(question, f"I would explore {skill} within {topic}."))
        confidence = int(confidences.get(question, 3))
        difficulty = next((entry.get("difficulty") for entry in plan if entry.get("skill") == skill), "intermediate")
        difficulty_label = _difficulty(difficulty)
        prior = repo.ensure(skill)
        score, rationale = _score_answer(answer, prior, difficulty_label, confidence)
        prior.update(score)
        skill_scores[skill] = score
        qa_pairs.append(
            {
                "question": question,
                "answer": answer,
                "score": score,
                "skill": skill,
                "confidence": confidence,
                "difficulty": difficulty_label,
                "rationale": rationale,
            }
        )
        questions.append(question)

    hydrated["questions"] = questions
    hydrated["qa"] = qa_pairs
    hydrated["priors"] = repo.as_dict()

    console.log("Scored %d questions across skills: %s", len(qa_pairs), ", ".join(skill_scores))
    return hydrated
