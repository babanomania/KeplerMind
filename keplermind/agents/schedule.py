"""Implementation of the Scheduler Agent."""

from __future__ import annotations

from datetime import datetime, timedelta

from .base import LoggingAgent
from ..state import SessionState


class SchedulerAgent(LoggingAgent):
    """Plan follow-up reviews."""

    def __init__(self) -> None:
        super().__init__(name="scheduler")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Creating spaced repetition schedule")
        now = datetime.utcnow()
        state.schedule = {
            "next_review_at": (now + timedelta(days=2)).isoformat(),
            "interval_days": 2,
        }
        return state
