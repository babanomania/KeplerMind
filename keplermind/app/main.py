"""CLI entrypoint placeholder for KeplerMind."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KeplerMind CLI (work in progress)")
    parser.add_argument("--topic", type=str, help="Learning topic to explore.")
    parser.add_argument("--goal", type=str, help="Desired learning goal.")
    parser.add_argument("--level-hint", type=str, help="User's self-assessed skill level.")
    parser.add_argument("--time", type=int, default=300, help="Time budget in seconds.")
    parser.add_argument("--style", type=str, help="Preferred explanation style.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    print("KeplerMind CLI bootstrap underway.")
    print("Received arguments:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print("Full workflow implementation will arrive in upcoming phases.")


if __name__ == "__main__":
    main()
