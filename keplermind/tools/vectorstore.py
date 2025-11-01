"""Lightweight vector store for semantic lookups."""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Dict, List, Sequence


def _tokenize(text: str) -> List[str]:
    return [token for token in text.lower().split() if token]


def _fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def _cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    numerator = sum(a[token] * b[token] for token in common)
    if numerator == 0:
        return 0.0
    sum_a = sum(value * value for value in a.values())
    sum_b = sum(value * value for value in b.values())
    denominator = math.sqrt(sum_a) * math.sqrt(sum_b)
    if denominator == 0:
        return 0.0
    return numerator / denominator


@dataclass
class VectorDocument:
    """Entry returned from a vector store lookup."""

    document_id: str
    content: str
    metadata: Dict[str, object]
    score: float


class SimpleVectorStore:
    """Naive vector store backed by cosine similarity over bag-of-words."""

    def __init__(self, persist_path: Path | None = None) -> None:
        self.persist_path = persist_path
        self._documents: Dict[str, dict] = {}
        self._index: Dict[str, Counter] = {}
        self._fingerprints: Dict[str, str] = {}
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if not self.persist_path or not self.persist_path.exists():
            return

        with self.persist_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        documents = payload.get("documents", [])
        self._next_id = int(payload.get("next_id", 1))

        for entry in documents:
            doc_id = str(entry["id"])
            content = entry["content"]
            metadata = entry.get("metadata", {})
            self._documents[doc_id] = {"content": content, "metadata": metadata}
            self._index[doc_id] = Counter(_tokenize(content))
            self._fingerprints[_fingerprint(content)] = doc_id

    def _persist(self) -> None:
        if not self.persist_path:
            return

        data = {
            "next_id": self._next_id,
            "documents": [
                {
                    "id": doc_id,
                    "content": payload["content"],
                    "metadata": payload.get("metadata", {}),
                }
                for doc_id, payload in self._documents.items()
            ],
        }

        with self.persist_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def add_documents(
        self, documents: Sequence[str], metadata: Sequence[Dict[str, object]]
    ) -> List[str]:
        """Store documents in the vector store and return their identifiers."""

        if len(documents) != len(metadata):  # pragma: no cover - defensive
            raise ValueError("documents and metadata must be the same length")

        stored_ids: list[str] = []

        for text, meta in zip(documents, metadata):
            cleaned = text.strip()
            if not cleaned:
                continue
            fingerprint = _fingerprint(cleaned)
            existing = self._fingerprints.get(fingerprint)
            if existing:
                stored_ids.append(existing)
                continue

            doc_id = str(self._next_id)
            self._next_id += 1
            self._documents[doc_id] = {"content": cleaned, "metadata": dict(meta)}
            self._index[doc_id] = Counter(_tokenize(cleaned))
            self._fingerprints[fingerprint] = doc_id
            stored_ids.append(doc_id)

        self._persist()
        return stored_ids

    def similarity_search(self, query: str, k: int = 3) -> List[VectorDocument]:
        """Return the ``k`` most similar documents for a query."""

        tokens = Counter(_tokenize(query))
        scored: list[VectorDocument] = []

        for doc_id, payload in self._documents.items():
            score = _cosine_similarity(tokens, self._index.get(doc_id, Counter()))
            scored.append(
                VectorDocument(
                    document_id=doc_id,
                    content=payload["content"],
                    metadata=payload.get("metadata", {}),
                    score=round(score, 3),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:k]


__all__ = ["SimpleVectorStore", "VectorDocument"]
