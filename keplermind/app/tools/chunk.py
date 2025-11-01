"""Utilities for chunking long documents into overlapping windows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Chunk:
    """Representation of a text window from a larger document."""

    id: str
    text: str
    start: int
    end: int


def chunk_text(
    text: str,
    *,
    chunk_size: int,
    overlap: int,
    prefix: str,
) -> list[Chunk]:
    """Split *text* into overlapping chunks using whitespace boundaries."""

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    words = text.split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[Chunk] = []

    index = 0
    counter = 0
    while index < len(words):
        window = words[index : index + chunk_size]
        chunk_text = " ".join(window)
        start = index
        end = min(len(words), index + chunk_size)
        chunk_id = f"{prefix}_{counter}"
        chunks.append(Chunk(id=chunk_id, text=chunk_text, start=start, end=end))
        counter += 1
        index += step

    return chunks


def flatten_texts(texts: Iterable[str]) -> str:
    """Join multiple pieces of text into a single body for chunking."""

    return "\n\n".join(part.strip() for part in texts if part.strip())


__all__ = ["Chunk", "chunk_text", "flatten_texts"]

