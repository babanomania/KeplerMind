"""Implementation of the Intake Agent."""

from __future__ import annotations

from typing import Any, Dict

from .base import LoggingAgent
from ..state import SessionState


class IntakeAgent(LoggingAgent):
    """Bootstrap the session state from a raw request payload."""

    def __init__(self) -> None:
        super().__init__(name="intake")

    def prepare(self, state: SessionState) -> SessionState:
        self._append_log(state, "Preparing intake state")
        return state

    def run(self, state: SessionState) -> SessionState:
        self._append_log(state, "Validating initial request")
        if not state.topic:
            state.topic = "Exploratory Learning"
            self._append_log(state, "Defaulted missing topic to 'Exploratory Learning'")
        if not state.goal:
            state.goal = "Establish baseline understanding"
            self._append_log(state, "Defaulted missing goal")
        if not state.level_hint:
            state.level_hint = "intermediate"
            self._append_log(state, "Assumed intermediate level")
        return state

    def finalize(self, state: SessionState) -> SessionState:
        self._append_log(state, "Intake complete")
        return state
