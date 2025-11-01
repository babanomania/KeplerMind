"""Implementation of the Research Agent."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .base import LoggingAgent
from ..state import SessionState
from ..tools import LocalSearchService, SearchResult


class ResearchAgent(LoggingAgent):
    """Collect curated research notes using the configured search tool."""

    def __init__(self, search_service: LocalSearchService) -> None:
        super().__init__(name="research")
        self.search_service = search_service

    def _serialize_results(self, results: Iterable[SearchResult]) -> list[dict]:
        serialized = []
        timestamp = datetime.utcnow().isoformat()
        for item in results:
            data = item.to_dict()
            data["retrieved_at"] = timestamp
            serialized.append(data)
        return serialized

    def run(self, state: SessionState) -> SessionState:
        query = state.topic or "Exploratory Learning"
        limit = state.preferences.get("search_result_count")
        self._append_log(state, f"Querying knowledge base for '{query}'")
        results = self.search_service.search(query, limit=limit)
        state.sources = self._serialize_results(results)
        state.notes = [result.summary for result in results]
        self._append_log(state, f"Collected {len(results)} research sources")
        return state
