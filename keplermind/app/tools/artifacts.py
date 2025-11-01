"""Helpers for working with artifact directories."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from ..state import S


def ensure_session_output_dir(state: S) -> Path:
    """Ensure the session has an output directory and return its path."""

    artifacts = state.setdefault("artifacts", {})
    existing = artifacts.get("output_dir")
    if existing and existing.get("path"):
        path = Path(existing["path"])
        path.mkdir(parents=True, exist_ok=True)
        return path

    session_id = state.get("session_id", "session")
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    base_dir = Path("assets/outputs") / f"{timestamp}_{session_id}"
    base_dir.mkdir(parents=True, exist_ok=True)

    artifacts["output_dir"] = {
        "path": str(base_dir),
        "description": "Session output directory.",
    }
    return base_dir


def register_artifact(state: S, name: str, *, path: Path, description: str, kind: str | None = None) -> None:
    artifacts = state.setdefault("artifacts", {})
    entry: dict[str, Any] = {"path": str(path), "description": description}
    if kind:
        entry["kind"] = kind
    artifacts[name] = entry
