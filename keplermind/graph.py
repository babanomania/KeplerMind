"""Simple orchestration graph for the KeplerMind agents."""

from __future__ import annotations

from typing import Iterable, List

from .agents.ask_and_score import QuestioningAgent
from .agents.build_rag import RAGBuilderAgent
from .agents.critic import CriticAgent
from .agents.explain import ExplanationAgent
from .agents.intake import IntakeAgent
from .agents.memorize import MemoryControllerAgent
from .agents.planner import PlannerAgent
from .agents.profile import ProfileAgent
from .agents.reflect_and_repair import ReflectionAgent
from .agents.report import ReporterAgent
from .agents.research import ResearchAgent
from .agents.schedule import SchedulerAgent
from .state import SessionState

AgentSequence = List


class KeplerMindGraph:
    """Executes the configured agent pipeline sequentially."""

    def __init__(self, agents: Iterable) -> None:
        self.agents = list(agents)

    def run(self, state: SessionState | None = None) -> SessionState:
        current = state or SessionState()
        for agent in self.agents:
            current = agent(current)
        return current


def build_default_graph() -> KeplerMindGraph:
    """Construct the default KeplerMind agent pipeline."""

    agents = [
        IntakeAgent(),
        ResearchAgent(),
        RAGBuilderAgent(),
        PlannerAgent(),
        QuestioningAgent(),
        CriticAgent(),
        ReflectionAgent(),
        ProfileAgent(),
        ExplanationAgent(),
        MemoryControllerAgent(),
        SchedulerAgent(),
        ReporterAgent(),
    ]
    return KeplerMindGraph(agents)
