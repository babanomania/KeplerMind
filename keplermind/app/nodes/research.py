"""Research node responsible for gathering and summarising sources."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console

from ..config.settings import settings
from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact
from ..tools.scrape import scrape
from ..tools.search import search

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
HALLUCINATION_GUARD = (PROMPTS_DIR / "hallucination_guard.md").read_text(encoding="utf-8").strip()

MIN_RESULTS = 8


def _summarise(text: str, *, limit: int = 80) -> str:
    words = text.split()
    excerpt = " ".join(words[:limit])
    return excerpt if len(words) <= limit else f"{excerpt} …"


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    topic = hydrated.get("topic", "Unknown Topic")
    backend_pref = hydrated.get("search_backend")

    results = search(
        topic,
        max_results=max(MIN_RESULTS, settings.rag.top_k + 3),
        backend_preference=backend_pref,
    )

    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    sources: list[dict[str, object]] = []
    notes: list[str] = []

    for index, result in enumerate(results, start=1):
        document = scrape(result.url, fallback_text=result.snippet)
        summary = _summarise(document.text)
        guard_hint = "pass" if document.word_count >= 40 else "review"
        note = (
            f"[{index}] {result.title}\n"
            f"Summary: {summary}\n"
            f"Guard: {guard_hint} — {HALLUCINATION_GUARD.splitlines()[0]}"
        )
        notes.append(note)
        sources.append(
            {
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "backend": result.backend,
                "content": document.text,
                "word_count": document.word_count,
                "retrieved_at": timestamp,
                "guard": guard_hint,
            }
        )

    hydrated["sources"] = sources
    hydrated["notes"] = notes

    output_dir = ensure_session_output_dir(hydrated)
    bibliography_path = output_dir / "bibliography.json"
    bibliography_path.write_text(json.dumps(sources, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "bibliography",
        path=bibliography_path,
        description="Collected research sources with metadata.",
        kind="json",
    )

    console.log(
        "Research gathered %d sources using %s backend.",
        len(sources),
        sources[0]["backend"] if sources else "unknown",
    )
    return hydrated
