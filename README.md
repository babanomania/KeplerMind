# KeplerMind

KeplerMind is an agentic learning and reasoning system organized as a sequence of specialized
agents. This repository currently provides a lightweight Python implementation that mirrors the
architecture described in `AGENTS.md`.

## Getting Started

1. Install dependencies with [Poetry](https://python-poetry.org/):
   ```bash
   poetry install
   ```
2. Populate the `.env` file with your OpenAI API key before integrating live retrieval.
3. Execute the default agent pipeline from the command line:
   ```bash
   poetry run keplermind --topic "Neural Networks" --goal "Summarize current challenges"
   ```
   Use `--as-json` to inspect the full session state or omit optional flags to rely on the
   built-in defaults provided by the Intake agent.

## Next Steps

The current implementation focuses on scaffolding. Replace placeholder logic within each agent
module with integrations to real tools (search, vector stores, evaluation models) to achieve the
full KeplerMind experience.
