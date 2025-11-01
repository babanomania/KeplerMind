"""Implementation of the Questioning Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class QuestioningAgent(LoggingAgent):
    """Generate formative assessment questions."""

    def __init__(self) -> None:
        super().__init__(name="questioning")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Generating diagnostic questions")
        if not state.questions:
            state.questions.extend(
                [
                    f"What is the core definition of {state.topic}?",
                    f"How does {state.topic} apply in real-world scenarios?",
                    f"Which misconceptions often arise when learning {state.topic}?",
                    f"Describe a challenge that {state.topic} helps resolve.",
                    f"How would you teach {state.topic} to a peer?",
                ]
            )
        return state
