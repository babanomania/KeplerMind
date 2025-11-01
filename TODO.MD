### Project: *KeplerMind — Discover · Reflect · Illuminate*

> **Goal:** Build a self-reflective CLI learning companion powered by MCP (Memory · Control · Planning).
> The user gives a topic → the agent performs research → builds a RAG → plans 5 adaptive questions → evaluates and reflects → explains → commits durable memories.

---

## 🌌 Phase 0 — Repository Setup

**Objective:** Bootstrap CLI environment and core layout.

* [x] Create folder structure:

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
* [x] Add `requirements.txt` with:

  ```
  langchain
  langgraph
  chromadb
  duckduckgo-search
  openai
  readability-lxml
  requests
  pandas
  numpy
  rich
  python-dotenv
  pydantic>=2
  pytest
  ```
* [x] Add `.env.example` with:

  ```
  OPENAI_API_KEY=
  TAVILY_API_KEY=
  ```
* [x] Add `.gitignore`:
  `.env`, `__pycache__`, `assets/outputs/*`, `*.sqlite`, `.DS_Store`
* [x] Create `Makefile` with targets:

  * `make run`
  * `make test`
  * `make clean`
* [x] Add placeholder `README.md` (will later describe CLI usage).
* [x] Create `config/settings.py` with model names, chunk sizes, and time budget constants.

---

## 🧠 Phase 1 — LangGraph Backbone

**Objective:** Implement the brain that orchestrates all nodes.

* [x] `app/state.py`:
  Define `TypedDict S` (topic, goal, priors, sources, plan, questions, qa, profile, explanations, mem_candidates, artifacts).

* [x] `app/graph.py`:

  * [x] Wire all nodes: `intake → research → build_rag → planner → ask_and_score → reflect_and_repair → profile → explain → memorize → schedule → report`.
  * [x] Implement conditional edges: reflection loops and repair checks.
  * [x] Print rich-style DAG summary in CLI at startup.

* [x] `app/main.py`:

  * [x] Implement a single CLI entrypoint using `argparse`.
  * [x] Options:

    ```
    --topic "Kafka Architecture"
    --goal "prepare for interview"
    --level-hint intermediate
    --time 300
    --style bullet
    ```
  * [x] Log progress with `rich.console` + timestamps.
  * [x] On completion: show summary table of scores and output paths.

---

## 🧩 Phase 2 — MCP Core System

**Objective:** Implement memory persistence and planning priors.

* [x] `mcp/stores.py`:

  * SQLite episodic log (`events(id, ts, session, phase, payload)`).
  * Chroma/FAISS semantic store.
  * JSON preference KV (`preferences.json`).

* [x] `mcp/policies.py`:

  * scoring/retention formulas.
  * summarization & redaction (truncate >240 chars).
  * top-N class retention logic.

* [x] `mcp/controller.py`:

  * `propose()`, `review()`, `commit()`, `retrieve()` with scoring weights.
  * Add audit to episodic log.

* [x] `mcp/priors.py`:

  * Beta priors for per-skill knowledge.
  * Thompson sampling for question planning.
  * spaced repetition schedule generator.

* [x] Test: `tests/test_mcp_policies.py`.

---

## 🔍 Phase 3 — Research & RAG Pipeline

**Objective:** Let KeplerMind explore, clean, and index the topic.

* [x] `tools/search.py`: Tavily → fallback to DuckDuckGo.

* [x] `tools/scrape.py`: HTML → readable text extraction.

* [x] `nodes/research.py`: orchestrate 8–15 sources, produce `notes[]` + `bibliography.json`.

* [x] `tools/chunk.py`: chunk text into ~900 tokens, 150 overlap.

* [x] `tools/embed.py`: embed and store into Chroma.

* [x] `nodes/build_rag.py`: embed chunks → mark `vector_ready=True`.

* [x] Prompt: `prompts/hallucination_guard.md`.

* [x] Test: `tests/test_rag_and_citations.py`.

---

## 🪐 Phase 4 — Planning and Question Design

**Objective:** Generate 10 candidate questions, pick top 5 with MCP priors.

* [x] `nodes/planner.py`:

  * Read priors, preferences, time budget.
  * Run Thompson sampling → assign difficulty levels.
  * Produce JSON plan with 5-question cap, ≥4 unique skills.
