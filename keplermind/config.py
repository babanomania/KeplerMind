"""Configuration handling for the KeplerMind system."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Mapping, Optional


class ConfigError(RuntimeError):
    """Raised when configuration values are invalid."""


@dataclass(frozen=True)
class AppConfig:
    """Container for application level configuration."""

    search_provider: str
    search_data_path: Path
    vector_store_path: Path
    default_search_results: int
    evaluation_threshold: float
    tavily_api_key: Optional[str] = None
    search_api_url: Optional[str] = None

    def validate(self) -> None:
        """Validate that configuration values are well formed."""

        errors: list[str] = []

        if self.default_search_results <= 0:
            errors.append("default_search_results must be greater than zero")

        if not self.search_data_path.is_file():
            errors.append(f"search data file not found: {self.search_data_path}")

        if self.search_provider not in {"local", "tavily"}:
            errors.append(
                "search_provider must be either 'local' or 'tavily'"
            )

        if self.search_provider == "tavily" and not self.tavily_api_key:
            errors.append("Tavily search provider requires TAVILY_API_KEY to be set")

        if not 0 < self.evaluation_threshold <= 1:
            errors.append("evaluation_threshold must be between 0 and 1")

        if errors:
            message = "; ".join(errors)
            raise ConfigError(message)


def load_config(env: Mapping[str, str] | None = None) -> AppConfig:
    """Load configuration from environment variables with validation."""

    environment = env or os.environ
    base_dir = Path(__file__).resolve().parent

    default_data_path = base_dir / "data" / "knowledge_base.json"
    default_vector_path = base_dir / "data" / "vector_store.json"

    search_provider = environment.get("KEPLERMIND_SEARCH_PROVIDER", "local").lower()
    search_data_path = Path(
        environment.get("KEPLERMIND_SEARCH_DATA_PATH", str(default_data_path))
    )
    vector_store_path = Path(
        environment.get("KEPLERMIND_VECTOR_STORE_PATH", str(default_vector_path))
    )

    default_results_raw = environment.get("KEPLERMIND_SEARCH_RESULT_COUNT", "5")
    evaluation_threshold_raw = environment.get("KEPLERMIND_EVALUATION_THRESHOLD", "0.65")

    try:
        default_results = int(default_results_raw)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigError(
            "KEPLERMIND_SEARCH_RESULT_COUNT must be an integer"
        ) from exc

    try:
        evaluation_threshold = float(evaluation_threshold_raw)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ConfigError(
            "KEPLERMIND_EVALUATION_THRESHOLD must be a float"
        ) from exc

    tavily_api_key = environment.get("TAVILY_API_KEY")
    search_api_url = environment.get("KEPLERMIND_SEARCH_URL")

    vector_store_path.parent.mkdir(parents=True, exist_ok=True)

    if not vector_store_path.exists():
        # Pre-create an empty vector store file so downstream tooling can rely on it.
        vector_store_path.write_text(json.dumps({"next_id": 1, "documents": []}, indent=2))

    config = AppConfig(
        search_provider=search_provider,
        search_data_path=search_data_path,
        vector_store_path=vector_store_path,
        default_search_results=default_results,
        evaluation_threshold=evaluation_threshold,
        tavily_api_key=tavily_api_key,
        search_api_url=search_api_url,
    )

    config.validate()
    return config


__all__ = ["AppConfig", "ConfigError", "load_config"]
