"""Base abstractions shared by KeplerMind agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..state import SessionState, StateDict


class Agent(ABC):
    """Abstract base class for all KeplerMind agents."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{self.__class__.__name__}(name={self.name!r})"

    def prepare(self, state: SessionState) -> SessionState:
        """Hook for pre-processing before the agent runs."""

        return state

    @abstractmethod
    def run(self, state: SessionState) -> SessionState:
        """Perform the agent's core work and mutate the state."""

    def finalize(self, state: SessionState) -> SessionState:
        """Hook for post-processing after the agent runs."""

        return state

    def __call__(self, state: SessionState) -> SessionState:
        """Execute the agent with pre- and post-processing hooks."""

        prepared = self.prepare(state)
        result = self.run(prepared)
        return self.finalize(result)


class LoggingAgent(Agent):
    """Agent mixin that records simple trace statements in the state."""

    log_key: str = "trace"

    def _append_log(self, state: SessionState, message: str) -> None:
        trace: Dict[str, Any] = getattr(state, self.log_key, None) or {}
        entries = trace.setdefault(self.name, [])
        entries.append(message)
        setattr(state, self.log_key, trace)

    def run(self, state: SessionState) -> SessionState:  # pragma: no cover - documented behavior
        raise NotImplementedError("LoggingAgent subclasses must implement run().")
