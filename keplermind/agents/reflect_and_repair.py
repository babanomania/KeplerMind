"""Implementation of the Reflection Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class ReflectionAgent(LoggingAgent):
    """Provide meta-level adjustments to the current plan."""

    def __init__(self) -> None:
        super().__init__(name="reflection")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Reviewing assessment outcomes")
        if state.assessments and state.assessments[0]["score"] < 0.8:
            state.plan.append(
                {
                    "step": len(state.plan) + 1,
                    "action": "Schedule targeted review session",
                    "duration_minutes": 15,
                }
            )
            self._append_log(state, "Added remedial plan step")
        return state
