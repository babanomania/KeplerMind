"""Implementation of the Profile Agent."""

from __future__ import annotations

from statistics import mean

from .base import LoggingAgent
from ..state import SessionState


class ProfileAgent(LoggingAgent):
    """Aggregate assessment results into a learner profile."""

    def __init__(self) -> None:
        super().__init__(name="profile")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Aggregating assessment results")
        scores = [entry.get("score", 0.0) for entry in state.assessments]
        if scores:
            average = mean(scores)
        else:
            average = 0.0
        state.profile = {
            "topic": state.topic,
            "average_score": round(average, 2),
            "level": self._infer_level(average),
        }
        return state

    @staticmethod
    def _infer_level(score: float) -> str:
        if score >= 0.8:
            return "advanced"
        if score >= 0.35:
            return "intermediate"
        return "beginner"
