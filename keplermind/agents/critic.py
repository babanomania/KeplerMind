"""Implementation of the Critic Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState
from ..tools import EvaluationService, SimpleVectorStore


class CriticAgent(LoggingAgent):
    """Assign scores to generated questions using the evaluation service."""

    def __init__(
        self, evaluation_service: EvaluationService, vector_store: SimpleVectorStore
    ) -> None:
        super().__init__(name="critic")
        self.evaluation_service = evaluation_service
        self.vector_store = vector_store

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Scoring learner responses")
        state.assessments = []

        for question in state.questions:
            references = self.vector_store.similarity_search(question, k=3)
            result = self.evaluation_service.evaluate(question, references)
            state.assessments.append(result.to_dict())

        self._append_log(state, f"Evaluated {len(state.assessments)} questions")
        return state
