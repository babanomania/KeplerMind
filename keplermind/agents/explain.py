"""Implementation of the Explanation Agent."""

from __future__ import annotations

from textwrap import dedent

from .base import LoggingAgent
from ..state import SessionState


class ExplanationAgent(LoggingAgent):
    """Produce a textual explanation for the learner."""

    def __init__(self) -> None:
        super().__init__(name="explanation")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Drafting learner-facing explanation")
        state.explanation = dedent(
            f"""
            ## Understanding {state.topic}

            {state.topic} plays a central role in contemporary learning trajectories. This
            placeholder explanation illustrates where to surface citations once the system is
            integrated with live retrieval.
            """
        ).strip()
        return state
