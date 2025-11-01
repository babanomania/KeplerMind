"""Simplified research node that fabricates structured sources."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.console import Console

from ..state import S


MOCK_SOURCES = [
    "Key concepts overview",
    "Expert interview digest",
    "Practical applications",
]


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "Unknown Topic")
    timestamp = datetime.utcnow().isoformat(timespec="seconds")

    sources = [
        {
            "title": f"{title} for {topic}",
            "summary": f"High-level summary of {title.lower()} related to {topic}.",
            "retrieved_at": timestamp,
            "url": f"https://example.com/{topic.replace(' ', '-').lower()}/{idx}",
        }
        for idx, title in enumerate(MOCK_SOURCES, start=1)
    ]
    hydrated["sources"] = sources

    console.log("Identified %d placeholder sources", len(sources))
    return hydrated
