"""Implementation of the RAG Builder Agent."""

from __future__ import annotations

from .base import LoggingAgent
from ..state import SessionState


class RAGBuilderAgent(LoggingAgent):
    """Simulate chunking and indexing research notes."""

    def __init__(self) -> None:
        super().__init__(name="rag_builder")

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Embedding research notes into vector store (placeholder)")
        anchor_fact = {
            "chunk_id": len(state.memories) + 1,
            "content": "Condensed summary of collected notes.",
            "metadata": {"topic": state.topic},
        }
        state.memories.append(anchor_fact)
        return state
