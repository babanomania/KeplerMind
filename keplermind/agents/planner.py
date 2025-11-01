"""Implementation of the Planner Agent."""

from __future__ import annotations

from typing import Optional

from .base import LoggingAgent
from ..state import SessionState
from ..tools import LLMServiceError, OpenAIChatService


class PlannerAgent(LoggingAgent):
    """Create a high-level learning plan."""

    def __init__(self, llm_service: Optional[OpenAIChatService] = None) -> None:
        super().__init__(name="planner")
        self.llm_service = llm_service

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Drafting a learning plan")

        topic = state.topic or "Exploratory Learning"
        goal = state.goal or "Build a working understanding"
        level = state.level_hint

        if self.llm_service is not None:
            try:
                state.plan = self.llm_service.generate_plan(
                    topic=topic,
                    goal=goal,
                    level_hint=level,
                    max_steps=5,
                )
                self._append_log(state, "Generated learning plan with OpenAI")
                return state
            except LLMServiceError as exc:
                self._append_log(state, f"LLM plan generation failed: {exc}")

        if not state.plan:
            state.plan.extend(
                [
                    {"step": 1, "action": f"Review foundational concepts for {topic}", "duration_minutes": 30},
                    {"step": 2, "action": f"Study applied examples related to {goal}", "duration_minutes": 40},
                    {
                        "step": 3,
                        "action": "Reflect on knowledge gaps and outline next questions",
                        "duration_minutes": 20,
                    },
                ]
            )
        return state
