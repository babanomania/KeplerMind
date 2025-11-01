"""Search integrations used by the research agent."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TYPE_CHECKING, List, Sequence

try:  # pragma: no cover - optional dependency import
    import httpx
except ImportError:  # pragma: no cover - handled gracefully at runtime
    httpx = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - typing only
    import httpx as httpx_module


class SearchError(RuntimeError):
    """Raised when a search provider cannot satisfy a query."""



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


class TavilySearchService:
    """Thin client for the Tavily web search API."""

    default_api_url = "https://api.tavily.com/search"

    def __init__(
        self,
        api_key: str,
        default_limit: int = 5,
        api_url: str | None = None,
        timeout: float = 15.0,
        client: "httpx_module.Client | None" = None,
    ) -> None:
        if httpx is None:
            raise SearchError(
                "httpx is not installed; run 'poetry install' to enable Tavily search"
            )

        if not api_key:
            raise SearchError("TavilySearchService requires an API key")

        self.api_key = api_key
        self.default_limit = default_limit
        self.api_url = api_url or self.default_api_url
        self.timeout = timeout
        self._client = client

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def search(self, query: str, limit: int | None = None) -> List[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": limit or self.default_limit,
        }

        client = self._get_client()

        try:
            response = client.post(self.api_url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network failure
            raise SearchError(f"Tavily request failed: {exc}") from exc

        data = response.json()
        results: Sequence[dict] = data.get("results", []) if isinstance(data, dict) else []

        serialized: list[SearchResult] = []
        for item in results:
            serialized.append(
                SearchResult(
                    title=item.get("title", "Untitled Result"),
                    url=item.get("url", ""),
                    summary=item.get("content", item.get("snippet", "")),
                    content=item.get("content", item.get("snippet", "")),
                    score=float(item.get("score", 0.0)),
                )
            )

        return serialized[: limit or self.default_limit]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None


__all__ = ["LocalSearchService", "SearchError", "SearchResult", "TavilySearchService"]
