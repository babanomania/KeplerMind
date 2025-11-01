"""Core configuration values for the KeplerMind CLI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    """Language model identifiers used across the system."""

    llm: str = "gpt-4o"
    embedding: str = "text-embedding-3-large"
    critic: str = "gpt-4o-mini"


@dataclass(frozen=True)
class RagConfig:
    """Defaults for RAG chunking and retrieval."""

    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 5


@dataclass(frozen=True)
class PlanningConfig:
    """Time budget and question planning defaults."""

    default_time_budget: int = 300
    min_questions: int = 5
    max_questions: int = 5


@dataclass(frozen=True)
class Settings:
    """Aggregate configuration facade."""

    models: ModelConfig = ModelConfig()
    rag: RagConfig = RagConfig()
    planning: PlanningConfig = PlanningConfig()


settings = Settings()
"""Module-level settings instance for convenience imports."""
