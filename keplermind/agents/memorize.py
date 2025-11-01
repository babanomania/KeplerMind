"""Implementation of the Memory Controller Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class MemoryControllerAgent(LoggingAgent):
    """Persist highlights from the session."""

    def __init__(self) -> None:
        super().__init__(name="memory_controller")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Selecting session memories")
        if state.explanation:
            state.memories.append(
                {
                    "type": "explanation_snippet",
                    "content": state.explanation[:120],
                }
            )
        return state
