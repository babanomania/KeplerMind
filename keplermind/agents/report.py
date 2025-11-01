"""Implementation of the Reporter Agent."""

from __future__ import annotations

from textwrap import dedent

from .base import LoggingAgent
from ..state import SessionState


class ReporterAgent(LoggingAgent):
    """Compile a structured session report."""

    def __init__(self) -> None:
        super().__init__(name="reporter")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Assembling final report")
        plan_summary = "\n".join(
            f"- Step {item['step']}: {item['action']} ({item['duration_minutes']} min)"
            for item in state.plan
        )
        state.report = dedent(
            f"""
            # KeplerMind Session Report

            **Topic:** {state.topic}
            **Goal:** {state.goal}
            **Estimated Level:** {state.profile.get('level', 'unknown')}

            ## Plan
            {plan_summary}

            ## Explanation
            {state.explanation}

            ## Next Review
            - Scheduled for: {state.schedule.get('next_review_at', 'TBD')}
            - Interval (days): {state.schedule.get('interval_days', 'TBD')}
            """
        ).strip()
        return state
