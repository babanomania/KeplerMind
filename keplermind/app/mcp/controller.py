"""Memory controller orchestrating propose → review → commit cycles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from . import policies
from .stores import EpisodicLog, PreferenceStore, SemanticStore


@dataclass
class MemoryController:
    """High-level interface encapsulating memory flows."""

    episodic_log: EpisodicLog
    semantic_store: SemanticStore
    preference_store: PreferenceStore
    pending: list[policies.MemoryCandidate] = field(default_factory=list)

    def propose(self, candidates: Iterable[dict[str, Any]]) -> None:
        """Register raw candidates for later review."""

        self.pending.extend(policies.normalize_candidate(candidate) for candidate in candidates)

    def review(self, *, limit: int = 5) -> list[policies.MemoryCandidate]:
        """Score and select the best candidates, updating the pending queue."""

        ranked = sorted(self.pending, key=lambda candidate: candidate.score(), reverse=True)
        self.pending = ranked[:limit]
        return list(self.pending)

    def commit(self, session_id: str) -> list[str]:
        """Persist the reviewed candidates and emit episodic events."""

        committed_ids: list[str] = []
        for candidate in self.pending:
            if candidate.type == "preference":
                key = candidate.metadata.get("key", f"pref_{len(self.preference_store.as_dict()) + 1}")
                self.preference_store.set(key, candidate.content)
                committed_ids.append(f"pref:{key}")
            else:
                doc_id = self.semantic_store.add(candidate.content, metadata={"type": candidate.type, **candidate.metadata})
                committed_ids.append(doc_id)

            self.episodic_log.record(
                session=session_id,
                phase="memorize",
                payload={
                    "type": candidate.type,
                    "score": candidate.score(),
                    "metadata": candidate.metadata,
                },
            )

        self.pending.clear()
        return committed_ids

    def retrieve(self, *, limit: int = 5, query: str | None = None) -> list[dict[str, Any]]:
        """Fetch memories for downstream use."""

        if query:
            documents = self.semantic_store.similarity_search(query, top_k=limit)
        else:
            documents = list(self.semantic_store.all())[:limit]

        return [
            {"id": document.doc_id, "content": document.content, "metadata": document.metadata}
            for document in documents
        ]
