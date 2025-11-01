"""CLI entrypoint for the KeplerMind prototype."""

from __future__ import annotations

import argparse
import os
from typing import Any

from rich.console import Console
from rich.table import Table

from .graph import build_graph
from .state import S

LOGO = " ☉  KeplerMind — Discover · Reflect · Illuminate"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KeplerMind CLI (prototype)")
    parser.add_argument("--topic", type=str, default="", help="Learning topic to explore.")
    parser.add_argument("--goal", type=str, default="", help="Desired learning goal.")
    parser.add_argument("--level-hint", type=str, default="", help="User's self-assessed skill level.")
    parser.add_argument("--time", type=int, default=300, help="Time budget in seconds.")
    parser.add_argument("--style", type=str, default="", help="Preferred explanation style.")
    parser.add_argument("--max-repairs", type=int, default=1, help="Maximum allowed reflection repairs.")
    parser.add_argument("--quiet", action="store_true", help="Suppress most console output.")
    parser.add_argument("--debug", action="store_true", help="Enable verbose logging.")
    return parser


def _print_logo(console: Console) -> None:
    console.print(f"[bold blue]{LOGO}[/bold blue]")


def _detect_backends(console: Console) -> dict[str, str]:
    """Identify which external services are available and warn if falling back."""

    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    search_backend = "tavily" if tavily_key else "duckduckgo"
    embedding_backend = "openai" if openai_key else "local"

    if not tavily_key:
        console.log("Tavily API key missing; using DuckDuckGo search fallback.")
    if not openai_key:
        console.log("OpenAI API key missing; using local embedding fallback.")

    return {"search_backend": search_backend, "embedding_backend": embedding_backend}


def _summary_table(state: S) -> Table:
    table = Table(title="Skill Summary", show_header=True, header_style="bold magenta")
    table.add_column("Skill", overflow="fold")
    table.add_column("Gap", justify="right")
    table.add_column("Level")

    profile = state.get("profile", {})
    for skill in profile.get("skills", []):
        table.add_row(
            skill.get("name", "Skill"),
            f"{skill.get('gap', 0.0):.2f}",
            skill.get("level", "unknown"),
        )

    if not profile.get("skills"):
        table.add_row("(no skills)", "-", "-")

    return table


def _print_artifacts(console: Console, artifacts: dict[str, Any]) -> None:
    if not artifacts:
        console.print("[yellow]No artifacts registered.[/yellow]")
        return

    table = Table(title="Artifacts", show_header=True, header_style="bold green")
    table.add_column("Name")
    table.add_column("Path", overflow="fold")
    table.add_column("Description")

    for name, info in artifacts.items():
        table.add_row(name, info.get("path", "n/a"), info.get("description", ""))

    console.print(table)


def main(argv: list[str] | None = None) -> S:
    parser = build_parser()
    args = parser.parse_args(argv)

    console = Console(quiet=args.quiet)
    if args.debug and not args.quiet:
        console.log("Debug mode enabled.")

    if not args.quiet:
        _print_logo(console)

    backends = _detect_backends(console)
    graph = build_graph(console=console, max_repairs=max(args.max_repairs, 0))
    if not args.quiet:
        graph.print_dag_summary()

    initial_state: S = {
        "topic": args.topic,
        "goal": args.goal,
        "level_hint": args.level_hint,
        "time_budget": args.time,
        "style": args.style,
    }
    initial_state.update(backends)

    final_state = graph.run(initial_state)

    if not args.quiet:
        console.print(_summary_table(final_state))
        _print_artifacts(console, final_state.get("artifacts", {}))

    return final_state


if __name__ == "__main__":  # pragma: no cover - CLI execution guard
    main()
