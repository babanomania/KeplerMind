"""Lightweight evaluation utilities for scoring answers."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable, List

from .vectorstore import VectorDocument


def _tokenize(text: str) -> List[str]:
    return [token for token in text.lower().split() if token]


@dataclass
class EvaluationResult:
    """Structured output from the evaluation service."""

    question: str
    score: float
    coverage: float
    reasons: List[str]
    supporting_documents: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


class EvaluationService:
    """Score question coverage against retrieved references."""

    def __init__(self, threshold: float = 0.65) -> None:
        self.threshold = threshold

    def evaluate(
        self, question: str, references: Iterable[VectorDocument]
    ) -> EvaluationResult:
        question_tokens = set(_tokenize(question))
        reference_tokens = set()
        supporting: list[str] = []

        for doc in references:
            supporting.append(doc.document_id)
            reference_tokens.update(_tokenize(doc.content))

        if not question_tokens:
            coverage = 0.0
        else:
            coverage = len(question_tokens & reference_tokens) / len(question_tokens)

        score = round(min(1.0, coverage * 1.2), 2)
        reasons: list[str] = []

        if score >= self.threshold:
            reasons.append("Question is well supported by retrieved references.")
        else:
            reasons.append("Limited alignment between question focus and reference material.")

        if not supporting:
            reasons.append("No reference documents available; expand research scope.")

        return EvaluationResult(
            question=question,
            score=score,
            coverage=round(coverage, 3),
            reasons=reasons,
            supporting_documents=supporting,
        )


__all__ = ["EvaluationResult", "EvaluationService"]
