"""Shared state definition for the KeplerMind execution graph."""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict


class ArtifactInfo(TypedDict, total=False):
    """Metadata about generated artifacts."""

    path: str
    description: NotRequired[str]
    kind: NotRequired[Literal["text", "json", "table", "log"]]


class QAResult(TypedDict, total=False):
    """Container for a question/answer pair evaluated by the system."""

    question: str
    answer: str
    score: NotRequired[float]
    rationale: NotRequired[str]


class ReflectionState(TypedDict, total=False):
    """Information about the latest reflection loop."""

    needs_repair: bool
    notes: NotRequired[str]


class SkillProfile(TypedDict, total=False):
    """Description of a single skill entry in the profile."""

    name: str
    gap: float
    level: str
    summary: NotRequired[str]


class ProfilePayload(TypedDict, total=False):
    """Aggregate profile information returned by the profiler node."""

    inferred_level: str
    skills: list[SkillProfile]


class S(TypedDict, total=False):
    """Canonical state dictionary exchanged between nodes."""

    session_id: str
    topic: str
    goal: str
    level_hint: str
    time_budget: int
    style: str
    priors: dict[str, Any]
    sources: list[dict[str, Any]]
    plan: list[dict[str, Any]]
    questions: list[str]
    qa: list[QAResult]
    profile: ProfilePayload
    explanations: dict[str, str]
    mem_candidates: list[dict[str, Any]]
    artifacts: dict[str, ArtifactInfo]
    reflection: ReflectionState
