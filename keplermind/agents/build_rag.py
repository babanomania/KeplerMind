"""Implementation of the RAG Builder Agent."""

from __future__ import annotations

from typing import List

from .base import LoggingAgent
from ..state import SessionState
from ..tools import SimpleVectorStore


class RAGBuilderAgent(LoggingAgent):
    """Chunk research notes and index them in the vector store."""

    def __init__(self, vector_store: SimpleVectorStore) -> None:
        super().__init__(name="rag_builder")
        self.vector_store = vector_store

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Embedding research notes into vector store")
        documents: List[str] = []
        metadata: List[dict] = []

        for source in state.sources:
            content = source.get("content") or source.get("summary", "")
            if not content:
                continue
            documents.append(content)
            metadata.append(
                {
                    "title": source.get("title"),
                    "url": source.get("url"),
                    "topic": state.topic,
                    "score": source.get("score"),
                }
            )

        if not documents:
            self._append_log(state, "No research documents available for embedding")
            return state

        doc_ids = self.vector_store.add_documents(documents, metadata)
        existing_ids = {memory.get("chunk_id") for memory in state.memories}

        for doc_id, doc_content, doc_meta in zip(doc_ids, documents, metadata):
            if doc_id in existing_ids:
                continue
            state.memories.append(
                {
                    "chunk_id": doc_id,
                    "content": doc_content,
                    "metadata": doc_meta,
                }
            )

        self._append_log(state, f"Indexed {len(doc_ids)} document chunks")
        return state
