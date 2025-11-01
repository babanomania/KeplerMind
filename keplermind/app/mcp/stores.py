"""Persistence utilities for the Memory · Control · Planning subsystem."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Sequence


DEFAULT_MEMORY_DIR = Path("keplermind/app/memory")
DEFAULT_MEMORY_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class EpisodicEvent:
    """Representation of an event recorded in the episodic log."""

    id: int
    ts: str
    session: str
    phase: str
    payload: dict[str, Any]


class EpisodicLog:
    """SQLite-backed event log capturing the system lifecycle."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_MEMORY_DIR / "events.sqlite"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                session TEXT NOT NULL,
                phase TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def record(self, *, session: str, phase: str, payload: dict[str, Any]) -> int:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO events (ts, session, phase, payload) VALUES (?, ?, ?, ?)",
                (timestamp, session, phase, json.dumps(payload)),
            )
        return int(cursor.lastrowid)

    def fetch_all(self) -> list[EpisodicEvent]:
        cursor = self._conn.execute("SELECT id, ts, session, phase, payload FROM events ORDER BY id ASC")
        events: list[EpisodicEvent] = []
        for row in cursor.fetchall():
            payload = json.loads(row[4]) if row[4] else {}
            events.append(EpisodicEvent(id=row[0], ts=row[1], session=row[2], phase=row[3], payload=payload))
        return events

    def close(self) -> None:
        self._conn.close()


@dataclass
class SemanticDocument:
    """Simple semantic document stored for retrieval."""

    doc_id: str
    content: str
    metadata: dict[str, Any]


class SemanticStore:
    """In-memory semantic store with naive similarity for tests."""

    def __init__(self) -> None:
        self._documents: list[SemanticDocument] = []

    def add(self, content: str, *, metadata: dict[str, Any] | None = None) -> str:
        doc_id = f"doc_{len(self._documents) + 1}"
        self._documents.append(SemanticDocument(doc_id=doc_id, content=content, metadata=metadata or {}))
        return doc_id

    def similarity_search(self, query: str, *, top_k: int = 5) -> list[SemanticDocument]:
        """Very small TF overlap ranking adequate for unit tests."""

        def _score(text: str) -> int:
            query_tokens = set(query.lower().split())
            return sum(1 for token in query_tokens if token in text.lower())

        ranked = sorted(self._documents, key=lambda doc: _score(doc.content), reverse=True)
        return ranked[:top_k]

    def all(self) -> Sequence[SemanticDocument]:
        return tuple(self._documents)


class PreferenceStore:
    """JSON key/value store used to persist user preferences."""

    def __init__(self, json_path: Path | str | None = None) -> None:
        self.json_path = Path(json_path) if json_path else DEFAULT_MEMORY_DIR / "preferences.json"
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        if self.json_path.exists():
            self._cache = json.loads(self.json_path.read_text(encoding="utf-8"))
        else:
            self._cache = {}

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._flush()

    def update(self, items: Iterable[tuple[str, Any]]) -> None:
        for key, value in items:
            self._cache[key] = value
        self._flush()

    def as_dict(self) -> dict[str, Any]:
        return dict(self._cache)

    def _flush(self) -> None:
        self.json_path.write_text(json.dumps(self._cache, indent=2, sort_keys=True), encoding="utf-8")
