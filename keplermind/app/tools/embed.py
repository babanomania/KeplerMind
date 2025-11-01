"""Lightweight deterministic embedding utilities for tests."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


def _hash_to_unit_vector(payload: str, *, dimensions: int = 12) -> list[float]:
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    floats = [int.from_bytes(digest[i : i + 4], "big", signed=False) for i in range(0, 48, 4)]
    floats = floats[:dimensions]
    vector = [value / 2**32 for value in floats]
    norm = math.sqrt(sum(component**2 for component in vector)) or 1.0
    return [round(component / norm, 6) for component in vector]


@dataclass
class DeterministicEmbedder:
    """Minimal embedder producing reproducible vectors."""

    dimensions: int = 12

    def embed(self, text: str) -> list[float]:
        return _hash_to_unit_vector(text, dimensions=self.dimensions)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [_hash_to_unit_vector(text, dimensions=self.dimensions) for text in texts]


__all__ = ["DeterministicEmbedder"]

