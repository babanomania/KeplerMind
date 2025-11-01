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
from .config import load_config
from .state import SessionState
from .tools import EvaluationService, LocalSearchService, SimpleVectorStore

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

    config = load_config()
    search_service = LocalSearchService(
        dataset_path=config.search_data_path,
        default_limit=config.default_search_results,
    )
    vector_store = SimpleVectorStore(config.vector_store_path)
    evaluation_service = EvaluationService(threshold=config.evaluation_threshold)

    agents = [
        IntakeAgent(),
        ResearchAgent(search_service=search_service),
        RAGBuilderAgent(vector_store=vector_store),
        PlannerAgent(),
        QuestioningAgent(vector_store=vector_store),
        CriticAgent(evaluation_service=evaluation_service, vector_store=vector_store),
        ReflectionAgent(),
        ProfileAgent(),
        ExplanationAgent(vector_store=vector_store),
        MemoryControllerAgent(),
        SchedulerAgent(),
        ReporterAgent(),
    ]
    return KeplerMindGraph(agents)
