# KeplerMind

*KeplerMind — Discover · Reflect · Illuminate*

This repository will host the KeplerMind CLI learning companion. Detailed usage instructions and architectural notes will be added as the system evolves.

## Getting Started

1. Create a Python virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and populate required API keys.
3. Run `make run ARGS="--help"` to explore the CLI once the main entrypoint is implemented.

## Project Structure

```
keplermind/
  app/
    nodes/
    mcp/
    tools/
    prompts/
    config/
    memory/
  assets/outputs/
  tests/
```

Additional documentation, prompts, and implementation details will be provided in future phases.
