"""Implementation of the Critic Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class CriticAgent(LoggingAgent):
    """Assign heuristic scores to simulated answers."""

    def __init__(self) -> None:
        super().__init__(name="critic")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Scoring learner responses (simulated)")
        if not state.assessments:
            state.assessments.append(
                {
                    "question": state.questions[0] if state.questions else "",
                    "score": 0.75,
                    "reasons": ["Demonstrated conceptual understanding", "Needs stronger examples"],
                }
            )
        return state
