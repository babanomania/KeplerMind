"""LLM integrations used across KeplerMind agents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from textwrap import dedent
from typing import Iterable, List, Mapping, Sequence

try:  # pragma: no cover - optional dependency import
    from openai import OpenAI, OpenAIError
except ImportError:  # pragma: no cover - handled gracefully at runtime
    OpenAI = None  # type: ignore[assignment]
    OpenAIError = Exception  # type: ignore[assignment]

from .vectorstore import VectorDocument


class LLMServiceError(RuntimeError):
    """Raised when an LLM-backed request cannot be satisfied."""


def _strip_code_fence(payload: str) -> str:
    """Remove optional Markdown code fences from an LLM response."""

    text = payload.strip()
    if text.startswith("```"):
        parts = text.split("```", 2)
        if len(parts) >= 2:
            return parts[1].strip()
    return text


def _parse_plan(raw: str) -> List[dict]:
    cleaned = _strip_code_fence(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise LLMServiceError("Plan response was not valid JSON") from exc

    if not isinstance(data, list):
        raise LLMServiceError("Plan response must be a JSON array of steps")

    normalized: list[dict] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, Mapping):
            raise LLMServiceError("Each plan entry must be a JSON object")
        step_no = int(item.get("step", index))
        action = str(item.get("action", ""))
        duration = int(item.get("duration_minutes", 30))
        normalized.append({"step": step_no, "action": action, "duration_minutes": duration})

    return normalized


def _format_documents(documents: Sequence[VectorDocument]) -> str:
    formatted = []
    for doc in documents:
        title = doc.metadata.get("title") or "Untitled Source"
        reference = f"- {title} (score {doc.score}): {doc.content.strip()}"
        formatted.append(reference)
    return "\n".join(formatted)


@dataclass
class OpenAIChatService:
    """Thin wrapper around OpenAI's chat completion API."""

    api_key: str
    model: str = "gpt-4o-mini"
    base_url: str | None = None
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if OpenAI is None:
            raise LLMServiceError(
                "OpenAI package is not installed; run 'poetry install' to enable LLM features"
            )

        if not self.api_key:
            raise LLMServiceError("OpenAIChatService requires an API key")

        client_args = {"api_key": self.api_key, "timeout": self.timeout}
        if self.base_url:
            client_args["base_url"] = self.base_url
        self._client = OpenAI(**client_args)

    def _complete(self, messages: Iterable[Mapping[str, str]], temperature: float = 0.2) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=list(messages),
                temperature=temperature,
            )
        except OpenAIError as exc:  # pragma: no cover - network failure
            raise LLMServiceError(f"OpenAI request failed: {exc}") from exc

        if not response.choices:
            raise LLMServiceError("OpenAI response did not contain any choices")

        message = response.choices[0].message
        content = getattr(message, "content", None)
        if isinstance(content, list):
            content = "".join(part.text for part in content if getattr(part, "text", None))

        if not content:
            raise LLMServiceError("OpenAI response did not contain any content")

        return str(content).strip()

    def generate_plan(
        self,
        *,
        topic: str,
        goal: str | None,
        level_hint: str | None,
        max_steps: int = 5,
    ) -> List[dict]:
        user_prompt = dedent(
            f"""
            Create a focused learning plan as a JSON array.
            Each array item must be an object with keys step, action, and duration_minutes.
            Use no more than {max_steps} steps.
            Topic: {topic}
            Goal: {goal or "General understanding"}
            Learner level: {level_hint or "unspecified"}
            """
        ).strip()

        messages = [
            {
                "role": "system",
                "content": "You are an expert learning designer. Respond with structured JSON only.",
            },
            {"role": "user", "content": user_prompt},
        ]

        completion = self._complete(messages)
        return _parse_plan(completion)

    def generate_explanation(
        self,
        *,
        topic: str,
        documents: Sequence[VectorDocument],
        profile: Mapping[str, object] | None = None,
    ) -> str:
        context = _format_documents(documents)
        profile_summary = json.dumps(profile or {}, ensure_ascii=False)

        user_prompt = dedent(
            f"""
            Produce a concise learner-facing explanation in GitHub-flavored Markdown.
            Use section headings and emphasise actionable insights.
            Topic: {topic}
            Learner profile: {profile_summary}
            Use the following supporting evidence:
            {context}
            """
        ).strip()

        messages = [
            {
                "role": "system",
                "content": "You are a reflective mentor who explains concepts clearly and cites evidence from the provided notes.",
            },
            {"role": "user", "content": user_prompt},
        ]

        return self._complete(messages, temperature=0.4)


__all__ = ["LLMServiceError", "OpenAIChatService"]
