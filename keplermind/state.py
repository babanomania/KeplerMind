"""Shared state definitions for KeplerMind agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SessionState:
    """Represents the evolving state shared across KeplerMind agents."""

    topic: Optional[str] = None
    goal: Optional[str] = None
    level_hint: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    plan: List[Dict[str, Any]] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)
    assessments: List[Dict[str, Any]] = field(default_factory=list)
    profile: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    memories: List[Dict[str, Any]] = field(default_factory=list)
    schedule: Dict[str, Any] = field(default_factory=dict)
    report: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return the state as a mutable dictionary."""

        return {
            "topic": self.topic,
            "goal": self.goal,
            "level_hint": self.level_hint,
            "preferences": dict(self.preferences),
            "sources": list(self.sources),
            "notes": list(self.notes),
            "plan": list(self.plan),
            "questions": list(self.questions),
            "assessments": list(self.assessments),
            "profile": dict(self.profile),
            "explanation": self.explanation,
            "memories": list(self.memories),
            "schedule": dict(self.schedule),
            "report": self.report,
        }


StateDict = Dict[str, Any]
