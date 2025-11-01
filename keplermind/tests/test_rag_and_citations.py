from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from keplermind.app.nodes import build_rag, intake, research


def test_research_and_rag_pipeline(tmp_path) -> None:
    console = Console(quiet=True)
    state = {
        "session_id": "test",
        "topic": "Quantum Tunneling",
        "artifacts": {"output_dir": {"path": str(tmp_path)}},
    }

    state = intake.run(state, console=console)
    state = research.run(state, console=console)

    assert len(state["sources"]) >= 8
    assert state["notes"]

    bibliography = Path(state["artifacts"]["bibliography"]["path"])
    assert bibliography.exists()
    with bibliography.open("r", encoding="utf-8") as handle:
        stored = json.load(handle)
    assert stored[0]["title"].startswith("Quantum Tunneling")

    state = build_rag.run(state, console=console)
    rag = state["rag"]
    assert rag["vector_ready"] is True
    assert rag["chunks"], "RAG builder should emit chunks"

    chunk = rag["chunks"][0]
    assert len(chunk["embedding"]) == 12

    rag_path = Path(state["artifacts"]["rag_index"]["path"])
    assert rag_path.exists()
    payload = json.loads(rag_path.read_text(encoding="utf-8"))
    assert payload["meta"]["chunk_size"] >= 900
