"""Synthetic search helpers with graceful backend fallbacks."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Iterable, List, Sequence


class SearchError(RuntimeError):
    """Base error raised for search failures."""


class BackendUnavailable(SearchError):
    """Raised when a requested backend cannot serve the query."""


@dataclass(frozen=True)
class SearchResult:
    """Structured representation of a search hit."""

    title: str
    url: str
    snippet: str
    backend: str


def _synthetic_results(query: str, *, backend: str, max_results: int) -> list[SearchResult]:
    """Generate deterministic pseudo-results for offline testing."""

    cleaned = "-".join(part.lower() for part in query.split() if part)
    results: list[SearchResult] = []
    for index in range(1, max_results + 1):
        digest = hashlib.sha256(f"{query}|{backend}|{index}".encode("utf-8")).hexdigest()[:10]
        title = f"{query.title()} Insight {index}"
        url = f"https://{backend}.example.com/{cleaned}/{digest}"
        snippet = f"Key takeaway {index} about {query} via {backend}."
        results.append(SearchResult(title=title, url=url, snippet=snippet, backend=backend))
    return results


def _tavily(query: str, *, max_results: int) -> list[SearchResult]:
    if not os.getenv("TAVILY_API_KEY"):
        raise BackendUnavailable("Tavily API key missing; cannot perform online search.")
    return _synthetic_results(query, backend="tavily", max_results=max_results)


def _duckduckgo(query: str, *, max_results: int) -> list[SearchResult]:
    return _synthetic_results(query, backend="duckduckgo", max_results=max_results)


def _backend_cycle(preference: str | None) -> List[str]:
    ordered = []
    if preference and preference != "auto":
        ordered.append(preference.lower())
    for backend in ("tavily", "duckduckgo"):
        if backend not in ordered:
            ordered.append(backend)
    return ordered


def search(
    query: str,
    *,
    max_results: int = 10,
    backend_preference: str | None = None,
) -> list[SearchResult]:
    """Search across available backends, preferring the requested provider."""

    errors: list[str] = []
    for backend in _backend_cycle(backend_preference):
        try:
            if backend == "tavily":
                return _tavily(query, max_results=max_results)
            if backend == "duckduckgo":
                return _duckduckgo(query, max_results=max_results)
        except BackendUnavailable as exc:  # pragma: no cover - error path tested via notes
            errors.append(str(exc))
            continue

    raise BackendUnavailable(
        "; ".join(errors) or "No search backend could satisfy the request."
    )


def snippets(results: Iterable[SearchResult]) -> Sequence[str]:
    """Extract snippets from a collection of results."""

    return [result.snippet for result in results]


__all__ = ["SearchResult", "search", "snippets", "BackendUnavailable", "SearchError"]