* [x] Prompts:

  * `prompts/planner.md`
  * `prompts/question_gen.md`
* [x] Test: `tests/test_planner_priors.py`.

---

## 💬 Phase 5 — Adaptive Q&A Loop

**Objective:** Ask, score, and reflect interactively in CLI.

* [x] `nodes/ask_and_score.py`:

  * Loop over 5 questions, prompt user for answer + self-confidence (1–5).
  * Grade via `scoring_critic.md`.
  * Update Beta priors + log result.

* [x] `nodes/reflect_and_repair.py`:

  * Trigger if evidence or score insufficient.
  * Offer minimal repair actions: re-ask, scaffold, lower difficulty.
  * Add `fix_recipe` memory candidate.

* [x] Prompts:

  * `prompts/scoring_critic.md`
  * `prompts/reflection_critic.md`

* [x] Test: `tests/test_reflection_loop.py`.

---

## 🧭 Phase 6 — Knowledge Profiling & Explanation

**Objective:** Derive knowledge profile and explain adaptively.

* [x] `nodes/profile.py`:

  * Aggregate skill gap scores, infer level.
  * Save `profile.json`.

* [x] `nodes/explain.py`:

  * For low-gap → **light** explanation.
  * For high-gap → **deep** explanation.
  * Add inline citations using `tools/citations.py`.

* [x] Prompts:

  * `prompts/explain_light.md`
  * `prompts/explain_deep.md`
  * `prompts/cite_merge.md`

* [x] Test: `tests/test_explain.py`.

---

## 🧠 Phase 7 — Memory Commit & Scheduling

**Objective:** Save durable memories and next review plan.

* [x] `nodes/memorize.py`:

  * Collect `preference`, `anchor_fact`, `fix_recipe`, `gap_signature`.
  * Call `MemoryController` to score and persist.

* [x] `nodes/schedule.py`:

  * Compute `next_review.json` using gap/stability ratio.

* [x] Test: `tests/test_mcp_commit.py`.

---

## 📜 Phase 8 — Reporting & CLI Output

**Objective:** Produce final learning report and summary.

* [x] `nodes/report.py`:

  * Create `report.md`, `profile.json`, `questions.jsonl`, and `bibliography.json`.
  * Append References list.
  * Print rich summary:

    ```
    Skill        Gap      Level
    Foundations  0.45     Intermediate
    Tools        0.22     Advanced
    Patterns     0.68     Beginner
    ```
  * Display output paths.

* [x] Test: `tests/test_report.py`.

---

## 💡 Phase 9 — CLI Polish

**Objective:** Make CLI smooth and enjoyable.

* [x] Add colored sections using `rich` (headers, progress bars, tables).
* [x] Add “orbit” icon or ASCII logo:

  ```
   ☉  KeplerMind — Discover · Reflect · Illuminate
  ```
* [x] Graceful fallbacks:

  * If Tavily key missing → DuckDuckGo.
  * If OpenAI key missing → fallback to local embed model (warn).
* [x] `--quiet` and `--debug` flags.
* [x] Store all outputs in `assets/outputs/<timestamp>/`.

---

## 🧪 Testing Plan

| File                        | What It Verifies                    |
| --------------------------- | ----------------------------------- |
| `test_mcp_policies.py`      | memory scoring + top-N pruning      |
| `test_rag_and_citations.py` | RAG integrity + citations           |
| `test_planner_priors.py`    | 5-question diversity + priors       |
| `test_reflection_loop.py`   | reflection loop & repair            |
| `test_explain.py`           | adaptive explanations with sources  |
| `test_mcp_commit.py`        | memory commit lifecycle             |
| `test_report.py`            | report completeness & summary table |

Run via:

```bash
pytest -q
```

---

## 🚀 Optional Enhancements

* [ ] **Offline Mode:** cache embeddings + reuse RAG.
* [ ] **Session Resume:** load last profile and continue.
* [ ] **Pretty Graph Print:** ASCII DAG from LangGraph.
* [ ] **Memory Dashboard:** `keplermind memory view` command (prints summary table).

---

## ✨ Completion Criteria

✅ When `python app/main.py --topic "X"` runs end-to-end:

* Web search → RAG build
* MCP planning → 5 Q&A
* Reflection + repair loop
* Profile + explanations generated
* Memory updated
* Final CLI report shown with paths to artifacts
