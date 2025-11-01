"""Placeholder RAG builder node."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console

from ..state import S


def run(state: S, *, console: Console | None = None) -> S:
    console = console or Console()
    hydrated: S = dict(state)

    session_id = hydrated.get("session_id", "unknown")
    output_stub = Path("assets/outputs") / f"{session_id}_rag.json"

    hydrated.setdefault("artifacts", {})
    hydrated["artifacts"]["rag_index"] = {
        "path": str(output_stub),
        "description": "Serialized RAG index placeholder.",
        "kind": "json",
    }

    console.log("Prepared RAG artifact at %s", output_stub)
    return hydrated
