"""Sequential orchestration of the KeplerMind nodes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Dict

from rich.console import Console
from rich.table import Table

from . import nodes
from .state import S

NodeCallable = Callable[[S], S]


class KeplerMindGraph:
    """A lightweight façade mimicking the future LangGraph orchestration."""

    def __init__(self, *, console: Console | None = None, max_repairs: int = 1) -> None:
        self.console = console or Console()
        self.max_repairs = max_repairs
        self.node_order = [
            "intake",
            "research",
            "build_rag",
            "planner",
            "ask_and_score",
            "reflect_and_repair",
            "profile",
            "explain",
            "memorize",
            "report",
        ]
        self.descriptions: Dict[str, str] = {
            "intake": "Normalize inputs and session identifiers.",
            "research": "Gather sources and initial notes.",
            "build_rag": "Store observations into a placeholder RAG artifact.",
            "planner": "Produce a five-step learning trajectory.",
            "ask_and_score": "Generate diagnostic questions and mock scores.",
            "reflect_and_repair": "Evaluate QA results and request repairs if needed.",
            "profile": "Infer skill levels from QA performance.",
            "explain": "Draft adaptive explanations per skill.",
            "memorize": "Aggregate memory candidates for persistence.",
            "report": "Write a Markdown report and register artifacts.",
        }

        self.registry: Dict[str, NodeCallable] = {
            "intake": lambda state: nodes.intake.run(state, console=self.console),
            "research": lambda state: nodes.research.run(state, console=self.console),
            "build_rag": lambda state: nodes.build_rag.run(state, console=self.console),
            "planner": lambda state: nodes.planner.run(state, console=self.console),
            "ask_and_score": lambda state: nodes.ask_and_score.run(state, console=self.console),
            "reflect_and_repair": lambda state: nodes.reflect_and_repair.run(state, console=self.console),
            "profile": lambda state: nodes.profile.run(state, console=self.console),
            "explain": lambda state: nodes.explain.run(state, console=self.console),
            "memorize": lambda state: nodes.memorize.run(state, console=self.console),
            "report": lambda state: nodes.report.run(state, console=self.console),
        }

    # ------------------------------------------------------------------
    # Presentation helpers
    # ------------------------------------------------------------------
    def print_dag_summary(self) -> None:
        """Render a simple DAG summary using Rich."""

        table = Table(title="KeplerMind Pipeline", show_header=True, header_style="bold magenta")
        table.add_column("Order", justify="right")
        table.add_column("Node")
        table.add_column("Description")

        for index, name in enumerate(self.node_order, start=1):
            table.add_row(str(index), name.replace("_", " ").title(), self.descriptions.get(name, ""))

        self.console.print(table)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    def _invoke(self, name: str, state: S) -> S:
        if name not in self.registry:
            raise KeyError(f"Unknown node '{name}'")
        self.console.rule(f"[bold cyan]{name.replace('_', ' ').title()}")
        return self.registry[name](state)

    def run(self, initial_state: S | None = None) -> S:
        """Execute the node sequence with a reflection loop."""

        state: S = dict(initial_state or {})

        for name in self.node_order:
            if name == "ask_and_score":
                state = self._invoke(name, state)

                repair_attempts = 0
                while True:
                    state = self._invoke("reflect_and_repair", state)
                    reflection = state.get("reflection", {})
                    if not reflection.get("needs_repair"):
                        break
                    if repair_attempts >= self.max_repairs:
                        self.console.log(
                            "Maximum repair attempts reached; continuing despite pending issues."
                        )
                        break
                    repair_attempts += 1
                    self.console.log(
                        "Reflection requested repair attempt %d — rerunning question node.",
                        repair_attempts,
                    )
                    state = self._invoke("ask_and_score", state)

                continue

            if name == "reflect_and_repair":
                # Already handled in the loop above.
                continue

            state = self._invoke(name, state)

        return state


def build_graph(*, console: Console | None = None, max_repairs: int = 1) -> KeplerMindGraph:
    """Factory helper used by the CLI entrypoint."""

    return KeplerMindGraph(console=console, max_repairs=max_repairs)
