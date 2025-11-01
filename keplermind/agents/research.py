"""Implementation of the Research Agent."""

from __future__ import annotations

from datetime import datetime

from .base import LoggingAgent
from ..state import SessionState


class ResearchAgent(LoggingAgent):
    """Collect lightweight placeholder research notes."""

    def __init__(self) -> None:
        super().__init__(name="research")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Gathering reference sources")
        if not state.sources:
            state.sources.extend(
                [
                    {
                        "title": f"Primer on {state.topic}",
                        "url": "https://example.com/primer",
                        "summary": "High-level overview compiled for bootstrapping.",
                        "retrieved_at": datetime.utcnow().isoformat(),
                    },
                    {
                        "title": f"Applications of {state.topic}",
                        "url": "https://example.com/applications",
                        "summary": "Key practical scenarios relevant for learners.",
                        "retrieved_at": datetime.utcnow().isoformat(),
                    },
                ]
            )
        if not state.notes:
            state.notes.append(
                "Initial research placeholders. Replace with live retrieval logic when integrating search APIs."
            )
        self._append_log(state, "Research summary prepared")
        return state
