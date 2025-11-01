"""Implementation of the Planner Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class PlannerAgent(LoggingAgent):
    """Create a high-level learning plan."""

    def __init__(self) -> None:
        super().__init__(name="planner")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Drafting a learning plan")
        if not state.plan:
            state.plan.extend(
                [
                    {"step": 1, "action": "Review foundational concepts", "duration_minutes": 30},
                    {"step": 2, "action": "Study applied examples", "duration_minutes": 40},
                    {"step": 3, "action": "Reflect on knowledge gaps", "duration_minutes": 20},
                ]
            )
        return state
