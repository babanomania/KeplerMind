"""Local search integration used by the research agent."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


def _tokenize(text: str) -> List[str]:
    return [token for token in text.lower().split() if token]


@dataclass
class SearchResult:
    """Represents a single search hit."""

    title: str
    url: str
    summary: str
    content: str
    score: float

    def to_dict(self) -> dict:
        return asdict(self)


class LocalSearchService:
    """Provide deterministic search over a curated knowledge base."""

    def __init__(self, dataset_path: Path, default_limit: int = 5) -> None:
        self.dataset_path = dataset_path
        self.default_limit = default_limit
        self._records = self._load_dataset(dataset_path)

    @staticmethod
    def _load_dataset(path: Path) -> List[dict]:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):  # pragma: no cover - defensive
            raise ValueError("Knowledge base must be a list of records")
        return data

    def search(self, query: str, limit: int | None = None) -> List[SearchResult]:
        """Return ranked search results for a query."""

        limit = limit or self.default_limit
        tokens = set(_tokenize(query))
        scored: list[tuple[float, dict]] = []

        for record in self._records:
            record_tokens = set(record.get("keywords", []))
            record_tokens.update(_tokenize(record.get("content", "")))

            if not tokens:
                overlap = 0.0
            else:
                overlap = len(tokens & record_tokens) / len(tokens)

            boosted = overlap
            if query.lower() in record.get("title", "").lower():
                boosted += 0.25

            scored.append((boosted, record))

        scored.sort(key=lambda item: item[0], reverse=True)

        if not scored:
            return []

        top_results = scored[:limit]
        if top_results[0][0] == 0 and len(scored) > limit:
            # Ensure we always provide deterministic output even when overlap is zero.
            top_results = scored[:limit]

        return [
            SearchResult(
                title=record["title"],
                url=record["url"],
                summary=record["summary"],
                content=record.get("content", record["summary"]),
                score=round(score, 3),
            )
            for score, record in top_results
        ]

    def refresh(self) -> None:
        """Reload the knowledge base from disk."""

        self._records = self._load_dataset(self.dataset_path)


__all__ = ["LocalSearchService", "SearchResult"]
