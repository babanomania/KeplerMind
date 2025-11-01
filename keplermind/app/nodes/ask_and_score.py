"""Generate placeholder questions and answers for the session."""

from __future__ import annotations

from typing import Iterable

from rich.console import Console

from ..config.settings import settings
from ..state import QAResult, S


QUESTION_TEMPLATES = [
    "What is one foundational idea about {topic}?",
    "How does {topic} support the stated goal?",
    "Describe a real-world scenario where {topic} is applied.",
    "What are common pitfalls when learning {topic}?",
    "Which follow-up action could deepen understanding of {topic}?",
]


def _generate_questions(topic: str, *, limit: int) -> list[str]:
    questions = [template.format(topic=topic) for template in QUESTION_TEMPLATES]
    return questions[:limit]


def _mock_answers(questions: Iterable[str]) -> list[QAResult]:
    results: list[QAResult] = []
    for index, question in enumerate(questions, start=1):
        results.append(
            {
                "question": question,
                "answer": "This is a placeholder answer emphasising reflection.",
                "score": 0.6 + index * 0.05,
                "rationale": "Scores are illustrative until the critic agent exists.",
            }
        )
    return results


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "the topic")
    limit = settings.planning.max_questions

    questions = _generate_questions(topic, limit=limit)
    qa_pairs = _mock_answers(questions)

    hydrated["questions"] = questions
    hydrated["qa"] = qa_pairs

    console.log("Generated %d questions and provisional scores", len(questions))
    return hydrated
