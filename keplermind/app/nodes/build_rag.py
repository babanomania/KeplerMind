"""RAG builder node converting research notes into vector chunks."""

from __future__ import annotations

import json

from rich.console import Console

from ..config.settings import settings
from ..state import S
from ..tools.artifacts import ensure_session_output_dir, register_artifact
from ..tools.chunk import chunk_text
from ..tools.embed import DeterministicEmbedder


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    sources = hydrated.get("sources", [])
    embedder = DeterministicEmbedder()

    chunks: list[dict[str, object]] = []
    for source_index, source in enumerate(sources, start=1):
        content = str(source.get("content", ""))
        if not content.strip():
            continue
        prefix = f"src{source_index}"
        windows = chunk_text(
            content,
            chunk_size=settings.rag.chunk_size,
            overlap=settings.rag.chunk_overlap,
            prefix=prefix,
        )
        for window in windows:
            embedding = embedder.embed(window.text)
            chunks.append(
                {
                    "id": window.id,
                    "source": source.get("url", ""),
                    "title": source.get("title", ""),
                    "text": window.text,
                    "start": window.start,
                    "end": window.end,
                    "embedding": embedding,
                }
            )

    hydrated["rag"] = {"chunks": chunks, "vector_ready": bool(chunks)}

    output_dir = ensure_session_output_dir(hydrated)
    rag_path = output_dir / "rag_index.json"
    rag_payload = {"meta": {"chunk_size": settings.rag.chunk_size}, "chunks": chunks}
    rag_path.write_text(json.dumps(rag_payload, indent=2), encoding="utf-8")
    register_artifact(
        hydrated,
        "rag_index",
        path=rag_path,
        description="Vector-ready document chunks.",
        kind="json",
    )

    console.log("RAG builder produced %d chunks", len(chunks))
    return hydrated
